void setup() {
    Serial.begin(38400);
    estContactforBensSake();
}

void loop() {
    Serial.println(millis());
}

void estContactforBensSake(){
    while (Serial.available() <= 0){
        Serial.print("R");
        delay(300);
    };
    Serial.flush();
    delay(10);
};