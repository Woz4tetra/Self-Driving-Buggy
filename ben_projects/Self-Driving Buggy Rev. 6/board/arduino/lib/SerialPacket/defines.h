// Select either ASCII or the normal binary serial packet type

#define SERIAL_ASCII
//#define SERIAL_BINARY

//#define DEBUG_SERIAL


#define DEFAULT_BAUDRATE 115200

#define COMMAND            0x01
#define COMMAND_REPLY      0x02

#define DATA_REQUEST       0x06
#define DATA_BYTE          0x03
#define DATA_INT           0x04

#define DATA_ARRAY_REQUEST 0x07
#define DATA_ARRAY         0x05
#define EXIT               0xff

//// Sensor Types:
//
//#define TEMPERATURE 0x10
//#define HUMIDITY    0x11
//
//#define DISTANCE    0x30
//#define MOTORSTATUS 0x50
//
//// Command IDs
//
//#define STOP_MOTOR_A       0x10
//#define START_MOTOR_A      0x11
//#define SET_SPEED_MOTOR_A  0x12
//#define BRAKE_MOTOR_A      0x13
//
//#define STOP_MOTOR_B       0x15
//#define START_MOTOR_B      0x16
//#define SET_SPEED_MOTOR_B  0x17
//#define BRAKE_MOTOR_B      0x18

// Command IDs
#define FAKE_LED            0x01
#define FAKE_SENSOR_8BIT    0x02
#define FAKE_SENSOR_16BIT   0x03
#define FAKE_GPS            0x04
#define FAKE_MOTOR          0x05

#define LED_13              0x0D