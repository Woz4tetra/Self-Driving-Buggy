/*
 LiquidCrystal Library - Hello World
 
 Demonstrates the use a 16x2 LCD display.  The LiquidCrystal
 library works with all LCD displays that are compatible with the 
 Hitachi HD44780 driver. There are many of them out there, and you
 can usually tell them by the 16-pin interface.
 
 This sketch prints "Hello World!" to the LCD
 and shows the time.
 
 The circuit:
 * LCD RS pin to digital pin 12
 * LCD Enable pin to digital pin 11
 * LCD D4 pin to digital pin 5
 * LCD D5 pin to digital pin 4
 * LCD D6 pin to digital pin 3
 * LCD D7 pin to digital pin 2
 * LCD R/W pin to ground
 * 10K resistor:
 * ends to +5V and ground
 * wiper to LCD VO pin (pin 3)
 
 Library originally added 18 Apr 2008
 by David A. Mellis
 library modified 5 Jul 2009
 by Limor Fried (http://www.ladyada.net)
 example added 9 Jul 2009
 by Tom Igoe
 modified 22 Nov 2010
 by Tom Igoe
 
 This example code is in the public domain.
 
 http://www.arduino.cc/en/Tutorial/LiquidCrystal
 */

// include the library code:
#include <LiquidCrystal.h>

int BUTTON_onoff = 0;
bool BUTTON_onoff_state = 0;
bool BUTTON_onoff_lastValue = 0;

int counter = 0;

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 7, 6, 5, 4, 3);

void setup() {
    //    Serial.begin(115200);
    
    // set up the LCD's number of columns and rows: 
    pinMode(BUTTON_onoff, INPUT);
    pinMode(1, OUTPUT);
    pinMode(2, OUTPUT);
    
    lcd.begin(16, 2);
    // Print a message to the LCD.
    lcd.print("GOTTA GO FAST");
}

void loop() {
    // set the cursor to column 0, line 1
    // (note: line 1 is the second row, since counting begins with 0):
    
    BUTTON_onoff_state = digitalRead(BUTTON_onoff);
    
    //    if (BUTTON_onoff_state != BUTTON_onoff_lastValue)
    //    {
    //        if (BUTTON_onoff_state == false) { // true makes event happen on button release
    //            counter++;
    //        }
    //        BUTTON_onoff_lastValue = BUTTON_onoff_state;
    //    }
    if (BUTTON_onoff_state == 0) {
        counter++;
    }
    
    lcd.setCursor(0, 1);
    // print the number of seconds since reset:
    //lcd.print(millis()/100);
    lcd.print(counter);
}