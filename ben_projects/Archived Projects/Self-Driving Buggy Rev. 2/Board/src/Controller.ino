
#include <Servo.h>
#include <AFMotor.h>
#include <Time.h>

int servoPin = 9;
int motorPin = 4;

int LED_running = 13;
int LED_standby = 12;
int LED_active = 11;

int BUTTON_onoff = 8;
bool BUTTON_onoff_state = 0;
bool BUTTON_onoff_lastValue = 0;

int inactiveTime = now();

unsigned int data = 0;

bool programRunning = true;

Servo steeringServo;
AF_DCMotor motor(motorPin, MOTOR12_64KHZ); // create motor #4, 64KHz pwm

void setup()
{
    Serial.begin(115200);
    steeringServo.attach(servoPin);

    pinMode(LED_running, OUTPUT);
    pinMode(LED_standby, OUTPUT);
    pinMode(LED_active, OUTPUT);

    pinMode(BUTTON_onoff, INPUT);

    digitalWrite(LED_active, LOW);
    digitalWrite(LED_standby, HIGH);
    digitalWrite(LED_running, LOW);

    BUTTON_onoff_lastValue = digitalRead(BUTTON_onoff);
}

void loop()
{
    BUTTON_onoff_state = digitalRead(BUTTON_onoff);

    if (BUTTON_onoff_state != BUTTON_onoff_lastValue)
    {
        if (BUTTON_onoff_state == false) { // true makes event happen on button release
            programRunning = !programRunning;
        }
        BUTTON_onoff_lastValue = BUTTON_onoff_state;
    }
    if (programRunning == true)
    {
        if (Serial.available() > 0)
        {
            digitalWrite(LED_active, LOW);
            digitalWrite(LED_standby, LOW);
            digitalWrite(LED_running, HIGH);

            data = receivedData();

            // ----- data conditionals start -----

            if (data == 0) {
                sendData(get_button(data));
            }
            else if (1 <= data && data <= 180) {
                set_steering(data - 1);
            }
            else if (181 <= data && data <= 381) {
                set_testMotor(data - 181);
            }

            // -----  data conditionals end  -----
            inactiveTime = now();
        }
        else {
            if (now() - inactiveTime >= 2)
            {
                digitalWrite(LED_active, LOW);
                digitalWrite(LED_standby, HIGH);
                digitalWrite(LED_running, LOW);
            }
        }
    }
    else
    {
        digitalWrite(LED_active, HIGH);
        digitalWrite(LED_standby, LOW);
        digitalWrite(LED_running, LOW);
    }
}

unsigned int receivedData()
{
    unsigned char upperData = Serial.read();
    delay(1);
    unsigned char lowerData = Serial.read();
    return upperData * 0x100 + lowerData;
}

void sendData(unsigned int inputData)
{
    //unsigned char lowerByte = inputData % 0x100;
    //unsigned char upperByte = inputData / 0x100;

    //Serial.print(lowerByte);
    //Serial.print(upperByte);

    Serial.write(inputData);
}

void setMotorSpeed(int inputSpeed, AF_DCMotor *motorInstance)
{
    int motorSpeed = map(abs(inputSpeed - 100), 0, 100, 0, 255);
    motorInstance->setSpeed(motorSpeed);
    if (inputSpeed > 100) {
        motorInstance->run(FORWARD);
    }
    else if (inputSpeed == 100) {
        motorInstance->run(BRAKE);
    }
    else {
        motorInstance->run(BACKWARD);
    }
}

// ----- functions start -----

unsigned int get_button(int input)
{
    return LED_running;
}
void set_steering(int input)
{
    steeringServo.write(input);
}
void set_testMotor(int input)
{
    setMotorSpeed(input, &motor);
}

// -----  functions end  -----