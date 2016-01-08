from pyb import I2C
import struct

class DOFsensor(object):
    SENSORS_GRAVITY_EARTH = 9.80665  # Earth's gravity in m/s^2 */
    SENSORS_GRAVITY_MOON = 1.6  # The moon's gravity in m/s^2 */
    SENSORS_GRAVITY_SUN = 275.0  # The sun's gravity in m/s^2 */
    SENSORS_GRAVITY_STANDARD = SENSORS_GRAVITY_EARTH
    SENSORS_MAGFIELD_EARTH_MAX = 60.0  # Maximum magnetic field on Earth's surface */
    SENSORS_MAGFIELD_EARTH_MIN = 30.0  # Minimum magnetic field on Earth's surface */
    SENSORS_PRESSURE_SEALEVELHPA = 1013.25  # Average sea level pressure is 1013.25 hPa */
    SENSORS_DPS_TO_RADS = 0.017453293  # Degrees/s to rad/s multiplier */
    SENSORS_GAUSS_TO_MICROTESLA = 100  # Gauss to micro-Tesla multiplier */

    PRESSURE_SEA = 1013.25

    def __init__(self, bus, address):
        self.bus = bus
        self.address = address
        self.i2c_ref = I2C(self.bus, I2C.MASTER)

        addresses = self.i2c_ref.scan()
        if self.address not in addresses:
            raise Exception("Sensor '%s' not found!" % self.address)

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

    def refresh(self):
        pass