//
//  Sensor.cpp
//  
//
//  Created by Benjamin Warwick on 11/17/15.
//
//

#include <Arduino.h>
#include "Sensor.h"

struct sensor_header {
    uint8_t node;
    uint8_t sensor_id;
    uint8_t* data;
    uint8_t size;
    sensor_convert_fn* convert;
};

bool is_sensor(sensor_t sensor)
{
    if (sensor == NULL) return false;
    if (sensor->convert == NULL) {
        return false;
    }
    
    // length of sensor->data == sensor->size
    
    return true;
}

// size is number of unsigned 8-bit integers this sensor requires
sensor_t sensor_new(int node, uint8_t sensor_id, uint8_t size,
                    sensor_convert_fn* convert_fn)
//@ensures is_sensor(\result);
{
    sensor_t new_sensor = new struct sensor_header;
    if (new_sensor == NULL)
    {
        Serial.println("allocation failed");
        abort();
    }
    
    new_sensor->node = node;
    new_sensor->sensor_id = sensor_id;
    new_sensor->size = size;
    new_sensor->convert = convert_fn;
    
    new_sensor->data = new uint8_t[size];
    
    if (new_sensor->data == NULL)
    {
        Serial.println("allocation failed");
        abort();
    }
    
    return new_sensor;
}

bool sensor_ids_equal(sensor_t sensor, uint8_t sensor_id)
{
    return sensor->sensor_id == sensor_id;
}

void sensor_update(sensor_t sensor, void* new_data)
{
    (*(sensor->convert))(sensor->data, new_data, sensor->size);
    // !!!size remains unchanged!!!
}

uint16_t sensor_parity(sensor_t sensor)
{
    uint16_t parity = sensor->sensor_id ^ sensor->node;
    
    for (int index = 0; index < sensor->size; index++) {
        parity ^= sensor->data[index];
    }
    
    return parity;
}

void sensor_toserial(sensor_t sensor)
{
    Serial.write(sensor->node);
    Serial.write('\t');
    Serial.write(sensor->sensor_id);
    Serial.write('\t');
    for (int index = 0; index < sensor->size; index++)
    {
        if (sensor->data[index] <= 0xf) {
            Serial.print("0");
        }
        Serial.print(sensor->data[index], HEX);
    }
    Serial.write('\t');
    Serial.print(sensor_parity(sensor), HEX);
    Serial.write('\n');
}

