"""
A library holding CV code for naively extracting cards from an image and
finding their name.
"""

import cv2
import numpy as np


###############################################################################
# Utility code from
# http://git.io/vGi60A
# Thanks to author of the sudoku example for the wonderful blog posts!
###############################################################################
def rectify(h):
    h = h.reshape((4,2))
    hnew = np.zeros((4,2), dtype = np.float32)

    add = h.sum(1)
    hnew[0] = h[np.argmin(add)]
    hnew[2] = h[np.argmax(add)]

    diff = np.diff(h, axis = 1)
    hnew[1] = h[np.argmin(diff)]
    hnew[3] = h[np.argmax(diff)]

    return hnew


###############################################################################
# Image Matching
###############################################################################
def preprocess(img):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 2 )
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 1)
    return thresh


def imgdiff(img1, img2):
    img1 = cv2.GaussianBlur(img1, (5,5), 5)
    img2 = cv2.GaussianBlur(img2, (5,5), 5)
    diff = cv2.absdiff(img1,img2)
    diff = cv2.GaussianBlur(diff, (5,5), 5)
    flag, diff = cv2.threshold(diff, 200, 255, cv2.THRESH_BINARY)
    return np.sum(diff)


def find_closest_card(training, card):
    if card["image"] is None:
        return {"rank": "*", "suit": "*", "contour": card["contour"]}
    features1 = preprocess(card["image"])
    features2 = cv2.flip(cv2.transpose(features1), 1)
    features3 = cv2.flip(cv2.transpose(features2), 1)
    features4 = cv2.flip(cv2.transpose(features3), 1)
    result = sorted(
        training.values(),
        key = lambda x:
            min(imgdiff(x[1], features1),
                imgdiff(x[1], features2),
                imgdiff(x[1], features3),
                imgdiff(x[1], features4)))[0][0]
    return {"rank": result[0], "suit": result[1], "contour": card["contour"]}


# Gets the sign of the 3D cross product's z direction for points in 2D space.
def cross_sign(a, b, point):
    return (a[0] - b[0]) * (point[1] - b[1]) - (a[1] - b[1]) * (point[0] - b[0]) >= 0


# Tests to see if the given point is internal to the hull created by the contours.
def is_internal(point, contour):
    c1 = cross_sign(contour[0], contour[1], point)
    c2 = cross_sign(contour[1], contour[2], point)
    c3 = cross_sign(contour[2], contour[3], point)
    c4 = cross_sign(contour[3], contour[0], point)
    return (c1 and c2 and c3 and c4) or (not c1 and not c2 and not c3 and not c4)


def cont_to_points(contour):
    return [map(lambda x: int(x), list(coord[0])) for coord in list(contour)]


# Gets the card in the center if it exists.
def get_center_card(im):
    center = (im.shape[1]/2,im.shape[0]/2)

    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray,(1,1),1000)
    flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    contours = contours[:min(len(contours), 10)]

    for card in contours:
        peri = cv2.arcLength(card, True)
        contour = cv2.approxPolyDP(card, 0.02*peri, True)

        if len(list(contour)) < 4:
            continue
        elif is_internal(center, cont_to_points(contour)):
            approx = rectify(contour[:4])

            h = np.array([ [0,0], [449,0], [449,449], [0,449] ], np.float32)

            transform = cv2.getPerspectiveTransform(approx, h)
            warp = cv2.warpPerspective(im, transform, (450,450))

            return {"image": warp, "contour": cont_to_points(contour)}

    return {"image": None, "contour": None}


###############################################################################
# Card Extraction For Training
###############################################################################
def get_cards(im, numcards):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1,1), 1000)
    flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    contours = contours[:min(len(contours), numcards)]

    for card in contours:
        peri = cv2.arcLength(card, True)
        contour = cv2.approxPolyDP(card, 0.02*peri, True)

        if len(list(contour)) < 4:
            yield {"image": None, "contour": cont_to_points(contour)}

        approx = rectify(contour[:4])

        h = np.array([ [0,0], [449,0], [449,449], [0,449] ], np.float32)

        transform = cv2.getPerspectiveTransform(approx, h)
        warp = cv2.warpPerspective(im, transform, (450,450))

        yield {"image": warp, "contour": cont_to_points(contour)}


def get_training(training_labels_filename, training_image_filename, num_training_cards, avoid_cards=None):
    training = {}

    labels = {}
    for line in file(training_labels_filename):
        key, num, suit = line.strip().split()
        labels[int(key)] = (num, suit)

    print "Training"

    im = cv2.imread(training_image_filename)
    for i,c in enumerate(get_cards(im,num_training_cards)):
        if avoid_cards is None or (labels[i][0] not in avoid_cards[0] and labels[i][1] not in avoid_cards[1]):
            training[i] = (labels[i], preprocess(c["image"]))

    print "Done training"
    return training
