#include <MPU9250.h>
#include <HallEncoder.h>
#include <SerialParser.h>
#include <Servo.h>

#include <Sensor.h>
#include <Command.h>

#include <Adafruit_GPS.h>

#define mySerial Serial1

Adafruit_GPS GPS(&mySerial);

// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences. 
#define GPSECHO  false

// this keeps track of whether we're using the interrupt
// off by default!
boolean usingInterrupt = false;
void useInterrupt(boolean); // Func prototype keeps Arduino 0023 happy

const int baud = 115200;
const int node = 2;

uint8_t object_id = 0;
uint64_t* payload = new uint64_t;

uint8_t accelgyro_buffer[14];
uint8_t magnet_buffer[7];


void imu_update(uint8_t* data, void* new_data, const int size)
{
    for (int index = 0; index < size; index++) {
        data[index] = ((uint8_t*)new_data)[index];
    }
}
void encoder_update(uint8_t* data, void* new_data, const int size)
{
    uint64_t deref_data = *(uint64_t*)new_data;
    
    // size == 4 (8 hex characters)
    for (int index = size - 1; index >= 0; index--)
    {
        data[index] = (uint8_t)(deref_data & 0xff);
        deref_data = deref_data >> 8;
    }
}


void to_hex(float input, uint8_t *array, int start)
{
    byte* bytearray = (byte*) &input;
    short float_length = 4;
    start *= float_length;
    
    for (int index = float_length - 1; index >= 0; index--) {
        array[((float_length - 1) - index) + start] = bytearray[index];
    }
}

const int gps_float_array_len = 4;
float gps_float_array[4];

void gps_update(uint8_t* data, void* new_data, const int size)
{
    gps_float_array[0] = GPS.latitude;
    gps_float_array[1] = GPS.longitude;
    gps_float_array[2] = GPS.speed;
    gps_float_array[3] = GPS.angle;
    
    for (int float_index = 0; float_index < (size - 2) / 4; float_index++) {
        to_hex(gps_float_array[float_index], data, float_index);
    }
    data[16] = GPS.satellites;
    data[17] = GPS.fixquality;
}

#define LED13_PIN 13

sensor_t accel, gyro, magnet, encoder, gps;
command_t servo1_command, led13_command;

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

Servo servo1;

void setup()
{
    begin_serial(baud);
    
    accel = sensor_new(node, 1, 6, &imu_update);
    gyro = sensor_new(node, 2, 6, &imu_update);
    magnet = sensor_new(node, 3, 6, &imu_update);
    
    encoder = sensor_new(node, 'a', 4, &encoder_update);
    gps = sensor_new(node, 'b', 18, &gps_update);
    
    servo1_command = command_new(node, 6);
    led13_command = command_new(node, 7);
    
    encoder_setup();
    mpu_setup();
    
    pinMode(LED13_PIN, OUTPUT);
    
    servo1.attach(3);
    servo1.write(0);
    
    *payload = 0;
    
    
    
    // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
    GPS.begin(9600);
    mySerial.begin(9600);
    
    // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
    GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
    // uncomment this line to turn on only the "minimum recommended" data
    //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
    // For parsing data, we don't suggest using anything but either RMC only or RMC+GGA since
    // the parser doesn't care about other sentences at this time
    
    // Set the update rate
    GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);   // 1 Hz update rate
    // For the parsing code to work nicely and have time to sort thru the data, and
    // print it out we don't suggest using anything higher than 1 Hz
    
    // Request updates on antenna status, comment out to keep quiet
    GPS.sendCommand(PGCMD_ANTENNA);
    
    // the nice thing about this code is you can have a timer0 interrupt go off
    // every 1 millisecond, and read data from the GPS for you. that makes the
    // loop code a heck of a lot easier!
    
#ifdef __arm__
    usingInterrupt = false;  //NOTE - we don't want to use interrupts on the Due
#else
    useInterrupt(true);
#endif
    
    delay(1000);
    // Ask for firmware version
    mySerial.println(PMTK_Q_RELEASE);
    
    
    
    handshake();
}

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
#endif //#ifdef__AVR__

void loop()
{
//    mpu_update(accelgyro_buffer, magnet_buffer);
    // in case you are not using the interrupt above, you'll
    // need to 'hand query' the GPS, not suggested :(
    if (! usingInterrupt) {
        // read data from the GPS in the 'main loop'
        char c = GPS.read();
        // if you want to debug, this is a good time to do it!
        if (GPSECHO)
            if (c) Serial.print(c);
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
    
    object_id = read_serial(payload);
    
    if (sensor_ids_equal(accel, object_id))
    {
        sensor_update(accel, accelgyro_buffer);
        sensor_toserial(accel);
    }
    
    else if (sensor_ids_equal(gyro, object_id))
    {
        for (int index = 0; index < 6; index++) {
            accelgyro_buffer[index] = accelgyro_buffer[index + 7];
        }
        sensor_update(gyro, accelgyro_buffer);
        sensor_toserial(gyro);
    }
    
    else if (sensor_ids_equal(magnet, object_id))
    {
        sensor_update(magnet, magnet_buffer);
        sensor_toserial(magnet);
    }
    
    else if (sensor_ids_equal(encoder, object_id))
    {
        sensor_update(encoder, (void*)(encoder_distance()));
        sensor_toserial(encoder);
    }
    
    else if (sensor_ids_equal(gps, object_id))
    {
        sensor_update(gps, NULL);
        sensor_toserial(gps);
    }
    
    else if (command_ids_equal(servo1_command, object_id)) {
        servo1.write(*(uint8_t*)payload);
    }
    
    else if (command_ids_equal(led13_command, object_id)) {
        digitalWrite(LED13_PIN, *payload);
    }
}


