//
//  Command.cpp
//  
//
//  Created by Benjamin Warwick on 11/17/15.
//
//

#include <Arduino.h>
#include "Command.h"

typedef struct command_header *command_t;
typedef void* command_fn(uint8_t* input);

struct command_header {
    int node;
    int command_id;
    int command_len;
    command_fn* do_something;
};

bool is_command(command_t command)
{
    if (command == NULL) return false;
    if (command->node <= 0 || command->node > 0xff) return false;
    if (command->command_len <= 0 || command->command_len > 0xff) return false;
    if (command->command_id < 0 || command->command_id > 0xff) return false;
    
    if (command->do_something == NULL) {
        return false;
    }
    
    return true;
}

command_t command_new(int node, int command_id, int command_len,
                      command_fn* input_command_fn)
{
    command_t new_command = new struct command_header;
    if (new_command == NULL)
    {
        Serial.println("allocation failed");
        abort();
    }
    
    new_command->node = node;
    new_command->command_id = command_id;
    new_command->command_len = command_len;
    new_command->do_something = input_command_fn;
    
    return new_command;
}

bool command_ids_equal(command_t command, int command_id)
{
    return command->command_id == command_id;
}

void* command_call(command_t command, uint8_t* input)
{
    return (*(command->do_something))(input);
}

int command_parity(command_t command)
{
    return command->node ^ command->command_id;
}

void command_toserial(command_t command)
{
    Serial.print(command->node, HEX);
    Serial.print('\t');
    Serial.print(command->command_id, HEX);
    Serial.print('\t');
    Serial.println(command_parity(command), HEX);
}
