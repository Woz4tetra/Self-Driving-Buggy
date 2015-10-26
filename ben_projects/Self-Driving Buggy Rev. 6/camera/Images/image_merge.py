import cv2
import os

project_dir = os.path.dirname(os.path.realpath(__file__)) + "/"


images = []
for file_name in os.listdir(project_dir):
    if file_name.rfind(".png") != -1:
        images.append((file_name, cv2.imread(project_dir + file_name)))

for file_name, image in images:
    image = image[0:175]
    cv2.imwrite(file_name, image)
