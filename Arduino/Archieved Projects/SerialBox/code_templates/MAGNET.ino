/* -------------------- Includes -------------------- */

/* -------------------- Globals --------------------- */

uint8_t magnet_array[6];

uint8_t Mag[7];

/* --------------------- Setup ---------------------- */

/* ---------------------- Loop ---------------------- */

// Read register Status 1 and wait for the DRDY: Data Ready

uint8_t ST1;
do
{
    I2Cread(MAG_ADDRESS,0x02,1,&ST1);
}
while (!(ST1&0x01));

// Read magnetometer data
I2Cread(MAG_ADDRESS,0x03,7,Mag);

/* --------------------- Serial --------------------- */

for (int index = 0; index < 6; index++) {
    magnet_array[index] = Mag[index];
}

Packet.sendDataArray(magnet_array, 6);