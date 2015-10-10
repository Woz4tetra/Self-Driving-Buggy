
//#define DOUBLE_MODE
#define FLOAT_MODE

#ifdef DOUBLE_MODE
const int length = 8;

#endif

#ifdef FLOAT_MODE
const int length = 4;

#endif

#ifdef DOUBLE_MODE
double number = 0;
double numbers[4];

#endif

#ifdef FLOAT_MODE
float number = 0;
float numbers[4] = {4026.7927, 7956.8672, 0.11, 0.05};

#endif

uint8_t hex_array[length];

#ifdef DOUBLE_MODE
void to_hex(double input, uint8_t *array, int length, int start);
#endif

#ifdef FLOAT_MODE
void to_hex(float input, uint8_t *array, int length, int start);
#endif

void float_array()
{
    for (int numbers_index = 0; numbers_index < 4; numbers_index++) {
        to_hex(numbers[numbers_index], hex_array, length, numbers_index * 4);
    }
    
    for (int array_index = 0; array_index < length; array_index++) {
        if (hex_array[array_index] < 0x10) {
            Serial.print("0");
        }
        Serial.print(hex_array[array_index], HEX);
    }
    Serial.println();
}

void single_float()
{
    to_hex(number, hex_array, length, 0);
    for (int index = 0; index < length; index++) {
        if (hex_array[index] < 0x10) {
            Serial.print("0");
        }
        Serial.print(hex_array[index], HEX);
    }
    Serial.println();
    delay(5);
    number += 1.1;
}

void setup()
{
    Serial.begin(115200);
}

void loop()
{
    if (Serial.available())
    {
        float_array();
    }
}

#ifdef DOUBLE_MODE
void to_hex(double input, uint8_t *array, int length, int start)
#endif

#ifdef FLOAT_MODE
void to_hex(float input, uint8_t *array, int length, int start)
#endif
{
    byte* bytearray = (byte*) &input;
    
    for (int index = length - 1; index >= 0; index--) {
        array[((length - 1) - index) + start] = bytearray[index];
    }
}