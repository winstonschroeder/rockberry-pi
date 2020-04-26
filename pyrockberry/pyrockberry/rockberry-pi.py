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
	logging.debug('starting %s', __name__)
	rbpi = RockberryPi()
	res = rbpi.midi_server.get_midi_devices()
	# try:
		# while (True):
			# pass
	# except KeyboardInterrupt:
		# logging.debug('finished')


""" TODOS:
* Try /proc/asound/ stuff for determining which devices are available
	* /proc/asound/cards contains an overview of kernel devices:		
 0 [VirMIDI        ]: VirMIDI - VirMIDI
                      Virtual MIDI Card 1
 1 [ALSA           ]: bcm2835_alsa - bcm2835 ALSA
                      bcm2835 ALSA
 2 [Interface      ]: USB-Audio - USB MIDI Interface
                      USB MIDI Interface at usb-3f980000.usb-1, full speed
	* /proc/asound/seq/clients contains a list of available sequencer clients:
Client info
  cur  clients : 7
  peak clients : 9
  max  clients : 192

Client   0 : "System" [Kernel]
  Port   0 : "Timer" (Rwe-)
  Port   1 : "Announce" (R-e-)
Client  14 : "Midi Through" [Kernel]
  Port   0 : "Midi Through Port-0" (RWe-)
Client  16 : "Virtual Raw MIDI 0-0" [Kernel]
  Port   0 : "VirMIDI 0-0" (RWeX)
Client  17 : "Virtual Raw MIDI 0-1" [Kernel]
  Port   0 : "VirMIDI 0-1" (RWeX)
Client  18 : "Virtual Raw MIDI 0-2" [Kernel]
  Port   0 : "VirMIDI 0-2" (RWeX)
Client  19 : "Virtual Raw MIDI 0-3" [Kernel]
  Port   0 : "VirMIDI 0-3" (RWeX)
Client  24 : "USB MIDI Interface" [Kernel]
  Port   0 : "USB MIDI Interface MIDI 1" (RWeX)
	
	
"""
	
	