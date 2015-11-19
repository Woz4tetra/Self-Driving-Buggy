//
//  MyGPS.hpp
//  NewSerialTest
//
//  Created by Benjamin Warwick on 11/18/15.
//
//

#include <Adafruit_GPS.h>

#ifndef MyGPS_h
#define MyGPS_h

typedef struct gps_data_header *gps_data;
struct gps_data_header {
    float* data;
    char* quality;
};

void gps_setup();
gps_data get_gps();

#endif /* MyGPS_h */
