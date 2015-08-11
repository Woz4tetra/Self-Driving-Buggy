#include <stdio.h>
#include <time.h>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <unistd.h>
//#include <iostream>

using namespace cv;

int main(int argc, char** argv)
{
    string filename = "Videos/IMG_0582.m4v";
    VideoCapture capture(filename);
    Mat frame;
    clock_t t;
    
    capture.set(CV_CAP_PROP_FRAME_WIDTH, 640);
    capture.set(CV_CAP_PROP_FRAME_HEIGHT, 360);
    
    if( !capture.isOpened() )
        throw "Error when reading steam_avi";
    
    unsigned int microseconds = 8;
    
    namedWindow( "w", 1);
    for( ; ; )
    {
        t = clock();
        capture >> frame;
        if(frame.empty())
            break;
//        imshow("w", frame);
        waitKey(1); // waits to display frame
        t = clock() - t;
        printf("time: %f\n", ((float)t)/CLOCKS_PER_SEC);
    }
    waitKey(0); // key press to close window
                // releases and window destroy are automatic in C++ interface
}
