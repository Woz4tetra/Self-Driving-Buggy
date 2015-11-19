/* -------------------- Includes -------------------- */

/* -------------------- Globals --------------------- */

uint8_t gyro_array[6];

/* --------------------- Setup ---------------------- */

/* ---------------------- Loop ---------------------- */

/* --------------------- Serial --------------------- */

for (int index = 7; index < 13; index++) {
    gyro_array[index] = Buf[index];
}

Packet.sendDataArray(gyro_array, 6);