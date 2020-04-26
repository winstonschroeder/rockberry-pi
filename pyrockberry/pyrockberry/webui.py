#!/usr/bin/env python3

""" Web user interface for controlling Foot Pi from tablets and/or computers. """

from flask import Flask
from flask import render_template

app = Flask(__name__)


def default_template(content):
	res = render_template('header.html')	
	res += render_template('menu.html')	
	res += content
	res += render_template('footer.html')
	return res

@app.route('/')
def index():
	return default_template(render_template('content.html', title="Test title", content="blablabla"))

app.run(debug=True, host='0.0.0.0', port=80) 