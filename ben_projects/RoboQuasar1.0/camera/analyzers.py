# applies houghlines or cascade classfier filters on an input camera frame

import numpy as np
import cv2

# commented out concatenate; 1 screen instd of 2 is shown

class LineFollower:
    def __init__(self, expected, y_bottom, width, height):
        self.centerRho, self.centerTheta = expected
        self.width, self.height = width, height
        self.yBottom = y_bottom
    
    def findAverageLines(self, lines):
        '''
        findAvgLines is not supposed to draw; 
        use update to blur and find lines, 
        then use findAvglines func to return avgline

        '''
        rightRho, rightTheta, leftRho, leftTheta = [], [], [], []

        # Divide lines into left and right groups, accoridng to sign of gradient 
        for currentLine in lines:
            # notes on indexing: currentline has format[[x1, y1]]
            # currentLine = lines[i]
            (rho, theta)  = (currentLine[0][0], currentLine[0][1])

            # if theta == np.pi/2:
            #     #ignore horizontal line to prevent "division by zero" for m
            #     continue 

            if theta > 0: 
                # lines with negative gradient; (y increases downwards in frame) 
                leftTheta.append(theta)
                leftRho.append(rho)
            elif theta <= 0:
                # lines with positive gradient;
                rightTheta.append(theta)
                rightRho.append(rho)

        if len(leftRho) != 0:
            avgLeftRho = np.median([leftRho])
            avgLeftTheta = np.median([leftTheta])
        else: (avgLeftRho, avgLeftTheta) = (0, 0)

        if len(rightRho) != 0:
            avgRightRho = np.median([rightRho])
            avgRightTheta = np.median([rightTheta])
        else: (avgRightRho, avgRightTheta) = (0, 0)



        self.avgCenterRho = (avgLeftRho + avgRightRho) / 2.0
        self.avgCenterTheta = (avgLeftTheta + avgRightTheta) / 2.0

        # Return (rho, theta) for average line; 
        return [(avgLeftRho, avgLeftTheta), (avgRightRho, avgRightTheta)]
        # return [(self.avgCenterRho, self.avgCenterTheta)]
    

    def findLineCoord(self, rho, theta):
        # turn avgLines into avgLinesCoord =[(x1, y1), (x2, y2)]
        # for i in len(self.avgLines):'
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * -b)
        y1 = int(y0 + 1000 * a)
        x2 = int(x0 - 1000 * -b)
        y2 = int(y0 - 1000 * a)
        return (x1, y1, x2, y2)

    
    def difference(self, expected, actual, y_bottom):
        return 0, 0  # distance difference, theta difference
        ''' need to filter out unneeded lines before taking avg'''
    
    def update(self, frame, draw_avg=True, draw_all=True, tolerance=50):
        # crop_frame = frame[]
        frame = frame[90:360,::]
        frame_lines = cv2.medianBlur(frame, 5)
        frame_lines = cv2.Canny(frame_lines, 1, 100)

        lines = cv2.HoughLines(frame_lines, rho=1, theta=np.pi / 180,
                               threshold=50,
                               min_theta=-70 * np.pi / 180,
                               max_theta=70 * np.pi / 180)

        if draw_all == True and lines != None:
            for line_set in lines[:tolerance]:
                for rho, theta in line_set:
                    a = np.cos(theta)
                    b = np.sin(theta)
                    x0 = a * rho
                    y0 = b * rho
                    x1 = int(x0 + 1000 * -b)
                    y1 = int(y0 + 1000 * a)
                    x2 = int(x0 - 1000 * -b)
                    y2 = int(y0 - 1000 * a)
                    
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    ''' Randomly drawing tolerance# of lines on screen'''


                    # frame = np.concatenate((frame, cv2.cvtColor(
                    #     np.uint8(frame_lines), cv2.COLOR_GRAY2BGR)), axis=0)
    
        if lines != None:
            averaged_line = self.findAverageLines(lines[:tolerance]) 
            (rho1, theta1) = (averaged_line)[0] 
            (rho2, theta2) = (averaged_line)[1]
            (x1,y1,x2,y2) = self.findLineCoord(rho1, theta1)
            (x3,y3,x4,y4) = self.findLineCoord(rho2, theta2)

            '''get coordinates of lines before drawing'''
            if draw_avg:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.line(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)

        else:
            averaged_line = None, None
        return frame, self.difference((self.centerRho, self.centerTheta
            ), averaged_line, self.yBottom)
