#!/usr/bin/env python3

""" deal with all the alsa functions like connecting midi cards etc.. 

Further reading:
* http://www.volkerschatz.com/noise/alsa.html explains the general alsa structure in detail.
* http://www.sabi.co.uk/Notes/linuxSoundALSA.html explains the components of alsa:
		* The hardware card level
		* The kernel module level
		* The /proc/asound kernel interface
		* The /dev/snd device interface
		* The ALSA library level
* https://alsa.opensrc.org/ all info you need!
"""


import logging, alsaseq, alsamidi, subprocess, collections, re
import json
from json import JSONEncoder
import utils

_aseqclient='rockberry-pi'
_raveloxmidi_in_port = [16,0]
_raveloxmidi_out_port = [17,0]


class MIDIServer(object):
	"""
	MIDIServer is a class for reflecting linux alsa midi devices. 
	An alsa midi devices are described as: 
	
	client
	 |
	  - port
	    |
	     - subdevice
			 
	They can be virtual or hardware. 
	"""
	
	devicelist = []

	def _aconnect_list(self):
		""" Executes bash command aconnect -l and return parsed results as list of dictionaries. """
		acon = subprocess.Popen("aconnect -l", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		mdev = None
		for l in acon.split('\n'):
			client = re.search('(?<=client )\d{1,2}', l)
			firstrow = re.search(r'client (\d+): \'([^\']*)\' \[([^\]]*)\]?', l)
			subseqrow = re.search(r' *(\d+) ?\'([^\']+)\'', l)
			if (firstrow):
				parameters = dict(map(lambda x: x.split('='), firstrow.group(3).split(',')))
				if (mdev):
					results.append(mdev)
				mdev = dict(client = firstrow.group(1), name = firstrow.group(2), type = parameters['type'])
				if ('card' in parameters):
					mdev['card'] = parameters['card']
			if (subseqrow):
				if ('subdevices' not in mdev):
					mdev['subdevices'] = []
				mdev['subdevices'].append(dict(id=subseqrow.group(1), name=subseqrow.group(2).strip()))
		if (mdev):
			results.append(mdev)
		return results

	def _aconnect_input(self):
		""" Executes bash command aconnect -i and return parsed results as list of dictionaries. """
		acon = subprocess.Popen("aconnect -i", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		mdev = None
		for l in acon.split('\n'):
			client = re.search('(?<=client )\d{1,2}', l)
			firstrow = re.search(r'client (\d+): \'([^\']*)\' \[([^\]]*)\]?', l)
			subseqrow = re.search(r' *(\d+) ?\'([^\']+)\'', l)
			if (firstrow):
				parameters = dict(map(lambda x: x.split('='), firstrow.group(3).split(',')))
				if (mdev):
					results.append(mdev)
				mdev = dict(client = firstrow.group(1), name = firstrow.group(2), type = parameters['type'])
				if ('card' in parameters):
					mdev['card'] = parameters['card']
			if (subseqrow):
				if ('subdevices' not in mdev):
					mdev['subdevices'] = []
				mdev['subdevices'].append(dict(id=subseqrow.group(1), name=subseqrow.group(2).strip()))
		if (mdev):
			results.append(mdev)
		return results
		
	def _aconnect_output(self):
		""" Executes bash command aconnect -o and return parsed results as list of dictionaries. """
		acon = subprocess.Popen("aconnect -o", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		mdev = None
		for l in acon.split('\n'):
			client = re.search('(?<=client )\d{1,2}', l)
			firstrow = re.search(r'client (\d+): \'([^\']*)\' \[([^\]]*)\]?', l)
			subseqrow = re.search(r' *(\d+) ?\'([^\']+)\'', l)
			if (firstrow):
				parameters = dict(map(lambda x: x.split('='), firstrow.group(3).split(',')))
				if (mdev):
					results.append(mdev)
				mdev = dict(client = firstrow.group(1), name = firstrow.group(2), type = parameters['type'])
				if ('card' in parameters):
					mdev['card'] = parameters['card']
			if (subseqrow):
				if ('subdevices' not in mdev):
					mdev['subdevices'] = []
				mdev['subdevices'].append(dict(id=subseqrow.group(1), name=subseqrow.group(2).strip()))
		if (mdev):
			results.append(mdev)
		return results
		
	def _raveloxmidi_devices(self):
		""" search in running processes for raveloxmidi, get the configuration file used and parse it for midi devices."""
		rlm = subprocess.Popen("ps aux|grep raveloxmidi", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		mdev = None
		for l in rlm.split('\n'):
			rw = re.search(r'.*/usr/local/bin/raveloxmidi [\w\- ]+\-c ([^ ]*)', l)
			if (rw):
				file = rw.group(1)
		if (file):
			rlm = subprocess.Popen("cat {}".format(file), shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
			mdev = dict()
			for l in rlm.split('\n'):
				rw = re.search(r'[^\# ]*alsa.input_device = (.*)', l)
				if (rw):
					mdev['input_device'] = rw.group(1)
				rw = re.search(r'[^\# ]*alsa.output_device = (.*)', l)
				if (rw):
					mdev['output_device'] = rw.group(1)
			return mdev
		return None

	def _create_alsaseq_client(self, clientname=_aseqclient):
		logging.debug('creating alsaseq client: {}'.format(clientname))
		alsaseq.client(clientname,2,3,True)
		alsaseq.start()
		
	def _run_once(event):
		logging.debug('sending event to output: {}'.format(event))
		alsaseq.output(event)
		
	def __init__(self, servername = _aseqclient):
		self._create_alsaseq_client(servername)

	def connect_input_devices(self, inputdevices):
		## FIXME: if alsaseq client has multiple inputs or outputs, count is input 1 = 0, input 2 = 1, [...], output 1 = inputn+1
		##				update connectfrom accordingly
		for dev in inputdevices:
			alsaseq.connectfrom(0, dev[0], dev[1])
			
	def connect_output_devices(self, outputdevices):
		## FIXME: if alsaseq client has multiple inputs or outputs, count is input 1 = 0, input 2 = 1, [...], output 1 = inputn+1
		##				update connectto accordingly
		for dev in outputdevices:
			alsaseq.connectto(1, dev[0], dev[1])
		
	def update_devicelist(self):
		""" Checks for available devices and updates internal list of MIDIDevices. """
		devices = []
		# loop thorugh all asequencer related midi input and output devices and create them again
		lst = self._aconnect_list()
		for i in lst:
			d = MIDIDevice(i['name'], i['client'])
			d.update_subdevices(i['subdevices'])
			devices.append(d)
		utils.update_list(self.devicelist, devices)
				
	def get_midi_devices(self):
		self.update_devicelist()
		return self.devicelist
	
	def run():
		try:
			while(True):
				if (alsaseq.inputpending()):
					_run_once(alsaseq.input())
		except KeyboardInterrupt:
			alsaseq.stop()
			logging.info('keyboard interrupt stopped {}'.format(__name__))

class MIDISubdevice(object):
	def __init__(self, port, portname):
		self.port = port
		self.portname = portname
		self.connections = []
		
	def __eq__(self, other):
		return ((self.port, self.portname, self.connections) == (other.port, other.portname, other.connections))
		
	def __ne__(self, other):
		return ((self.port, self.portname, self.connections) != (other.port, other.portname, other.connections))
		
	def __lt__(self, other):
		return ((self.port, self.portname, self.connections) < (other.port, other.portname, other.connections))
	
	def __le__(self, other):
		return ((self.port, self.portname, self.connections) <= (other.port, other.portname, other.connections))
		
	def __ge__(self, other):
		return ((self.port, self.portname, self.connections) >= (other.port, other.portname, other.connections))
	def __repr__(self):
		return '{}'.format(json.dumps(self.__dict__, sort_keys=True, indent=4))
	def __str__(self):
		return 'Name: {}, port: {}'.format(self.portname, self.port)

class MIDIDevice(object):
	""" MIDIDevice combines all neccessary technical and semantical information on a MIDI Device """
	def __init__(self, name, client):
		self.client = client
		self.name = name
		self.subdevices = []
	
	def __eq__(self, other):
		return ((self.client, self.name, self.input_ports, self.output_ports) == (other.client, other.name, other.input_ports, other.output_ports))
		
	def __ne__(self, other):
		return ((self.client, self.name, self.input_ports, self.output_ports) != (other.client, other.name, other.input_ports, other.output_ports))
		
	def __lt__(self, other):
		return ((self.client, self.name, self.input_ports, self.output_ports) < (other.client, other.name, other.input_ports, other.output_ports))
		
	def __le__(self, other):
		return ((self.client, self.name, self.input_ports, self.output_ports) <= (other.client, other.name, other.input_ports, other.output_ports))
		
	def __ge__(self, other):
		return ((self.client, self.name, self.input_ports, self.output_ports) > (other.client, other.name, other.input_ports, other.output_ports))
				
	def __repr__(self):
		return '{}'.format(json.dumps(self.__dict__, sort_keys=True, indent=4, cls=MidiJSONEncoder))

	def __str__(self):
		return 'Client: {}, Name: {}'.format(self.client, self.name)

	def update_subdevices(self, data):
		subdevices = []
		for i in data:
			sd = MIDISubdevice(i['id'], i['name'])
			subdevices.append(sd)
		utils.update_list(self.subdevices, subdevices)