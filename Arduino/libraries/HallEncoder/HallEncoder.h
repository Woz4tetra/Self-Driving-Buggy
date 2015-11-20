//
//  Encoder.h
//  
//
//  Created by Benjamin Warwick on 11/17/15.
//
//

#include <Arduino.h>
#include <DueTimer.h>

#ifndef HallEncoder_h
#define HallEncoder_h

void encoder_setup();
unsigned long* encoder_distance();

#endif /* HallEncoder_h */