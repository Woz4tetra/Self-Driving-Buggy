
/* -------------------------------------------------- */
/*                      Setup                         */
/* -------------------------------------------------- */

int var1 = 0;

void setup()
{
    Serial.begin(38400);
    
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