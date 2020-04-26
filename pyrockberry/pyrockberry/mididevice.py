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

"""


import logging, alsaseq, alsamidi, subprocess, collections, re
import json

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
	
	_devicelist = []

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
		
	def _amidi_list(self):
		""" Executes bash command amidi -l and return parsed results as list of dictionaries. """
		ami = subprocess.Popen("amidi -l", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		for l in ami.split('\n'):
			rw = re.search(r'([IO]{1,2}) +(hw:\d,\d,?\d?) +([^\(]*)[\(]?(\d*)(?<= subdevices\))?', l)
			if (rw):
				mdev = dict(direction=rw.group(1), device=rw.group(2), name=rw.group(3))
				if (rw.group(4)!=''):
					mdev['subdevices'] = int(rw.group(4))
				results.append(mdev)
		return results
		
	def _aplaymidi_list(self):
		""" Executes bash command amidi -l and return parsed results as list of dictionaries. """
		apmi = subprocess.Popen("aplaymidi -l", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		for l in apmi.split('\n'):
			rw = re.search(r'(\d+:\d+) +([\w\d\- ]+) {2,}([\w\d\- ]+)', l)
			if (rw):
				mdev = dict(port=rw.group(1), client=rw.group(2), port_name=rw.group(3))
				results.append(mdev)
		return results
		
	def _arecordmidi_list(self):
		""" Executes bash command amidi -l and return parsed results as list of dictionaries. """
		apmi = subprocess.Popen("arecordmidi -l", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		for l in apmi.split('\n'):
			rw = re.search(r'(\d+:\d+) +([\w\d\- ]+) {2,}([\w\d\- ]+)', l)
			if (rw):
				mdev = dict(port=rw.group(1), client=rw.group(2), port_name=rw.group(3))
				results.append(mdev)
		return results
		
	def _aseqdump_list(self):
		""" Executes bash command aseqdump -l and return parsed results as list of dictionaries. """
		ase = subprocess.Popen("aseqdump -l", shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8')
		results = []
		for l in ase.split('\n'):
			rw = re.search(r' *(\d+:\d+) +([\w\d\- ]+) {2,}([\w\d\- ]+)' ,l)
			if (rw):
				mdev = dict(port = rw.group(1), clientname = rw.group(2).strip(), port_name = rw.group(3).strip())
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
		ami = self._amidi_list()
		apmi = self._aplaymidi_list()
		armi = self._arecordmidi_list()
		ase = self._aseqdump_list()
		aco = self._aconnect_list()
		rlm = self._raveloxmidi_devices()
		devices = []
		
		print (json.dumps(apmi, sort_keys=True, indent=4))
		
		i = 0
		for acon in aco:
			## try matching the above results with each other
			for sd in acon['subdevices']:
				sd['port'] = '{}:{}'.format(acon['client'],sd['id'])
				if ('card' in acon):
						for amid in ami:
							if (amid['device'][:6]=='hw:{},{}'.format(acon['card'],sd['id'])):
								sd['amidiinfo'] = amid
								# FIXME: hw assignment doesn't work over sd ID because in case of virtual midi it is always 0
								# use ouput of aplaymidi instead
								# print ('acon hw:{},{}'.format(acon['card'],sd['id']))
								# print (amid['device'][:6])
							for rlmi in rlm.items():
								#print (amid['device'][:6])
								if (rlmi[1][:6]==amid['device'][:6]):
									#print ('found one')
									sd['rtpmidi_usage'] = rlmi[0]
				for aseq in ase:
					if (aseq['port']==sd['port']):
						sd['aseqdumpinfo'] = aseq
				
			## ... and create a list of midi devices
			
		#print(json.dumps(aco, sort_keys=True, indent=4))
		
		# for a in aco:
			# if (a['name'] == 'rockberry-pi'):
				# print (a)
				
		#print (aco[3])

	def get_midi_devices(self):
		self.update_devicelist()
		return self._devicelist
	
	def run():
		try:
			while(True):
				if (alsaseq.inputpending()):
					_run_once(alsaseq.input())
		except KeyboardInterrupt:
			alsaseq.stop()
			logging.info('keyboard interrupt stopped {}'.format(__name__))

class MIDIDevicePort(object):
	def __init__(self, port, portname, clientname):
		self.port = port
		self.portname = portname
		self.clientname = clientname
		self.connections = []

class MIDIDeviceOutputPort(MIDIDevicePort):
	pass

class MIDIDeviceInputPort(MIDIDevicePort):
	pass

class MIDIDevice(object):
	""" MIDIDevice combines all neccessary technical and semantical information on a MIDI Device """
	def __init__(self):
		self.card = ''							## see output of amidi -L
		self.device = ''						## see output of amidi -L
		self.subdevice = ''					## see output of amidi -L
		self.input_ports = []
		self.output_ports = []
	
	def repr(self):
		return 'MIDIDevice: ' + self.name + ' {' + self.port + '}'
		
	def __str__(self):
		return 'MIDIDevice: ' + self.name + ' {' + self.card + '}'