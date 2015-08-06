
/* -------------------------------------------------- */
/*                      Setup                         */
/* -------------------------------------------------- */
void setup()
{
    Serial.begin(38400);
    
    establishContact();
    
    char incommingByte = Serial.read();
    while (incommingByte != '\n')
    {
        Serial.print(incommingByte);
        incommingByte = Serial.read();
    }
}


/* -------------------------------------------------- */
/*                       Loop                         */
/* -------------------------------------------------- */
void loop()
{
    Serial.println(millis(), DEC);
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