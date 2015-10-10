
#include <Adafruit_GPS.h>

#include "SerialPacket.h"
#include "defines.h"

/* Command IDs */
#define ACCEL_GYRO_ID 0x00
#define ENCODER_ID 0x01
#define SERVO_ID 0x02
#define GPS_ID 0x03
#define LED13_ID 0x04

uint8_t command_id = 0;
uint8_t payload = 0;

SerialPacket Packet;

#define LED13_PIN 13

/* GPS Globals */
// GPS power pin to Arduino Due 3.3V output.
// GPS ground pin to Arduino Due ground.
// For hardware serial 1 (recommended):
//   GPS TX to Arduino Due Serial1 RX pin 19
//   GPS RX to Arduino Due Serial1 TX pin 18
#define mySerial Serial1

Adafruit_GPS GPS(&mySerial);

uint8_t gps_array[12];
float gps_float_array[6];

// this keeps track of whether we're using the interrupt
// off by default!
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy

#ifdef __AVR__
// Interrupt is called once a millisecond, looks for any new GPS data, and stores it
SIGNAL(TIMER0_COMPA_vect) {
    char c = GPS.read();
    // if you want to debug, this is a good time to do it!
#ifdef UDR0
    if (GPSECHO)
    if (c) UDR0 = c;  
    // writing direct to UDR0 is much much faster than Serial.print 
    // but only one character can be written at a time. 
#endif
}

void useInterrupt(boolean v) {
    if (v) {
        // Timer0 is already used for millis() - we'll just interrupt somewhere
        // in the middle and call the "Compare A" function above
        OCR0A = 0xAF;
        TIMSK0 |= _BV(OCIE0A);
        usingInterrupt = true;
    } else {
        // do not call the interrupt function COMPA anymore
        TIMSK0 &= ~_BV(OCIE0A);
        usingInterrupt = false;
    }
}
#endif

void setup()
{
    Serial.begin(115200);
    // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
    GPS.begin(9600);
    mySerial.begin(9600);
    
    // Enable RMC (recommended minimum) and GGA (fix data) including altitude
    GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
    
    // Set the update rate
    GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
    
    // Request updates on antenna status, comment out to keep quiet
    GPS.sendCommand(PGCMD_ANTENNA);
    
    #ifdef __arm__
        usingInterrupt = false;  //NOTE - we don't want to use interrupts on the Due
    #else
        useInterrupt(true);
    #endif
    
    delay(1000);
    
//    Packet.begin(115200, 2);
//    handshake();
}

void loop()
{
    // in case you are not using the interrupt above, you'll
    // need to 'hand query' the GPS, not suggested :(
    if (!usingInterrupt) {
        // read data from the GPS in the 'main loop'
        char c = GPS.read();
    }
    // if a sentence is received, we can check the checksum, parse it...
    if (GPS.newNMEAreceived()) {
        // a tricky thing here is if we print the NMEA sentence, or data
        // we end up not listening and catching other sentences! 
        // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
        //Serial.println(GPS.lastNMEA());   // this also sets the newNMEAreceived() flag to false
        
        if (!GPS.parse(GPS.lastNMEA()))   // this also sets the newNMEAreceived() flag to false
        return;  // we can fail to parse a sentence in which case we should just wait for another
    }
    Serial.print("\nTime: ");
    Serial.print(GPS.hour, DEC); Serial.print(':');
    Serial.print(GPS.minute, DEC); Serial.print(':');
    Serial.print(GPS.seconds, DEC); Serial.print('.');
    Serial.println(GPS.milliseconds);
    Serial.print("Date: ");
    Serial.print(GPS.day, DEC); Serial.print('/');
    Serial.print(GPS.month, DEC); Serial.print("/20");
    Serial.println(GPS.year, DEC);
    Serial.print("Fix: "); Serial.print((int)GPS.fix);
    Serial.print(" quality: "); Serial.println((int)GPS.fixquality); 
    if (GPS.fix) {
        Serial.print("Location: ");
        Serial.print(GPS.latitude, 4); Serial.print(GPS.lat);
        Serial.print(", "); 
        Serial.print(GPS.longitude, 4); Serial.println(GPS.lon);
        
        Serial.print("Speed (knots): "); Serial.println(GPS.speed);
        Serial.print("Angle: "); Serial.println(GPS.angle);
        Serial.print("Altitude: "); Serial.println(GPS.altitude);
        Serial.print("Satellites: "); Serial.println((int)GPS.satellites);
    }
}

/*
    SerialEvent occurs whenever a new data comes in the
    hardware serial RX.  This routine is run between each
    time loop() runs, so using delay inside loop can delay
    response.  Multiple bytes of data may be available.
*/
void serialEvent()
{
//    int result = Packet.readSerialData();
//    if (result == 1)
//    {
//        command_id = Packet.getCommandID();
//        payload = Packet.getPayload();
//        
//        while (Serial.read() > 0) {  }
//        Serial.flush();
//    }
//    else if (result == 2)
//    {
//        if (command_id == LED13_ID)
//        {
//            digitalWrite(LED13_PIN, payload);
//            Packet.sendCommandReply(command_id, payload);
//        }
//        else if (command_id == GPS_ID)
//        {
//            
//        }
//    }
    
    
//    gps_float_array[0] = GPS.latitude;
//    gps_float_array[1] = GPS.longitude;
//    gps_float_array[2] = GPS.speed;
//    gps_float_array[3] = GPS.angle;
//    gps_float_array[4] = GPS.satellites;
//    gps_float_array[5] = GPS.fixquality;
//    for (int float_index; float_index < 6; float_index++)
//    {
//        byte* array = (byte*) &gps_float_array[float_index];
//        for (int index = 0; index < 4; index++) {
//            gps_array[float_index * 4 + index] = array[index];
//        }
//    }
    
//    Packet.sendDataArray(gps_array, 24);
}

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}