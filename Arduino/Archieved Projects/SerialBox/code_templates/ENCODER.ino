
/* -------------------- Includes -------------------- */
#include <DueTimer.h>

/* -------------------- Globals --------------------- */

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

/* --------------------- Setup ---------------------- */

/*disable interrupts to ensure we won't receive the first timer 
 or I2C interrupt before we are ready*/
noInterrupts();

pinMode(A0, INPUT);

is_in_range = false; //make sure we don't start at > 0 distance
distance = 0;

Timer1.attachInterrupt(handler); //handler is a function pointer
Timer1.start(ADC_POLLING_PERIOD_US);
interrupts();

/* ---------------------- Loop ---------------------- */

/* --------------------- Serial --------------------- */

noInterrupts();
Packet.sendData16bit(command_id, distance);
interrupts();