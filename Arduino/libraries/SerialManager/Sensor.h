//
//  Sensor.h
//  
//
//  Created by Benjamin Warwick on 11/17/15.
//
//

#ifndef Sensor_h
#define Sensor_h

#include <Arduino.h>

typedef struct sensor_header *sensor_t;
typedef void sensor_convert_fn(uint8_t* data, void* new_data, const int size);

sensor_t sensor_new(int node, uint8_t sensor_id, uint8_t size,
                    sensor_convert_fn* convert_fn);
bool sensor_ids_equal(sensor_t sensor, uint8_t sensor_id);
void sensor_update(sensor_t sensor, void* new_data);
void sensor_toserial(sensor_t sensor);

#endif /* Sensor_h */
