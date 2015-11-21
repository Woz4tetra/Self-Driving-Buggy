//
//  SerialParser.h
//  NewSerialTest
//
//  Created by Benjamin Warwick on 11/18/15.
//
//

#ifndef SerialParser_h
#define SerialParser_h

#include "Packet.h"

void begin_serial(unsigned int baud);
uint8_t read_serial(uint64_t* payload);

#endif /* SerialParser_h */
