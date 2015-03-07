#!/usr/bin/env python

"""
A flask webapp that does nothing but receive image attachements and returns
card suit/rank.

API:

  POST http://127.0.0.1:5000/ Attempts to post a file. The request must be 
sent with a enctype of multipart/form-data and the file must be included as
form-data keyed as `image`. The server will look for a card in the center of 
the image, and return a json doc with fields for 'suit' and 'rank' if it finds
one. If no card is found, these fields will not be present.

"""


import cv2
from flask import abort, Flask, jsonify, request
import numpy


app = Flask(__name__)


@app.route('/', methods=['POST'])
def process_image():
    try:
        image_file = request.files['image']
    except KeyError:
        abort(400)
    img_str = image_file.read()
    nparr = numpy.fromstring(img_str, numpy.uint8)
    im = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)

    # TODO: Actual image processing goes here:
    json_response = jsonify({'height': im.shape[1], 'width': im.shape[0]})
    return json_response


if __name__ == '__main__':
    # TODO: Training of images should take place here.
    app.run(host='0.0.0.0', debug=True)

