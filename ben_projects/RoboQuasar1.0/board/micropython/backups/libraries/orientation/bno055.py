import struct

# from .dof_sensor import DOFsensor
import pyb



class IMU(object):
    REGISTERS = dict(
            # Page id register definition
            BNO055_PAGE_ID_ADDR=0X07,

            # PAGE0 REGISTER DEFINITION START
            BNO055_CHIP_ID_ADDR=0x00,
            BNO055_ACCEL_REV_ID_ADDR=0x01,
            BNO055_MAG_REV_ID_ADDR=0x02,
            BNO055_GYRO_REV_ID_ADDR=0x03,
            BNO055_SW_REV_ID_LSB_ADDR=0x04,
            BNO055_SW_REV_ID_MSB_ADDR=0x05,
            BNO055_BL_REV_ID_ADDR=0X06,

            # Accel data register
            BNO055_ACCEL_DATA_X_LSB_ADDR=0X08,
            BNO055_ACCEL_DATA_X_MSB_ADDR=0X09,
            BNO055_ACCEL_DATA_Y_LSB_ADDR=0X0A,
            BNO055_ACCEL_DATA_Y_MSB_ADDR=0X0B,
            BNO055_ACCEL_DATA_Z_LSB_ADDR=0X0C,
            BNO055_ACCEL_DATA_Z_MSB_ADDR=0X0D,

            # Mag data register
            BNO055_MAG_DATA_X_LSB_ADDR=0X0E,
            BNO055_MAG_DATA_X_MSB_ADDR=0X0F,
            BNO055_MAG_DATA_Y_LSB_ADDR=0X10,
            BNO055_MAG_DATA_Y_MSB_ADDR=0X11,
            BNO055_MAG_DATA_Z_LSB_ADDR=0X12,
            BNO055_MAG_DATA_Z_MSB_ADDR=0X13,

            # Gyro data registers
            BNO055_GYRO_DATA_X_LSB_ADDR=0X14,
            BNO055_GYRO_DATA_X_MSB_ADDR=0X15,
            BNO055_GYRO_DATA_Y_LSB_ADDR=0X16,
            BNO055_GYRO_DATA_Y_MSB_ADDR=0X17,
            BNO055_GYRO_DATA_Z_LSB_ADDR=0X18,
            BNO055_GYRO_DATA_Z_MSB_ADDR=0X19,

            # Euler data registers
            BNO055_EULER_H_LSB_ADDR=0X1A,
            BNO055_EULER_H_MSB_ADDR=0X1B,
            BNO055_EULER_R_LSB_ADDR=0X1C,
            BNO055_EULER_R_MSB_ADDR=0X1D,
            BNO055_EULER_P_LSB_ADDR=0X1E,
            BNO055_EULER_P_MSB_ADDR=0X1F,

            # Quaternion data registers
            BNO055_QUATERNION_DATA_W_LSB_ADDR=0X20,
            BNO055_QUATERNION_DATA_W_MSB_ADDR=0X21,
            BNO055_QUATERNION_DATA_X_LSB_ADDR=0X22,
            BNO055_QUATERNION_DATA_X_MSB_ADDR=0X23,
            BNO055_QUATERNION_DATA_Y_LSB_ADDR=0X24,
            BNO055_QUATERNION_DATA_Y_MSB_ADDR=0X25,
            BNO055_QUATERNION_DATA_Z_LSB_ADDR=0X26,
            BNO055_QUATERNION_DATA_Z_MSB_ADDR=0X27,

            # Linear acceleration data registers
            BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR=0X28,
            BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR=0X29,
            BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR=0X2A,
            BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR=0X2B,
            BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR=0X2C,
            BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR=0X2D,

            # Gravity data registers
            BNO055_GRAVITY_DATA_X_LSB_ADDR=0X2E,
            BNO055_GRAVITY_DATA_X_MSB_ADDR=0X2F,
            BNO055_GRAVITY_DATA_Y_LSB_ADDR=0X30,
            BNO055_GRAVITY_DATA_Y_MSB_ADDR=0X31,
            BNO055_GRAVITY_DATA_Z_LSB_ADDR=0X32,
            BNO055_GRAVITY_DATA_Z_MSB_ADDR=0X33,

            # Temperature data register
            BNO055_TEMP_ADDR=0X34,

            # Status registers
            BNO055_CALIB_STAT_ADDR=0X35,
            BNO055_SELFTEST_RESULT_ADDR=0X36,
            BNO055_INTR_STAT_ADDR=0X37,

            BNO055_SYS_CLK_STAT_ADDR=0X38,
            BNO055_SYS_STAT_ADDR=0X39,
            BNO055_SYS_ERR_ADDR=0X3A,

            # Unit selection register
            BNO055_UNIT_SEL_ADDR=0X3B,
            BNO055_DATA_SELECT_ADDR=0X3C,

            # Mode registers
            BNO055_OPR_MODE_ADDR=0X3D,
            BNO055_PWR_MODE_ADDR=0X3E,

            BNO055_SYS_TRIGGER_ADDR=0X3F,
            BNO055_TEMP_SOURCE_ADDR=0X40,

            # Axis remap registers
            BNO055_AXIS_MAP_CONFIG_ADDR=0X41,
            BNO055_AXIS_MAP_SIGN_ADDR=0X42,

            # SIC registers
            BNO055_SIC_MATRIX_0_LSB_ADDR=0X43,
            BNO055_SIC_MATRIX_0_MSB_ADDR=0X44,
            BNO055_SIC_MATRIX_1_LSB_ADDR=0X45,
            BNO055_SIC_MATRIX_1_MSB_ADDR=0X46,
            BNO055_SIC_MATRIX_2_LSB_ADDR=0X47,
            BNO055_SIC_MATRIX_2_MSB_ADDR=0X48,
            BNO055_SIC_MATRIX_3_LSB_ADDR=0X49,
            BNO055_SIC_MATRIX_3_MSB_ADDR=0X4A,
            BNO055_SIC_MATRIX_4_LSB_ADDR=0X4B,
            BNO055_SIC_MATRIX_4_MSB_ADDR=0X4C,
            BNO055_SIC_MATRIX_5_LSB_ADDR=0X4D,
            BNO055_SIC_MATRIX_5_MSB_ADDR=0X4E,
            BNO055_SIC_MATRIX_6_LSB_ADDR=0X4F,
            BNO055_SIC_MATRIX_6_MSB_ADDR=0X50,
            BNO055_SIC_MATRIX_7_LSB_ADDR=0X51,
            BNO055_SIC_MATRIX_7_MSB_ADDR=0X52,
            BNO055_SIC_MATRIX_8_LSB_ADDR=0X53,
            BNO055_SIC_MATRIX_8_MSB_ADDR=0X54,

            # Accelerometer Offset registers
            ACCEL_OFFSET_X_LSB_ADDR=0X55,
            ACCEL_OFFSET_X_MSB_ADDR=0X56,
            ACCEL_OFFSET_Y_LSB_ADDR=0X57,
            ACCEL_OFFSET_Y_MSB_ADDR=0X58,
            ACCEL_OFFSET_Z_LSB_ADDR=0X59,
            ACCEL_OFFSET_Z_MSB_ADDR=0X5A,

            # Magnetometer Offset registers
            MAG_OFFSET_X_LSB_ADDR=0X5B,
            MAG_OFFSET_X_MSB_ADDR=0X5C,
            MAG_OFFSET_Y_LSB_ADDR=0X5D,
            MAG_OFFSET_Y_MSB_ADDR=0X5E,
            MAG_OFFSET_Z_LSB_ADDR=0X5F,
            MAG_OFFSET_Z_MSB_ADDR=0X60,

            # Gyroscope Offset registers
            GYRO_OFFSET_X_LSB_ADDR=0X61,
            GYRO_OFFSET_X_MSB_ADDR=0X62,
            GYRO_OFFSET_Y_LSB_ADDR=0X63,
            GYRO_OFFSET_Y_MSB_ADDR=0X64,
            GYRO_OFFSET_Z_LSB_ADDR=0X65,
            GYRO_OFFSET_Z_MSB_ADDR=0X66,

            # Radius registers
            ACCEL_RADIUS_LSB_ADDR=0X67,
            ACCEL_RADIUS_MSB_ADDR=0X68,
            MAG_RADIUS_LSB_ADDR=0X69,
            MAG_RADIUS_MSB_ADDR=0X6A
    )
    VECTORS = dict(
            ACCELEROMETER="BNO055_ACCEL_DATA_X_LSB_ADDR",
            MAGNETOMETER="BNO055_MAG_DATA_X_LSB_ADDR",
            GYROSCOPE="BNO055_GYRO_DATA_X_LSB_ADDR",
            EULER="BNO055_EULER_H_LSB_ADDR",
            LINEARACCEL="BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR",
            GRAVITY="BNO055_GRAVITY_DATA_X_LSB_ADDR"
    )

    BNO055_ADDRESS_A = 0x28
    BNO055_ADDRESS_B = 0x29
    BNO055_ID = 0xA0

    def __init__(self, bus, use_address_a=True):
        if use_address_a:
            self.address = self.BNO055_ADDRESS_A
        else:
            self.address = self.BNO055_ADDRESS_B

        self.bus = bus
        self.i2c_ref = pyb.I2C(self.bus, pyb.I2C.MASTER)

        addresses = self.i2c_ref.scan()
        if self.address not in addresses:
            raise Exception("Sensor '%s' not found!" % self.address)

        chip_id = self.i2c_read_8(self.REGISTERS["BNO055_CHIP_ID_ADDR"])
        if chip_id != self.BNO055_ID:
            pyb.delay(1000)
            chip_id = self.i2c_read_8(self.REGISTERS["BNO055_CHIP_ID_ADDR"])
            if chip_id != self.BNO055_ID:
                raise Exception("Chip ID invalid: " + str(chip_id))

        self.quat_scale = 1.0 / (1 << 14)

    def i2c_read_8(self, register):
        raw_bytes = self.i2c_ref.mem_read(1, self.address, register)
        return struct.unpack(">B", raw_bytes)[0]  # unsigned 8-bit

    def i2c_read_16(self, register):
        raw_bytes = self.i2c_ref.mem_read(2, self.address, register)
        return struct.unpack(">H", raw_bytes)[0]  # unsigned 16-bit

    def i2c_sread_16(self, register):
        raw_bytes = self.i2c_ref.mem_read(2, self.address, register)
        return struct.unpack(">h", raw_bytes)[0]  # signed 16-bit

    def i2c_write_8(self, register, value):
        self.i2c_ref.mem_write(value, self.address, register,
                               timeout=10, addr_size=8)

    def i2c_recv(self, num_bytes):
        raw_bytes = self.i2c_ref.recv(num_bytes, self.address)
        return struct.unpack(">%sb" % str(num_bytes), raw_bytes)

    def i2c_send(self, data):
        self.i2c_ref.send(data, self.address)

    def get_vector(self, source, use_raw=False):
        self.i2c_send(self.REGISTERS[self.VECTORS[source]])
        buffer = self.i2c_recv(6)
        x = (buffer[1] << 8) | buffer[0]
        y = (buffer[3] << 8) | buffer[2]
        z = (buffer[5] << 8) | buffer[4]

        if use_raw:
            if source == "MAGNETOMETER" or source == "EULER":
                divisor = 16.0
            elif source == "GYROSCOPE":
                divisor = 900.0
            elif source == "GRAVITY" or source == "ACCELEROMETER" or \
                    source == "LINEARACCEL":
                divisor = 100.0
            else:
                divisor = 1.0

            return x / divisor, y / divisor, z / divisor
        else:
            return x, y, z

    def get_quaternion(self, use_raw=False):
        buffer = self.i2c_recv(8)
        w = (buffer[1] << 8) | buffer[0]
        x = (buffer[3] << 8) | buffer[2]
        y = (buffer[5] << 8) | buffer[4]
        z = (buffer[7] << 8) | buffer[6]

        if use_raw:
            return (self.quat_scale * w,
                    self.quat_scale * x,
                    self.quat_scale * y,
                    self.quat_scale * z)
        else:
            return w, x, y, z

