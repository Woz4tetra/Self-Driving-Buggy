
from .dof_sensor import DOFsensor

class Gyroscope(DOFsensor):
    L3GD20_ADDRESS = 0
    def __init__(self, bus):
        super().__init__(bus, self.L3GD20_ADDRESS)

        self.v_x, self.v_y, self.v_z = 0, 0, 0
