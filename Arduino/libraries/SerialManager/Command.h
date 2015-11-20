//
//  Command.h
//  
//
//  Created by Benjamin Warwick on 11/17/15.
//
//

#ifndef Command_h
#define Command_h

#include <Arduino.h>

typedef struct command_header *command_t;
typedef void command_fn(uint64_t* input);

bool is_command(command_t command);
command_t command_new(uint8_t node, uint8_t command_id);

bool command_ids_equal(command_t command, uint8_t command_id);

void* command_call(command_t command, uint8_t* input);

int command_parity(command_t command);
void command_toserial(command_t command);

#endif /* Command_h */
