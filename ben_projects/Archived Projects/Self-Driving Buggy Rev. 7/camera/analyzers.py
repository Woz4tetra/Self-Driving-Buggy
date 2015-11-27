
import numpy as np
import cv2

class LineFollower:
    def __init__(self, expected, y_bottom, width, height):
        rho, theta = expected
        self.width, self.height = width, height
        
        self.rho = rho
        self.theta = theta
        self.yBottom = y_bottom
    
    def averageLines(self, lines):
        return lines[0]
    
    def difference(self, expected, actual, y_bottom):
        return 0, 0  # distance difference, theta difference
    
    def update(self, frame, enable_draw=True, tolerance=10):
        frame_lines = cv2.medianBlur(frame, 5)
        frame_lines = cv2.Canny(frame_lines, 1, 100)

        lines = cv2.HoughLines(frame_lines, rho=1, theta=np.pi / 180,
                               threshold=50,
                               min_theta=-70 * np.pi / 180,
                               max_theta=70 * np.pi / 180)

        if enable_draw == True and lines != None:
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
                    frame = np.concatenate((frame, cv2.cvtColor(
                        np.uint8(frame_lines), cv2.COLOR_GRAY2BGR)), axis=0)
        
        if lines != None:
            averaged_line = self.averageLines(lines[:tolerance])  # returns rho, theta
        else:
            averaged_line = None, None
        return frame, self.difference((self.rho, self.theta), averaged_line, self.yBottom)
