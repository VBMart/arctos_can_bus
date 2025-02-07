from time import sleep

import can
from can.interfaces import serial

from motors import XMotor, YMotor, ZMotor, AMotor, BMotor, CMotor



class Arctos:
    def __init__(self, bus: can.interface.Bus) -> None:
        """
        Initialize the Arctos class with a CAN bus interface and motor instances.
        
        :param bus: CAN bus interface for motor communication.
        """
        self._bus = bus
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
        self._listener_active = False
        self._listener_thread = None
        self.start_can_listener()

    def start_can_listener(self):
        import threading
        self._listener_active = True  # Ensure flag is set
        self._listener_thread = threading.Thread(target=self._listener, daemon=True)
        self._listener_thread.start()

    def _listener(self):
        while self._listener_active:
            try:
                message = self._bus.recv(timeout=0.1)
                if message:
                    self.on_new_can_message(message)
                sleep(0.5)
            except (OSError, serial.serialutil.SerialException) as e:
                # Likely the bus/serial port is closed.
                break

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
        print(
            f"\tReceived: arbitration_id=0x{message.arbitration_id:X}, data=[{received_data_bytes}], is_extended_id=False"
        )

    def get_motor(self, motor_id: str):
        """
        Get the motor instance by its identifier.

        :param motor_id: The identifier of the motor ('x', 'y', 'z', 'a', 'b', 'c').
        :return: The motor instance if found, otherwise None.
        """
        assert motor_id in self._motor_classes, f"Motor with id '{motor_id}' not found."
        return self._motors.get(motor_id)

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
            motor.go_home(timeout=0)

    def x_motor(self):
        """Get the X motor instance."""
        return self.get_motor('x')

    def y_motor(self):
        """Get the Y motor instance."""
        return self.get_motor('y')

    def z_motor(self):
        """Get the Z motor instance."""
        return self.get_motor('z')

    def a_motor(self):
        """Get the A motor instance."""
        return self.get_motor('a')

    def b_motor(self):
        """Get the B motor instance."""
        return self.get_motor('b')

    def c_motor(self):
        """Get the C motor instance."""
        return self.get_motor('c')
