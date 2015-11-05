
/**
 *  @file SerialBox.ino
 *  
 *  Self Driving Buggy sensor board drivers and serial communication
 *  
 *  @author Ben Warwick
 *  @author Nat Jeffries
 *  Add yourselves to authors field upon contribution!
 *  
 *  In order to run this code you need the following libraries:
 *  https://github.com/ivanseidel/DueTimer
 *  Wire.h library (built-in)
 *  /ben_projects/Self-Driving\ Buggy\ Rev.\ 6/board/test_serial.py
 *  
 */

/* ----- Place includes here ----- */

/* ================================================== *
 *                  Global constants                  *
 * ================================================== */


/* -------------- Command IDs start ----------------- */
/*                                                    */
/*                                                    */
/* --------------- Command IDs end ------------------ */

/* -------------- Serial Globals start -------------- */
/*                                                    */
const int baud = 9600;
const int node = 2;
/*                                                    */
/* --------------- Serial Globals end --------------- */


/* --------------- Auto Globals start --------------- */
/*                                                    */
/*                                                    */
/* ---------------- Auto Globals end ---------------- */

/* ================================================== *
 *                       Setup                        *
 * ================================================== */

void handshake()
{
    Serial.print("R");  // Send ready flag
    while (Serial.available() <= 0) {  }
    
    Serial.flush();
}

void setup()
{
    Packet.begin(baud, node);
    
    /* ---------------- Auto Setup start ---------------- */
    /*                                                    */
    /*                                                    */
    /* ----------------- Auto Setup end ----------------- */
    
    handshake();
}

/* ================================================== *
 *                  Loop and Serial                   *
 * ================================================== */

void loop()
{
    
}

void to_hex(float input, uint8_t *array, int start)
{
    byte* bytearray = (byte*) &input;
    short float_length = 4;
    start *= float_length;
    
    for (int index = float_length - 1; index >= 0; index--) {
        array[((float_length - 1) - index) + start] = bytearray[index];
    }
}

/*
 SerialEvent occurs whenever a new data comes in the
 hardware serial RX.  This routine is run between each
 time loop() runs, so using delay inside loop can delay
 response.  Multiple bytes of data may be available.
 */
void serialEvent()
{
    /* ---------------- Read Serial ----------------- */
    int result = Packet.readSerialData();
    // if result == 0, misformed packet, don't do anything
    if (result == 1)
    {
        command_id = Packet.getCommandID();
        payload = Packet.getPayload();
        
        while (Serial.read() > 0) {  }
        Serial.flush();
    }
    else if (result == 2)
    {
        /* ----------------- Auto Loop start ---------------- */
        /*                                                    */
        /*                                                    */
        /* ------------------ Auto Loop end ----------------- */
    }
}
