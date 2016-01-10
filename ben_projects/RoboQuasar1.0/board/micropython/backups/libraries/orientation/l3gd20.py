from .dof_sensor import DOFsensor


class Gyroscope(DOFsensor):
    GYRO_REGISTER = dict(  # DEFAULT    TYPE
            WHO_AM_I=0x0F,  # 11010100   r
            CTRL_REG1=0x20,  # 00000111   rw
            CTRL_REG2=0x21,  # 00000000   rw
            CTRL_REG3=0x22,  # 00000000   rw
            CTRL_REG4=0x23,  # 00000000   rw
            CTRL_REG5=0x24,  # 00000000   rw
            REFERENCE=0x25,  # 00000000   rw
            OUT_TEMP=0x26,  # _________   r
            STATUS_REG=0x27,  # _________ r
            OUT_X_L=0x28,  # _________ r
            OUT_X_H=0x29,  # _________ r
            OUT_Y_L=0x2A,  # _________ r
            OUT_Y_H=0x2B,  # _________ r
            OUT_Z_L=0x2C,  # _________ r
            OUT_Z_H=0x2D,  # _________ r
            FIFO_CTRL_REG=0x2E,  # 00000000   rw
            FIFO_SRC_REG=0x2F,  # _________ r
            INT1_CFG=0x30,  # 00000000   rw
            INT1_SRC=0x31,  # _________ r
            TSH_XH=0x32,  # 00000000   rw
            TSH_XL=0x33,  # 00000000   rw
            TSH_YH=0x34,  # 00000000   rw
            TSH_YL=0x35,  # 00000000   rw
            TSH_ZH=0x36,  # 00000000   rw
            TSH_ZL=0x37,  # 00000000   rw
            INT1_DURATION=0x38  # 00000000   rw
    )

    GYRO_RANGE = dict(
            DPS_250=250,
            DPS_500=500,
            DPS_2000=2000
    )
    L3GD20_ADDRESS = 0x6B  # 1101011
    L3GD20_POLL_TIMEOUT = 100
    L3GD20_ID = 0xD4
    L3GD20H_ID = 0xD7

    GYRO_SENSITIVITY = dict(
            DPS_250=22 / 256,  # Roughly 22/256 for fixed point match
            DPS_500=45 / 256,  # Roughly 45/256
            DPS_2000=18 / 256  # Roughly 18/256
    )

    def __init__(self, bus, rng):
        super().__init__(bus, self.L3GD20_ADDRESS)
        self.sensor_id = self.i2c_read_8(self.GYRO_REGISTER['WHO_AM_I'])

        self.v_x, self.v_y, self.v_z = 0, 0, 0
        self.range = rng

        if self.sensor_id != self.L3GD20_ID or self.sensor_id != self.L3GD20H_ID:
            raise Exception("Invalid ID for gyroscope")

        self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG1'], 0x00)
        self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG1'], 0x0F)

        if self.range == self.GYRO_RANGE['DPS_250']:
            self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG4'], 0x00)
        elif self.range == self.GYRO_RANGE['DPS_500']:
            self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG4'], 0x10)
        elif self.range == self.GYRO_RANGE['DPS_2000']:
            self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG4'], 0x20)

    def refresh(self):
        readingValid = False
        while not readingValid:
            self.i2c_send(self.GYRO_REGISTER['OUT_X_L'] | 0x80)
            xlo, xhi, ylo, yhi, zlo, zhi = self.i2c_recv(6)

            self.v_x = xlo | (xhi << 8)
            self.v_y = ylo | (yhi << 8)
            self.v_z = zlo | (zhi << 8)

            if (not (-32760 < self.v_x < 32760) or
                    not (-32760 < self.v_y < 32760) or
                    not (-32760 < self.v_z < 32760)):
                if self.range == self.GYRO_RANGE['DPS_500']:
                    self.range = self.GYRO_RANGE['DPS_2000']
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG1'], 0x00)
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG1'], 0x0F)
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG4'], 0x20)
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG5'], 0x80)
                    readingValid = False

                elif self.range == self.GYRO_RANGE['DPS_250']:
                    self.range = self.GYRO_RANGE['DPS_500']
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG1'], 0x00)
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG1'], 0x0F)
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG4'], 0x10)
                    self.i2c_write_8(self.GYRO_REGISTER['CTRL_REG5'], 0x80)
                    readingValid = False
                else:
                    readingValid = True
            else:
                readingValid = True

        if self.range == self.GYRO_RANGE['DPS_250']:
            self.v_x *= self.GYRO_SENSITIVITY['DPS_250']
            self.v_y *= self.GYRO_SENSITIVITY['DPS_250']
            self.v_z *= self.GYRO_SENSITIVITY['DPS_250']

        elif self.range == self.GYRO_RANGE['DPS_500']:
            self.v_x *= self.GYRO_SENSITIVITY['DPS_500']
            self.v_y *= self.GYRO_SENSITIVITY['DPS_500']
            self.v_z *= self.GYRO_SENSITIVITY['DPS_500']

        elif self.range == self.GYRO_RANGE['DPS_2000']:
            self.v_x *= self.GYRO_SENSITIVITY['DPS_2000']
            self.v_y *= self.GYRO_SENSITIVITY['DPS_2000']
            self.v_z *= self.GYRO_SENSITIVITY['DPS_2000']

        self.v_x *= self.SENSORS_DPS_TO_RADS
        self.v_y *= self.SENSORS_DPS_TO_RADS
        self.v_z *= self.SENSORS_DPS_TO_RADS


