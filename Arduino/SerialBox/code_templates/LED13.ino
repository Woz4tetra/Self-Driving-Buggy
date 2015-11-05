
/* -------------------- Globals --------------------- */

#define LED13_PIN 13

/* --------------------- Setup ---------------------- */

pinMode(LED13_PIN, OUTPUT);

/* ---------------------- Loop ---------------------- */

digitalWrite(LED13_PIN, payload);
Packet.sendCommandReply(command_id, payload);