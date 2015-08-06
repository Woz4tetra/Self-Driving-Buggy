
/* -------------------------------------------------- */
/*                      Setup                         */
/* -------------------------------------------------- */
void setup()
{
    Serial.begin(38400);
    
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