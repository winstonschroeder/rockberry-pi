#!/usr/bin/env python3

""" rockberry-pi is the main application for handling MIDI presets with a raspberry pi """

import logging
import mididevice as midi

class RockberryPi(object):
	def __init__(self):
		self.midi_server = midi.MIDIServer('rockberry-pi')
	
	def start_webui(self):
		pass
	

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	logging.info('starting %s', __name__)
	rbpi = RockberryPi()
	res = rbpi.midi_server.get_midi_devices()
	