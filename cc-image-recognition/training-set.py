
import cv2
import numpy as np
import imreclib as rec

training = rec.get_training("train.tsv","train3.jpg",6)

for i in range(0, 6):
    cv2.imshow("image", training[i][1])
    raw_input("")
    cv2.destroyAllWindows()