#!/usr/bin/env python3

""" deal with all the alsa functions like connecting midi cards etc.. """


import logging, alsaseq, alsamidi, subprocess, collections, re

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
		""" Executes bash command aconnect -l and return parsed results as list of MIDIDevice. """
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
				mdev = MIDIDevice()
				mdev.client = firstrow.group(1)
				mdev.name = firstrow.group(2)
				mdev.isvirutal = (parameters['type'] != 'Kernel')
				if ('card' in parameters):
					mdev.card = parameters['card']
			if (subseqrow):
				print(subseqrow.group(1))
		if (mdev):
			results.append(mdev)
		return results
		
	def _amidi_list(self):
		ami = subprocess.Popen("amidi -l", shell=True, stdout=subprocess.PIPE).stdout.read()
		amidilist = []
		head = ami
		ami = ami.replace(b'  ', b'\t')
		while (ami.find(b'\t\t')>0):
			ami = ami.replace(b'\t\t',b'\t')
		header = []
		head = head.split(b'\n')[0]
		ami = ami.split(b'\n')
		for h in head.decode('utf-8').split(' '):
			c = h.lstrip()
			if (len(c)>1):
				header.append(c)
		for ln in ami[1:]:
			cols = ln.decode('utf-8').split('\t')
			if (len(cols) == len(header)):
				amidilist.append( {header[0]:cols[0].lstrip(), header[1]:cols[1].lstrip(), header[2]:cols[2].lstrip(), } )
		return amidilist
		
	def _aseqdump_list(self):
		aseq = subprocess.Popen("aseqdump -l", shell=True, stdout=subprocess.PIPE).stdout.read()
		aseq = aseq.replace(b'  ', b'\t')
		aseqdump = []
		while (aseq.find(b'\t\t')>0):
			aseq = aseq.replace(b'\t\t',b'\t')
		aseq = aseq.split(b'\n')
		header = []
		for h in aseq[0].decode('utf-8').split('\t'):
			header.append(h.lstrip())
		for ln in aseq[1:]:
			cols = ln.decode('utf-8').split('\t')
			if (len(cols) == len(header)):
				aseqdump.append( {header[0]:cols[0].lstrip(), header[1]:cols[1].lstrip(), header[2]:cols[2].lstrip(), } )
		return aseqdump

	def _create_alsaseq_client(self, clientname=_aseqclient):
		logging.debug('creating alsaseq client: {}'.format(clientname))
		alsaseq.client(clientname,1,1,True)
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
		ase = self._aseqdump_list()
		aco = self._aconnect_list()

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

class MIDIDevice(object):
	""" MIDIDevice combines all neccessary technical and semantical information on a MIDI Device """
	def __init__(self):
		self.card = ''							## see output of amidi -L
		self.device = ''						## see output of amidi -L
		self.subdevice = ''					## see output of amidi -L
		self.direction = ''		
		self.name = ''
		self.isvirutal = False
		self.altname = ''
		self.alsaconnectto = []
		self.alsaconnectfrom = []
		self.outboardconnectto = ''
		self.outboardconnectfrom = ''
		self.channel_input_assignments = dict.fromkeys(list(map(lambda x:'ch{:02d}'.format(x), range(1,16))),'')
		self.channel_output_assignments = dict.fromkeys(list(map(lambda x:'ch{:02d}'.format(x), range(1,16))),'')
	
	def repr(self):
		return 'MIDIDevice: ' + self.name + ' {' + self.port + '}'
		
	def __str__(self):
		return 'MIDIDevice: ' + self.name + ' {' + self.card + '}'