
#include <NewPing.h>

#define SONAR_TRIGGER_PIN_1  8
#define SONAR_ECHO_PIN_1     6
#define MAX_DISTANCE 200

NewPing sonar1(SONAR_TRIGGER_PIN_1, SONAR_ECHO_PIN_1, MAX_DISTANCE);
unsigned int sonar1Reading = 0;

long time0;


/* -------------------------------------------------- */
/*                      Setup                         */
/* -------------------------------------------------- */

int var1 = 0;

void setup()
{
    Serial.begin(38400);
    
    time0 = millis();
    
    establishContact();
}


/* -------------------------------------------------- */
/*                       Loop                         */
/* -------------------------------------------------- */
void loop()
{
    char incommingByte = Serial.read();
    
    if (Serial.available() > 0)
    {
        if (incommingByte == 't')
        {
            Serial.print(millis(), DEC);
            Serial.print('\n');
        }
        else if (incommingByte == 'v') {
            var1 += 10;
        }
        else if (incommingByte == 'p')
        {
            Serial.print(var1);
            Serial.print('\n');
        }
        else if (incommingByte == 'u')
        {
            if (time0 - millis() > 33)
            {
                unsigned int usec = sonar1.ping();
                sonar1Reading = usec / US_ROUNDTRIP_CM;
                time0 = millis();
            }
            Serial.print(sonar1Reading); // centimeters
            Serial.print('\n');
        }
    }
}

void establishContact()
{
    while (Serial.available() <= 0)
    {
        Serial.print("R");  // Send ready flag
        delay(300);
    }
    
    Serial.flush();
    delay(10);
}