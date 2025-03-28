from time import sleep

import can
from can.interfaces import serial

from base_motor import MotorStatus
from gripper_device import GripperDevice
from led_device import LedDevice, Color
from motors import XMotor, YMotor, ZMotor, AMotor, BMotor, CMotor


motor_statuses_to_color_mapping = {
    MotorStatus.UNKNOWN: Color.VIOLET,
    MotorStatus.OK: Color.GREEN,
    MotorStatus.MOVING: Color.YELLOW,
    MotorStatus.ERROR: Color.RED,
    MotorStatus.HOMING: Color.CYAN,
}


class Arctos:
    def __init__(self, bus: can.interface.Bus) -> None:
        """
        Initialize the Arctos class with a CAN bus interface and motor instances.
        
        :param bus: CAN bus interface for motor communication.
        """
        self._bus = bus

        # Initialize motor instances
        self._motor_classes = {
            'x': XMotor,
            'y': YMotor,
            'z': ZMotor,
            'a': AMotor,
            'b': BMotor,
            'c': CMotor
        }
        self._motors = {key: cls(bus) for key, cls in self._motor_classes.items()}
        for motor in self._motors.values():
            motor.can_wait_for_response = False

        self.led = LedDevice(bus)
        self.gripper = GripperDevice(bus)

        # Start the CAN listener
        self._listener_active = False
        self._listener_thread = None
        self.start_can_listener()
        self.motor_statuses_to_led()

    def __str__(self):
        return f"Arctos \n\t Motors: \n\t\t {'\n\t\t '.join([str(motor) for motor in self._motors.values()])}"

    def start_can_listener(self):
        import threading
        self._listener_active = True  # Ensure flag is set
        self._listener_thread = threading.Thread(target=self._listener, daemon=True)
        self._listener_thread.start()

    def _listener(self):
        while self._listener_active:
            try:
                message = self._bus.recv(timeout=0.1)
                try:
                    if message:
                        self.on_new_can_message(message)
                except Exception as e:
                    print(f"Error (on_new_can_message): {e}")
                sleep(0.3)
            except (OSError, serial.serialutil.SerialException) as e:
                print(f"Error: {e}")
                # Likely the bus/serial port is closed.
                break
        print("Listener stopped")

    def stop_can_listener(self):
        self._listener_active = False
        if hasattr(self, '_listener_thread'):
            self._listener_thread.join(timeout=2)
        # Now it is safe to close the bus/serial port
        self._bus.shutdown()  # or self._bus.close() depending on your API

    def __del__(self):
        """
        Destructor to clean up resources when the object is destroyed.
        """
        self.stop_can_listener()

    def motor_statuses_to_led(self):
        is_led_changed = False
        for motor in self.get_active_motors():
            color = motor_statuses_to_color_mapping.get(motor.status, Color.BLACK)
            changed = self.led.set_motor_color(motor.can_id, color)
            is_led_changed = is_led_changed or changed

        if is_led_changed:
            self.led.show()


    def on_new_can_message(self, message: can.Message):
        """
        Handle a new CAN message.
        
        :param message: The received CAN message.
        """
        # Example: Call a method based on message content
        # This is a placeholder and should be replaced with actual logic
        received_data_bytes = ", ".join(
            [f"0x{byte:02X}" for byte in message.data]
        )
        sender_id = message.arbitration_id
        print(
            f"\tReceived: arbitration_id=0x{sender_id:X}, data=[{received_data_bytes}], is_extended_id=False"
        )
        motor = self.get_motor_by_id(sender_id)
        if motor:
            motor.on_can_message(message)
            self.motor_statuses_to_led()

    def get_motor_by_axis(self, axis_name: str):
        """
        Get the motor instance by its identifier.

        :param axis_name: The identifier of the motor ('x', 'y', 'z', 'a', 'b', 'c').
        :return: The motor instance if found, otherwise None.
        """
        assert axis_name in self._motor_classes, f"Motor with id '{axis_name}' not found."
        return self._motors.get(axis_name)

    def get_motor_by_id(self, motor_id: int):
        """
        Get the motor instance by its CAN id.

        :param motor_id: The CAN id of the motor.
        :return: The motor instance if found, otherwise None.
        """
        for motor in self._motors.values():
            if motor.can_id == motor_id:
                return motor
        return None

    def get_active_motors(self):
        """
        Get the active motors.

        :return: A list of active motors.
        """
        return [motor for motor in self._motors.values() if motor.is_active]

    def go_home(self):
        """
        Send the go home command to all motors.
        """
        for motor in self.get_active_motors():
            if motor not in [self.b_motor(), self.c_motor()]:
                motor.go_home()

    def x_motor(self):
        """Get the X motor instance."""
        return self.get_motor_by_axis('x')

    def y_motor(self):
        """Get the Y motor instance."""
        return self.get_motor_by_axis('y')

    def z_motor(self):
        """Get the Z motor instance."""
        return self.get_motor_by_axis('z')

    def a_motor(self):
        """Get the A motor instance."""
        return self.get_motor_by_axis('a')

    def b_motor(self):
        """Get the B motor instance."""
        return self.get_motor_by_axis('b')

    def c_motor(self):
        """Get the C motor instance."""
        return self.get_motor_by_axis('c')
