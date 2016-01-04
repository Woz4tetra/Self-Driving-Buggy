from .dof_sensor import DOFsensor

class Accelerometer(DOFsensor):
    LSM303_REGISTER_ACCEL = dict(
        CTRL_REG1_A=0x20,
        CTRL_REG2_A=0x21,
        CTRL_REG3_A=0x22,
        CTRL_REG4_A=0x23,
        CTRL_REG5_A=0x24,
        CTRL_REG6_A=0x25,
        REFERENCE_A=0x26,
        STATUS_REG_A=0x27,
        OUT_X_L_A=0x28,
        OUT_X_H_A=0x29,
        OUT_Y_L_A=0x2A,
        OUT_Y_H_A=0x2B,
        OUT_Z_L_A=0x2C,
        OUT_Z_H_A=0x2D,
        FIFO_CTRL_REG_A=0x2E,
        FIFO_SRC_REG_A=0x2F,
        INT1_CFG_A=0x30,
        INT1_SOURCE_A=0x31,
        INT1_THS_A=0x32,
        INT1_DURATION_A=0x33,
        INT2_CFG_A=0x34,
        INT2_SOURCE_A=0x35,
        INT2_THS_A=0x36,
        INT2_DURATION_A=0x37,
        CLICK_CFG_A=0x38,
        CLICK_SRC_A=0x39,
        CLICK_THS_A=0x3A,
        TIME_LIMIT_A=0x3B,
        TIME_LATENCY_A=0x3C,
        TIME_WINDOW_A=0x3D
    )
    LSM303_ADDRESS_ACCEL = 0x19
    MG_LSB = 0.001

    def __init__(self, bus):
        super().__init__(bus, self.LSM303_ADDRESS_ACCEL)
        self.x, self.y, self.z = 0, 0, 0

    def refresh(self):
        self.i2c_send(self.LSM303_REGISTER_ACCEL['OUT_X_L_A'] | 0x80)
        xlo, xhi, ylo, yhi, zlo, zhi = self.i2c_recv(6)

        self.x = ((xlo | (xhi << 8)) >> 4) * self.MG_LSB * self.SENSORS_GRAVITY_STANDARD
        self.y = ((ylo | (yhi << 8)) >> 4) * self.MG_LSB * self.SENSORS_GRAVITY_STANDARD
        self.z = ((zlo | (zhi << 8)) >> 4) * self.MG_LSB * self.SENSORS_GRAVITY_STANDARD

class Magnetometer(DOFsensor):
    LSM303_REGISTER_MAG = dict(
        CRA_REG_M=0x00,
        CRB_REG_M=0x01,
        MR_REG_M=0x02,
        OUT_X_H_M=0x03,
        OUT_X_L_M=0x04,
        OUT_Z_H_M=0x05,
        OUT_Z_L_M=0x06,
        OUT_Y_H_M=0x07,
        OUT_Y_L_M=0x08,
        SR_REG_Mg=0x09,
        IRA_REG_M=0x0A,
        IRB_REG_M=0x0B,
        IRC_REG_M=0x0C,
        TEMP_OUT_H_M=0x31,
        TEMP_OUT_L_M=0x32
    )

    LSM303_MAGGAIN = [  # range of mag values +/-
        0x20, # gain 1.3
        0x40, # gain 1.9
        0x60, # gain 2.5
        0x80, # gain 4.0
        0xA0, # gain 4.7
        0xC0, # gain 5.6
        0xE0 # gain 8.1
    ]

    LSM303_ADDRESS_MAG = 0x1e

    def __init__(self, bus):
        super().__init__(bus, self.LSM303_ADDRESS_MAG)

        self.i2c_write_8(self.LSM303_REGISTER_MAG['MR_REG_M'], 0x00)
        reg1_a = self.i2c_read_8(self.LSM303_REGISTER_MAG['CRA_REG_M'])
        if reg1_a != 0x10:
            raise Exception("Invalid cra register for LSM303 Mag!")

        self.gain = 0
        self.gauss_lsb_xy = 0
        self.gauss_lsb_z = 0
        self.set_mag_gain(self.LSM303_MAGGAIN[0])

        self.x, self.y, self.z = 0, 0, 0

    def set_mag_gain(self, gain):
        self.i2c_write_8(self.LSM303_REGISTER_MAG['CRB_REG_M'], self.LSM303_MAGGAIN[gain])
        self.gain = gain

        if gain == 0:
            self.gauss_lsb_xy = 1100
            self.gauss_lsb_z = 980

        elif gain == 1:
            self.gauss_lsb_xy = 855
            self.gauss_lsb_z = 760

        elif gain == 2:
            self.gauss_lsb_xy = 670
            self.gauss_lsb_z = 600

        elif gain == 3:
            self.gauss_lsb_xy = 450
            self.gauss_lsb_z = 400

        elif gain == 4:
            self.gauss_lsb_xy = 400
            self.gauss_lsb_z = 355

        elif gain == 5:
            self.gauss_lsb_xy = 330
            self.gauss_lsb_z = 295

        elif gain == 6:
            self.gauss_lsb_xy = 230
            self.gauss_lsb_z = 205

    def read(self):
        self.i2c_send(self.LSM303_REGISTER_MAG['OUT_X_H_M'])
        xlo, xhi, ylo, yhi, zlo, zhi = self.i2c_recv(6)

        x = ((xlo | (xhi << 8)) >> 4)
        y = ((ylo | (yhi << 8)) >> 4)
        z = ((zlo | (zhi << 8)) >> 4)

        return x, y, z

    def set_mag_rate(self, rate):
        reg_m = (rate & 0x07) << 2
        self.i2c_write_8(self.LSM303_REGISTER_MAG['CRA_REG_M'], reg_m)

    def refresh(self):
        reading_valid = False
        while not reading_valid:
            reg_mg = self.i2c_read_8(self.LSM303_REGISTER_MAG['SR_REG_Mg'])
            if not (reg_mg & 0x1):
                return

            raw_x, raw_y, raw_z = self.read()

            if (not (-2040 < raw_x < 2040) or
                    not (-2040 < raw_y < 2040) or
                    not (-2040 < raw_z < 2040)):  # if sensor is saturating
                self.set_mag_gain(self.gain + 1)
                reading_valid = False
            else:
                reading_valid = True

            self.x = raw_x / self.gauss_lsb_xy * self.SENSORS_GAUSS_TO_MICROTESLA
            self.y = raw_y / self.gauss_lsb_xy * self.SENSORS_GAUSS_TO_MICROTESLA
            self.z = raw_z / self.gauss_lsb_z * self.SENSORS_GAUSS_TO_MICROTESLA



