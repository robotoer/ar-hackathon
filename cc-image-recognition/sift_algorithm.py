import cv2
import numpy as np

img_path = "/Users/kevinlaube/ar-hackathon/cc-image-recognition/training-images/C/2/2-0.jpg"

img = cv2.imread(img_path)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

sift = cv2.SIFT()
kp, des = sift.detectAndCompute(gray,None)

print kp
print des 

img=cv2.drawKeypoints(gray,kp)

cv2.imwrite('sift_keypoints.jpg',img)