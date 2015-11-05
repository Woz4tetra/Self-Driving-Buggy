
/**
 *  @file SerialBox.ino
 *  
 *  Self Driving Buggy sensor board drivers and serial communication
 *  
 *  @author Ben Warwick
 *  @author Nat Jeffries
 *  Add yourselves to authors field upon contribution!
 *  
 *  In order to run this code you need the following libraries:
 *  https://github.com/ivanseidel/DueTimer
 *  Wire.h library (built-in)
 *  /ben_projects/Self-Driving\ Buggy\ Rev.\ 6/board/test_serial.py
 *  
 */

//#include "I2Cdev.h"
//#include "MPU6050_6Axis_MotionApps20.h"
#include <Wire.h>
#include <DueTimer.h>
#include <Servo.h>
#include <Adafruit_GPS.h>

#include <SerialPacket.h>
#include <defines.h>

/* ================================================== *
 *                  Global constants                  *
 * ================================================== */


/* -------------- Command IDs start ----------------- */
/*                                                    */
#define ENCODER_ID 0x00
#define LED13_ID 0x01
#define SERVO_ID 0x02
/*                                                    */
/* --------------- Command IDs end ------------------ */

/* -------------- Serial Globals start -------------- */
/*                                                    */
const int baud = 9600;
const int node = 2;
/*                                                    */
/* --------------- Serial Globals end --------------- */


/* --------------- Auto Globals start --------------- */
/*                                                    */
/* ----- ENCODER globals ----- */

bool is_in_range; //if true, trigger when we see out-of-range value
int last_rising_edge; //ms
volatile uint16_t distance; // counts of the encoder

#define HYST_TRIG_HIGH 950 //TODO: Tune these based on OBSERVED values
#define HYST_TRIG_LOW 850
//#define WHEEL_CIR (10.0 * PI)
#define ADC_POLLING_PERIOD_US 1000 //1KHz polling rate
/*
 The following back-of-the-envelope calcultaions indicate max speed:
 Assume we must poll at least 50x per revolution in order to 
 ALWAYS detect the magnet (this is conservative).
 Inches per Revolution = 31.415
 1KHz sample rate => 20 revolutions per second at 50 samples/rev
 628.3 inches per second => (approx) 37mph
 */

/* handler for timer interrupt during which ADC is polled */
void handler()
{
    int hall_value = analogRead(A0);
    
    if (is_in_range && (hall_value > HYST_TRIG_HIGH))
    {
        distance += 1; //WHEEL_CIR;
        is_in_range = false;
    }
    else if (!is_in_range && (hall_value <= HYST_TRIG_LOW)) {
        is_in_range = true;
    }
}


/* ----- LED13 globals ----- */

#define LED13_PIN 13


/* ----- SERVO globals ----- */

Servo servo1;


/*                                                    */
/* ---------------- Auto Globals end ---------------- */

/* ================================================== *
 *                       Setup                        *
 * ================================================== */

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

void setup()
{
    Packet.begin(baud, node);
    
/* ---------------- Auto Setup start ---------------- */
/*                                                    */
	/* ----- ENCODER setup ----- */
	
	/*disable interrupts to ensure we won't receive the first timer 
	 or I2C interrupt before we are ready*/
	noInterrupts();
	
	pinMode(A0, INPUT);
	
	is_in_range = false; //make sure we don't start at > 0 distance
	distance = 0;
	
	Timer1.attachInterrupt(handler); //handler is a function pointer
	Timer1.start(ADC_POLLING_PERIOD_US);
	interrupts();
	
	

	/* ----- LED13 setup ----- */
	
	pinMode(LED13_PIN, OUTPUT);
	
	

	/* ----- SERVO setup ----- */
	
	servo1.attach(3);
	servo1.write(0);
	
	

/*                                                    */
/* ----------------- Auto Setup end ----------------- */
    
    handshake();
}

/* ================================================== *
 *                  Loop and Serial                   *
 * ================================================== */

void loop()
{
    
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

/*
 SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent()
{
    /* ---------------- Read Serial ----------------- */
    int result = Packet.readSerialData();
    // if result == 0, misformed packet, don't do anything
    if (result == 1)
    {
        command_id = Packet.getCommandID();
        payload = Packet.getPayload();
        
        while (Serial.read() > 0) {  }
        Serial.flush();
    }
    else if (result == 2)
    {
/* ----------------- Auto Loop start ---------------- */
/*                                                    */
		/* ----- ENCODER loop ----- */
		
		noInterrupts();
		Packet.sendData16bit(command_id, distance);
		interrupts();

		/* ----- LED13 loop ----- */
		
		digitalWrite(LED13_PIN, payload);
		Packet.sendCommandReply(command_id, payload);

		/* ----- SERVO loop ----- */
		
		servo1.write(payload);
		Packet.sendCommandReply(command_id, payload);

/*                                                    */
/* ------------------ Auto Loop end ----------------- */
    }
}
