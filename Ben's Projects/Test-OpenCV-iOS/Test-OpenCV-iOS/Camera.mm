//
//  Camera.m
//  Test-OpenCV-iOS
//
//  Created by Benjamin Warwick on 8/10/15.
//  Copyright (c) 2015 The Ban Hammer. All rights reserved.
//

#import "Camera.h"


@implementation Camera

- (void) initCameraWithView: (UIImageView *) imageView
{
    self.camera = [[CvVideoCamera alloc] initWithParentView:imageView];
    self.camera.defaultAVCaptureDevicePosition = AVCaptureDevicePositionFront;
    self.camera.defaultAVCaptureSessionPreset = AVCaptureSessionPreset352x288;
    self.camera.defaultAVCaptureVideoOrientation = AVCaptureVideoOrientationPortrait;
    self.camera.defaultFPS = 30;
    self.camera.grayscaleMode = NO;
}

@end
