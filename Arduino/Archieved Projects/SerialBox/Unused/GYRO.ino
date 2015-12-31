/* -------------------- Includes -------------------- */

/* -------------------- Globals --------------------- */

/* --------------------- Setup ---------------------- */

/* ---------------------- Loop ---------------------- */

/* --------------------- Serial --------------------- */

for (int index = 0; index < data_length; index++) {
    gyro_data[index] = Buf[index + data_length];
}

Packet.sendDataArray(gyro_data, data_length);