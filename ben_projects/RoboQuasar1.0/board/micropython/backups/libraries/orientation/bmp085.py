from .dof_sensor import DOFsensor

class Barometer(DOFsensor):
    BMP085_MODE = dict(
            ULTRALOWPOWER=0,
            STANDARD=1,
            HIGHRES=2,
            ULTRAHIGHRES=3
    )
    BMP085_REGISTER = dict(
            CAL_AC1=0xAA,
            CAL_AC2=0xAC,
            CAL_AC3=0xAE,
            CAL_AC4=0xB0,
            CAL_AC5=0xB2,
            CAL_AC6=0xB4,
            CAL_B1=0xB6,
            CAL_B2=0xB8,
            CAL_MB=0xBA,
            CAL_MC=0xBC,
            CAL_MD=0xBE,
            CHIPID=0xD0,
            VERSION=0xD1,
            SOFTRESET=0xE0,
            CONTROL=0xF4,
            TEMPDATA=0xF6,
            PRESSUREDATA=0xF6,
            READTEMPCMD=0x2E,
            READPRESSURECMD=0x34
    )

    BMP085_ADDRESS = 0x77

    def __init__(self, bus, mode=3):
        super().__init__(bus, self.BMP085_ADDRESS)
        self.mode = mode
        self.bus = bus
        self.coeffs = {}

        self.altitude = 0
        self.pressure = 0
        self.temperature = 0
        self.pressure_sea = self.PRESSURE_SEA

        assert self.mode in self.BMP085_MODE.values()

        if self.i2c_read_8(self.BMP085_REGISTER['CHIPID']) != 0x55:
            raise Exception("Invalid chip ID for BMP085!")

        self.read_coefficients()

    def read_coefficients(self):
        self.coeffs['ac1'] = self.i2c_sread_16(self.BMP085_REGISTER['ac1'])
        self.coeffs['ac2'] = self.i2c_sread_16(self.BMP085_REGISTER['ac2'])
        self.coeffs['ac3'] = self.i2c_sread_16(self.BMP085_REGISTER['ac3'])
        self.coeffs['ac4'] = self.i2c_read_16(self.BMP085_REGISTER['ac4'])
        self.coeffs['ac5'] = self.i2c_read_16(self.BMP085_REGISTER['ac5'])
        self.coeffs['ac6'] = self.i2c_read_16(self.BMP085_REGISTER['ac6'])
        self.coeffs['b1'] = self.i2c_sread_16(self.BMP085_REGISTER['b1'])
        self.coeffs['b2'] = self.i2c_sread_16(self.BMP085_REGISTER['b2'])
        self.coeffs['mb'] = self.i2c_sread_16(self.BMP085_REGISTER['mb'])
        self.coeffs['mc'] = self.i2c_sread_16(self.BMP085_REGISTER['mc'])

    def read_raw_temperature(self):
        self.i2c_write_8(self.BMP085_REGISTER['CONTROL'],
                       self.BMP085_REGISTER['READTEMPCMD'])
        pyb.delay(5)
        return self.i2c_read_16(self.BMP085_REGISTER['TEMPDATA'])

    def read_raw_pressure(self):
        self.i2c_write_8(self.BMP085_REGISTER['CONTROL'],
                       self.BMP085_REGISTER['READPRESSURECMD'] + self.mode << 6)

        if self.mode == self.BMP085_MODE['ULTRALOWPOWER']:
            pyb.delay(5)
        elif self.mode == self.BMP085_MODE['STANDARD']:
            pyb.delay(8)
        elif self.mode == self.BMP085_MODE['HIGHRES']:
            pyb.delay(14)
        elif self.mode == self.BMP085_MODE['ULTRAHIGHRES']:
            pyb.delay(26)

        p16 = self.i2c_read_16(self.BMP085_REGISTER['PRESSUREDATA'])
        pressure = p16 << 8
        p8 = self.i2c_read_8(self.BMP085_REGISTER['PRESSUREDATA'] + 2)
        pressure += p8
        pressure >>= (8 - self.mode)

        return pressure

    @staticmethod
    def pressure_to_altitude(sea_level, pressure_atm):
        return 44330.0 * (1.0 - pressure_atm / sea_level ** 0.1903)

    def computeB5(self, ut):
        X1 = (ut - self.coeffs['ac6']) * self.coeffs['ac5'] >> 15
        X2 = self.coeffs['mc'] << 11 / (X1 + self.coeffs['md'])

        return X1 + X2

    def get_pressure(self):
        ut = self.read_raw_temperature()
        up = self.read_raw_pressure()

        b5 = self.computeB5(ut)
        b6 = b5 - 4000
        x1 = self.coeffs['b2'] * ((b6 ** 2) >> 12) >> 11
        x2 = (self.coeffs['ac2'] * b6) >> 11
        x3 = x1 + x2
        b3 = (((self.coeffs['ac1'] * 4 + x3) << self.mode) + 2) >> 2

        x1 = (self.coeffs['ac3'] * b6) >> 13
        x2 = (self.coeffs['b1'] * ((b6 ** 2) >> 12)) >> 16
        x3 = (x1 + x2 + 2) >> 2
        b4 = (self.coeffs['ac4'] * (x3 + 32768)) >> 15
        b7 = (up - b3) * (50000 >> self.mode)

        if b7 < 0x80000000:
            p = (b7 << 1) / b4
        else:
            p = (b7 / b4) << 1

        x1 = (p >> 8) ** 2
        x1 = (x1 * 3038) >> 16
        x2 = (-7357 * p) >> 16

        return p + ((x1 + x2 + 3791) >> 4)

    def get_temperature(self):
        ut = self.read_raw_temperature()
        b5 = self.computeB5(ut)
        t = (b5 + 8) >> 4
        t /= 10

        return t

    def refresh(self):
        self.pressure = self.get_pressure()
        self.temperature = self.get_temperature()
        self.altitude = self.pressure_to_altitude(self.pressure_sea,
                                                  self.pressure)

