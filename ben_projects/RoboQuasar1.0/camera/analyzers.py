# applies houghlines or cascade classfier filters on an input camera frame

import numpy as np
import cv2

class LineFollower:
    def __init__(self, expected, y_bottom, width, height):
        self.centerRho, self.centerTheta = expected
        self.width, self.height = width, height
        self.yBottom = y_bottom

    def isEqual(self, currentTheta, existedTheta, tolerance): 
        '''
        if rho and theta are close enough,
        set these lines as equivalent
        To minimize # of lines on screen
        '''
        if abs(currentTheta - existedTheta) <= tolerance:
            return True
        return False 

    def merge(self, line_set):
        occurance = len(line_set)
        # if occurs more than once, 
        # merge and return a single median (rho, theta)
        if occurance > 1:
            medianTheta = np.median(line_set[0][0])
            medianRho = np.median(line_set[0][1])
            line_set = [occurance, medianRho, medianTheta]
        else: 
            line_set = [occurance, line_set[0][0], line_set[0][1]]
        return line_set

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
            (rho, theta)  = (currentLine[0], currentLine[1])
            if theta > 0: 
                # lines with negative gradient; (y increases downwards in frame)
                leftTheta.append(theta)
                leftRho.append(rho)

            elif theta <= 0:
                rightTheta.append(theta)
                rightRho.append(rho)

        if len(leftRho) != 0:
            avgLeftRho = np.median([leftRho])
            avgLeftTheta = np.median([leftTheta])
        else:
            (avgLeftRho, avgLeftTheta) = (0, 0)

        if len(rightRho) != 0:
            avgRightRho = np.median([rightRho])
            avgRightTheta = np.median([rightTheta])
        else: (avgRightRho, avgRightTheta) = (0, 0)

        self.avgCenterRho = (avgLeftRho + avgRightRho) / 2.0
        self.avgCenterTheta = (avgLeftTheta + avgRightTheta) / 2.0

        return [(avgLeftRho, avgLeftTheta), (avgRightRho, avgRightTheta)]

    def findLineCoord(self, rho, theta):
        # turn avgLines into avgLinesCoord =[(x1, y1), (x2, y2)]
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
    
    def update(self, frame, draw_avg=True, draw_all=True, 
        maxNumLines = 10, tolerance = 0.01):
        frame = frame[90:360,::]
        frame_lines = cv2.medianBlur(frame, 5)
        frame_lines = cv2.Canny(frame_lines, 1, 100)

        lines = cv2.HoughLines(frame_lines, rho=1, theta=np.pi / 180,
                               threshold=100,
                               min_theta=-70 * np.pi / 180,
                               max_theta=70 * np.pi / 180)
        
        i= -1
        linesDrawn = []
        # updating lines, aftermergin similar ones
        if lines != None:
            lines = lines[:,0] # removing one layer of brackets

            '''
            tests on merging and sorting starts here, 
            1) lines are sorted accoriding to their rho value (len)
            (could also sort according to theta)
            2) while loops compare neighboring ones to partition them,
            3) merge func also append multiplicity/ occurance of that partition 
            4) all lines are sorted based on # of occurance

            '''
            lines.sort(axis = 0) 
            print "LINES HERE----", lines
            while i < (len(lines)/2 - 1):
                #  len(lines) doublecounts (rho, theta)
                i += 1
                temp = []
                temp.append(np.array(lines[i]))
                while self.isEqual(lines[i][1], lines[i+1][1], tolerance):
                    # ugly syntax, but it's comparing neighboring theta vals
                    temp.append(lines[i+1])
                    i += 1
                temp = self.merge(temp) 
                linesDrawn.append(temp)

            linesDrawn = np.array(linesDrawn)
            linesDrawn.sort() # sorting based on occurance times
            

        if draw_all == True:
            '''
            draw lines based on their occurance times
            '''
            idx = 0
            while idx < (maxNumLines/2 -1) and idx < len(linesDrawn):
                (rho, theta) = (linesDrawn[-1*idx][1], linesDrawn[-1*idx][2])
                # used -1* here to reverse order; 
                # .sort(reverse=True) somehow doesn't work

                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * -b)
                y1 = int(y0 + 1000 * a)
                x2 = int(x0 - 1000 * -b)
                y2 = int(y0 - 1000 * a)
                
                cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                idx +=1

        if lines is not None:

            averaged_line = self.findAverageLines(lines[:maxNumLines]) 
            (rho1, theta1) = (averaged_line)[0] 
            (rho2, theta2) = (averaged_line)[1]
            (x1, y1, x2, y2) = self.findLineCoord(rho1, theta1)
            (x3, y3, x4, y4) = self.findLineCoord(rho2, theta2)

            # get coordinates of lines before drawing
            if draw_avg:
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.line(frame, (x3, y3), (x4, y4), (0, 255, 0), 2)

        else:
            averaged_line = None, None
        return frame, self.difference((self.centerRho, self.centerTheta
                                       ), averaged_line, self.yBottom)
