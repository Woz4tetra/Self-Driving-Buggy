//
//  Packet.h
//  NewSerialTest
//
//  Created by Benjamin Warwick on 11/18/15.
//
//

#ifndef Packet_h
#define Packet_h

typedef struct packet_node_header packet_node;
struct packet_node_header {
    uint8_t data;
    packet_node* next;
};

typedef struct packet_header* packet_t;
struct packet_header {
    packet_node* start;
    packet_node* end;
    unsigned int size;
};

packet_t packet_new();
void packet_free(packet_t packet);

bool packet_empty(packet_t packet);
unsigned int packet_size(packet_t packet);

void enq(packet_t packet, uint8_t new_data);
uint8_t deq(packet_t packet);

void packet_print(packet_t packet);

#endif /* Packet_h */