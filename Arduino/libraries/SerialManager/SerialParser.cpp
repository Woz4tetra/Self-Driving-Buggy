//
//  SerialParser.cpp
//  NewSerialTest
//
//  Created by Benjamin Warwick on 11/18/15.
//
//

#include <Arduino.h>
#include "SerialParser.h"

packet_t packet;

void begin_serial(unsigned int baud)
{
    packet = packet_new();
    Serial.begin(baud);
}

bool is_hex(char character)
{
    return ('0' <= character && character <= '9') ||
        ('A' <= character && character <= 'F') ||
        ('a' <= character && character <= 'f');
}

uint8_t char_to_uint(char character)
{
    if ('0' <= character && character <= '9') {
        return (uint8_t)(character - '0');
    }
    else if ('A' <= character && character <= 'F') {
        return (uint8_t)(character - 'A' + 10);
    }
    else if ('a' <= character && character <= 'f') {
        return (uint8_t)(character - 'a' + 10);
    }
    else {
        return 0;
    }
}

//#define IGNORE_PARITY

uint8_t read_serial(uint64_t* payload) // command payloads limited by unsigned 64 bits
{
    char incomming_char = '\0';
    
    // Extract serial data until there's no more data or a '\n' is found
    // If a '\n' is not found, packet will not be cleared and the program will
    // cycle around to fill it later if more data appears
    while (Serial.available() > 0 && incomming_char != '\n')
    {
        incomming_char = (char)Serial.read();
        
        if (incomming_char != '\n') {
            enq(packet, (uint8_t)incomming_char);
        }
    }
    
    bool is_valid_packet = false;
    uint8_t object_id = 0;
    
    if (incomming_char == '\n' && !packet_empty(packet))
    {
        object_id = deq(packet);// - '0';
//        Serial.print("object_id 0: ");
//        Serial.print(object_id == 1);
//        Serial.print("(");
//        Serial.print(object_id);
//        Serial.println(")");
        
        char next_char = (char)deq(packet);
        
        // if there's more data, that means this packet is a command packet
        // else, the packet is a single character sensor packet
        if (packet_size(packet) >= 2 && next_char == '\t')
        {
            /* ----- Extract payload ----- */
            
            /*
             data comes in as uint8's in reverse order. This is to avoid
             having a length field in the packet or running through the data
             twice (putting it into an array then traversing backwards or
             something. bit_shift increases by one hex digit for each piece of
             data (by 4)
            */
            int bit_shift = 0;
            
            // The dequeue character from the packet to be converted.
            // Initially the ascii for '0'
            uint8_t packet_char = 48; 
            
            // packet_char converted from the ascii version of numbers to
            // unsigned 8-bit integer ('A' -> 10, 'a' -> 10, '9' -> 9, ...)
            uint8_t data = 0;
            
            // The data that will replace the input payload should the packet
            // be correctly formed (parities match)
            uint64_t new_payload = 0;
            
            while (!packet_empty(packet) && is_hex((char)packet_char))
            {
                // extract data from packet in reverse order
                packet_char = deq(packet);
                
                // if '\t', the data stream has ended
                if (packet_char == '\t') {
                    break;
                }
                
                // convert ascii representation of digit to unsigned 8-bit int
                data = char_to_uint(packet_char);
                
                // add new data to new_payload and shift it to the correct
                // decimal place. BE CAREFUL OF OVERFLOW!!!
                // I'm making no checks that the incomming data fits
                // 64 bits.
                if (bit_shift < 16) {
                    new_payload += ((uint64_t)(data)) << (4 * bit_shift);
                }
                
                // move to the next digit
                bit_shift += 1;
            }
            
#ifndef IGNORE_PARITY
            // calculate parity according to the command packet specification
            uint16_t calc_parity = (uint16_t)(object_id ^ new_payload);
            
            // If the last character is '\t' and there are two things left
            // in the packet (two parity digits)
            if (packet_char == '\t')
            {
                uint8_t digit1 = char_to_uint(deq(packet));
                uint8_t digit2 = char_to_uint(deq(packet));
                
                // The parity comes in as two hex characters. Extract them
                // and place them in the correct digit places
                uint16_t parity = (digit1 << 4) + digit2;
                
//                Serial.print("parity: ");
//                Serial.print(parity, HEX);
//                Serial.print(", calc_parity: ");
//                Serial.println(calc_parity, HEX);
//                Serial.println("calc_parity 2: ");
//                Serial.println(object_id);
//                Serial.println((long unsigned int)new_payload);
//                Serial.println((uint16_t)(object_id ^ new_payload));
//                Serial.println(packet_empty(packet));
                
                // if the last character is '\n' and the parity are equal,
                // the packet is valid. Update the payload
                if (packet_empty(packet) && parity == calc_parity)
                {
                    *payload = new_payload;
                    is_valid_packet = true;
                }
            }
#endif /* IGNORE_PARITY */
            
#ifdef IGNORE_PARITY
            *payload = new_payload;
            is_valid_packet = true;
#endif
        }
        // This implies the packet is a sensor packet
        else {
            is_valid_packet = true;
        }
        
//        packet = packet_new();
        
//        Serial.print("is_valid_packet: ");
//        Serial.println(is_valid_packet);
//        
//        Serial.print("object_id: ");
//        Serial.print((char)object_id);
//        Serial.print(" (");
//        Serial.print(object_id);
//        Serial.println(")");
//        
//        Serial.print("payload: ");
//        Serial.println(*(unsigned long*)payload);
    }
    
    if (is_valid_packet) {
        return object_id;
    }
    else {
        return 0;
    }
}

