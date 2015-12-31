/* -------------------- Includes -------------------- */

/* -------------------- Globals --------------------- */

/* --------------------- Setup ---------------------- */

/* ---------------------- Loop ---------------------- */

/* --------------------- Serial --------------------- */

for (int index = 0; index < data_length; index++) {
    magnet_data[index] = Mag[index];
}

Packet.sendDataArray(magnet_data, data_length);