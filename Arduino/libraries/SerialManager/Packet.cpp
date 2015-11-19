//
//  Packet.cpp
//  NewSerialTest
//
//  Created by Benjamin Warwick on 11/18/15.
//
//

#include "Arduino.h"
#include "Packet.h"

packet_t packet_new()
{
    packet_t new_packet = new struct packet_header;
    new_packet->start = new struct packet_node_header;
    new_packet->end = new_packet->start;
    new_packet->size = 0;
    
    return new_packet;
}

bool packet_empty(packet_t packet) {
    return packet->start == packet->end;
}

unsigned int packet_size(packet_t packet) {
    return packet->size;
}

void enq(packet_t packet, char new_data)
{
    // the end of the queue is at end   
    packet->end->data = new_data;
    
    packet->end->next = new struct packet_node_header; // end is dummy node
    
    packet->end = packet->end->next;
    
    packet->size += 1;
}

char deq(packet_t packet)
{
    // the beginning of the queue is at start
    if (!packet_empty(packet))
    {
        char deqd = packet->start->data;
        
        packet->start = packet->start->next;
        
        packet->size -= 1;
        
        return deqd;
    }
    else {
        return '\0';
    }
}

void packet_free(packet_t packet)
{
    for (packet_node* node = packet->start; node != packet->end; node = node->next) {
        free(node);
    }
    free(packet);
}

void packet_print(packet_t packet)
{
    if (!packet_empty(packet))
    {
        for (packet_node* node = packet->start; node != packet->end; node = node->next) {
            Serial.print((char)node->data); Serial.print('\t');
        }
        Serial.println();
    }
}

