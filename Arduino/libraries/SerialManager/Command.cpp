//
//  Command.cpp
//  
//
//  Created by Benjamin Warwick on 11/17/15.
//
//

#include <Arduino.h>
#include "Command.h"

struct command_header {
    uint8_t node;
    uint8_t command_id;
};

command_t command_new(uint8_t node, uint8_t command_id)
{
    command_t new_command = new struct command_header;
    
    new_command->node = node;
    new_command->command_id = command_id;
    
    return new_command;
}

bool command_ids_equal(command_t command, uint8_t command_id) {
    return command->command_id == command_id;
}

int command_parity(command_t command) {
    return command->node ^ command->command_id;
}

void command_toserial(command_t command)
{
    Serial.write(command->node);
    Serial.write('\t');
    Serial.write(command->command_id);
    Serial.write('\t');
    int parity = command_parity(command);
    if (parity <= 0xf) {
        Serial.print("0");
    }
    Serial.print(parity, HEX);
    
    Serial.write('\n');
}
