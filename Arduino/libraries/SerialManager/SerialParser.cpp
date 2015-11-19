//
//  SerialParser.cpp
//  NewSerialTest
//
//  Created by Benjamin Warwick on 11/18/15.
//
//

#include <Arduino.h>
#include "SerialParser.h"

void begin_serial(unsigned int baud) {
    Serial.begin(baud);
}

bool is_hex(char character)
{
    return ('0' <= character && character <= '9') ||
        ('A' <= character && character <= 'F') ||
        ('a' <= character && character <= 'f');
}

char read_serial(unsigned int* payload) // command payloads limited by unsigned int
{
    char incomming_char = '\0';
    packet_t packet = packet_new();
    
    while (Serial.available() > 0 && incomming_char != '\n')
    {
        incomming_char = (char)Serial.read();
        enq(packet, incomming_char);
    }
    
    packet_print(packet);
    
    if (!packet_empty(packet))
    {
        char object_id = deq(packet);
        
        if (packet_size(packet) >= 2 && deq(packet) == '\t')
        {
            int bit_shift = 0;
            char data = '0';
            char calc_parity = object_id;
            unsigned int new_payload = 0;
            
            while (!packet_empty(packet) && data != '\t' && is_hex(data))
            {
                data = deq(packet);
                
                calc_parity ^= data;
                
                new_payload += ((unsigned int)(data)) << (8 * bit_shift); // BE CAREFUL OF OVERFLOW!!
                bit_shift += 1;
            }
            
            if (data == '\t') {
                char parity = deq(packet);
                if (deq(packet) == '\r' && parity == calc_parity) {
                    *payload = new_payload;
                }
            }
        }
        
        packet_free(packet);
        return object_id;
    }
    else {
        packet_free(packet);
        return '\0';
    }
}

