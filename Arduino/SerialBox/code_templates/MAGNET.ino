/* -------------------- Includes -------------------- */

/* -------------------- Globals --------------------- */

I2Cdev I2C_M;

const int mag_data_length = 6;

uint8_t magnet_uint8[mag_data_length];

/* --------------------- Setup ---------------------- */

/* ---------------------- Loop ---------------------- */

I2C_M.writeByte(MPU9150_RA_MAG_ADDRESS, 0x0A, 0x01); //enable the magnetometer
delay(10);
I2C_M.readBytes(MPU9150_RA_MAG_ADDRESS, MPU9150_RA_MAG_XOUT_L,
                mag_data_length, magnet_uint8);

/* --------------------- Serial --------------------- */

Packet.sendDataArray(magnet_uint8, mag_data_length);