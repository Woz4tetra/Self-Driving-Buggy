//
//  Camera.h
//  Test-OpenCV-iOS
//
//  Created by Benjamin Warwick on 8/10/15.
//  Copyright (c) 2015 The Ban Hammer. All rights reserved.
//

#import <Foundation/Foundation.h>

#import <opencv2/videoio/cap_ios.h>

@interface Camera : NSObject
{
    CvVideoCamera* videoCamera;
}

- (void) initCameraWithView: (UIImageView *) imageView;

@property (nonatomic, retain) CvVideoCamera* camera;

@end