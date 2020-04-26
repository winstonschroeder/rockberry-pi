#!/usr/bin/env python3

""" rockberry-pi is the main application for handling MIDI presets with a raspberry pi """

import logging, alsaseq, alsamidi, subprocess, collections

_aseqclient='rockberry-pi'
_raveloxmidi_in_port = [16,0]
_raveloxmidi_out_port = [17,0]

def aconnect_list():
	acon = subprocess.Popen("aconnect -l", shell=True, stdout=subprocess.PIPE).stdout.read()
	

def aseqdump_list():
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

def amidi_list():
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

def create_alsaseq_client(clientname=_aseqclient):
	logging.debug('creating alsaseq client: {}'.format(clientname))
	alsaseq.client(clientname,1,1,True)
	alsaseq.start()

def connect_input_devices(inputdevices):
	## FIXME: if alsaseq client has multiple inputs or outputs, count is input 1 = 0, input 2 = 1, [...], output 1 = inputn+1
	##				update connectfrom accordingly
	for dev in inputdevices:
		alsaseq.connectfrom(0, dev[0], dev[1])
		
def connect_output_devices(outputdevices):
	## FIXME: if alsaseq client has multiple inputs or outputs, count is input 1 = 0, input 2 = 1, [...], output 1 = inputn+1
	##				update connectto accordingly
	for dev in outputdevices:
		alsaseq.connectto(1, dev[0], dev[1])

def _run_once(event):
	logging.debug('sending event to output: {}'.format(event))
	alsaseq.output(event)

def run():
	try:
		while(True):
			if (alsaseq.inputpending()):
				_run_once(alsaseq.input())
	except KeyboardInterrupt:
		alsaseq.stop()
		logging.info('keyboard interrupt stopped {}'.format(__name__))

def main():
	logging.basicConfig(level=logging.DEBUG)
	logging.info('starting %s', __name__)
	print(aseqdump_list())
	print(amidi_list())
	inputdevices = [_raveloxmidi_in_port]
	outputdevices = [_raveloxmidi_out_port]
	create_alsaseq_client()
	connect_input_devices(inputdevices)
	connect_output_devices(outputdevices)
	
	print(alsaseq.status())
	

if __name__ == "__main__":
	main()
	run()
