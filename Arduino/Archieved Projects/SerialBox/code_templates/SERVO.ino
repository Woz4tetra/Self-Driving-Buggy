
/* -------------------- Includes -------------------- */
#include <Servo.h>

/* -------------------- Globals --------------------- */

Servo servo1;

/* --------------------- Setup ---------------------- */

servo1.attach(3);
servo1.write(0);

/* ---------------------- Loop ---------------------- */

/* --------------------- Serial --------------------- */

servo1.write(payload);
Packet.sendCommandReply(command_id, payload);