/* -------------------------------------------------- */
/*                      Setup                         */
/* -------------------------------------------------- */

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
    if (Serial.available() > 0)
    {
        char incommingByte = Serial.read();
        
        if (incommingByte == '') {
            
        }
    }
}

/* -------------------------------------------------- */
/*                  Serial Handshake                  */
/* -------------------------------------------------- */


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