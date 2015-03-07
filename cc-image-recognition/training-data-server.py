#!/usr/bin/env python

"""
A Flask server to capture image data for training use.
All images sent must be labeled with a number and suit.
Valid identifiers are {S, C, H, D} for suit and {1-13}
for numbers.
"""

import os
import logging

from flask import abort, request, jsonify, Flask

app = Flask(__name__)

@app.route('/', methods=['POST'])
def save_image():
	try:
		image = request.files['image']
	except KeyError:
		abort(400)
	#input = raw_input("Please enter something: ")
	suit, value = ('C', 5)#process_input(input)
	if suit == -1:
		abort(413)

	image_str = image.read()

	dir_path = "training-images/" + suit + "/" + str(value)
	try:
		os.makedirs(dir_path)
		index = 0
	except OSError as err:
		logging.debug(err)
		index = len(os.listdir(dir_path))
		# Do nothing
	file_path = dir_path + "/" + str(value) + "-" + str(index) + ".jpg"
	with open(file_path, 'wb') as f:
		f.write(image_str)

	return jsonify({})

def process_input(input):
	"""
	Resolves user input to a (suit, value) tuple. Suit must
	be in (S, C, H, D) and value must be in (1 - 13).
	"""
	suit_values = set(('S', 'C', 'H', 'D'))
	card_values = set(range(1,14))

	suit = input[0]
	value = int(input[2])

	if (suit not in suit_values or
			value not in card_values):
		return (-1, -1)

	return (suit, value)


if __name__ == '__main__':       
  	app.run(host='0.0.0.0', port=5050, debug=True)
