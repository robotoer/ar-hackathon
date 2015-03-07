#!/usr/bin/env python

"""
A flask webapp that does nothing but receive image attachements and returns
card suit/rank.

Usage:
python card-rec-server.py <training image file> <training labels file>

API:

  POST http://127.0.0.1:5000/ Attempts to post a file. The request must be
sent with a enctype of multipart/form-data and the file must be included as
form-data keyed as `image`. The server will look for a card in the center of
the image, and return a json doc with fields for 'suit' and 'rank' if it finds
one. If no card is found, these fields will not be present.

"""


import sys

import cv2
from flask import abort, Flask, jsonify, request
import numpy as np


app = Flask(__name__)

training = None


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


def find_closest_card(training, img):
    if img is None:
        return ["*", "*"]
    features1 = preprocess(img)
    features2 = cv2.flip(cv2.transpose(features1), 1)
    return sorted(
        training.values(),
        key = lambda x: min(imgdiff(x[1], features1), imgdiff(x[1], features2)))[0][0]


# Gets the sign of the 3D cross product's z direction for points in 2D space.
def cross_sign(ref_point, pivot, point):
    a = list(ref_point[0])
    b = list(pivot[0])
    return (a[0] - b[0]) * (point[1] - b[1]) - (a[1] - b[1]) * (point[0] - b[0]) >= 0


# Tests to see if the given point is internal to the hull created by the contours.
def is_internal(point, contour):
    c1 = cross_sign(list(contour)[0], list(contour)[1], point)
    c2 = cross_sign(list(contour)[1], list(contour)[2], point)
    c3 = cross_sign(list(contour)[2], list(contour)[3], point)
    c4 = cross_sign(list(contour)[3], list(contour)[0], point)
    return (c1 and c2 and c3 and c4) or (not c1 and not c2 and not c3 and not c4)

# Gets the card in the center if it exists.
def get_center_card(im, center):
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
        elif is_internal(center, contour):
            approx = rectify(cv2.approxPolyDP(card,0.02*peri,True)[:4])

            h = np.array([ [0,0], [449,0], [449,449], [0,449] ], np.float32)

            transform = cv2.getPerspectiveTransform(approx, h)
            warp = cv2.warpPerspective(im, transform, (450,450))

            return warp

    return None


###############################################################################
# Card Extraction For Training
###############################################################################
def get_cards(im, numcards=4, showcontours=False):
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1,1), 1000)
    flag, thresh = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:numcards]

    for card in contours:
        peri = cv2.arcLength(card, True)

        approx = rectify(cv2.approxPolyDP(card, 0.02*peri, True)[:4])

        h = np.array([ [0,0], [449,0], [449,449], [0,449] ], np.float32)

        transform = cv2.getPerspectiveTransform(approx, h)
        warp = cv2.warpPerspective(im, transform, (450,450))

        yield warp


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
            training[i] = (labels[i], preprocess(c))

    print "Done training"
    return training


@app.route('/', methods=['POST'])
def process_image():
    if training is not None:
        try:
            image_file = request.files['image']
        except KeyError:
            abort(400)
        img_str = image_file.read()
        nparr = np.fromstring(img_str, np.uint8)
        im = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)

        width = im.shape[0]
        height = im.shape[1]

        card = find_closest_card(training, get_center_card(im,(height/2,width/2)))
        if (card == None or card[0] == "*" or card[1] == "*"):
            return jsonify({})
        else:
            return jsonify({"rank": card[0], "suit": card[1]})
    else:
        return jsonify({})


if __name__ == '__main__':
    if len(sys.argv) == 3:
        training_image_filename = sys.argv[1]
        training_labels_filename = sys.argv[2]
        num_training_cards = 56

        training = get_training(training_labels_filename,training_image_filename,num_training_cards)

        app.run(host='0.0.0.0', debug=True)

    else:
        print __doc__

