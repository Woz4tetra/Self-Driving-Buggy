
void setup()
{
    Serial.begin(115200);
    Serial.println("Ready!");
}

void loop()
{
    if (Serial.available() > 0) {
        Serial.print((char)Serial.read());
    }
}

