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
import imreclib as rec


app = Flask(__name__)


training = None


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

        cards = filter(lambda card: card != None and card["suit"] != "*" and card["rank"] != "*",
                       [rec.find_closest_card(training, rec.get_center_card(im))])
        print {"result": cards}
        return jsonify({"result": cards})
    else:
        return jsonify({"result": []})


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        training_image_filename = sys.argv[1]
        training_labels_filename = sys.argv[2]
        num_training_cards = 56

        training = rec.get_training(training_labels_filename,training_image_filename,num_training_cards)

        app.run(host='0.0.0.0', debug=True)

    else:
        print __doc__

