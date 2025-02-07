import can
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
            motor.go_home()

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
