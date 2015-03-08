import cv2
import numpy as numpy
#from matplotlib import pyplot as plt

img_path = "/Users/kevinlaube/ar-hackathon/cc-image-recognition/training-images/C/2/2-0.jpg"

print("Reading image")
img = cv2.imread(img_path, 0)
print("Finished reading")
surf = cv2.SURF(400)
kp, des = surf.detectAndCompute(img,None)

print len(kp)

img2 = cv2.drawKeypoints(img,kp,None,(255,0,0),4)
#plt.imshow(img2), plt.show()