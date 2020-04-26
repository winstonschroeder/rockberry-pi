#!/bin/bash

# sudo apt-get update
# sudo apt-get upgrade
# sudo apt-get -y install git

# sudo apt-get -y install python3-pip

## Disable ipv6
if ! grep -q "net.ipv6.conf.all.disable_ipv6 = 1" "/etc/sysctl.conf"; 
then 
	sudo echo "net.ipv6.conf.all.disable_ipv6 = 1" >> "/etc/sysctl.conf"
fi

sudo sysctl -p

# sudo apt-get -y install autoconf automake 
# sudo apt-get -y install pkgconfig
# sudo apt-get -y install libasound2-dev

# git clone https://github.com/ravelox/pimidi.git
# sudo apt-get -y install libavahi-client-dev
# cd pimidi/raveloxmidi
# sh ./autogen.sh
# ./configure
# make deb
# cd ../..
# cp pimidi/raveloxmidi/build/*.deb .
# rm -rf pimidi

# sudo dpkg -i raveloxmidi*.deb

## create raveloxmidi config file 
### NOTE!!!! raveloxmidi only works properly is snd-virmidi module is loaded
### see https://github.com/ravelox/pimidi/blob/master/FAQ.md for details

sndvirmidisetup="
# automatically start virtual raw midi devices for raveloxmidi
snd-virmidi"
# sudo echo "$sndvirmidisetup" > /etc/modules-load.d/virtual_midi.conf
# sudo modprobe snd-virmidi ## for now just load the module (until next reboot)

rlmidicfg="
network.bind_address=0.0.0.0
#	IP address that raveloxmidi listens on. This can be an IPv4 or IPv6 address.
#	Default is 0.0.0.0 ( meaning all IPv4 interfaces ). IPv6 equivalent is ::
#	This must be set in the configuration file for raveloxmidi to run.
# network.control.port=5004
#	Main RTP MIDI listening port for new connections and shutdowns.
#	Used in the zeroconf definition for the RTP MIDI service.
#	Default is 5004.
# network.data.port=5005
#	Listening port for all other data in the conversation.
#	Default is 5005.
# network.local.port=5006
#	Local listening port for accepting MIDI events.
#	Default is 5006.
# service.ipv4
#	Indicate whether Avahi service should use IPv4 addresses. Default is yes.
# service.ipv6
#	Indicate whether Avahi service should use IPv6 addressed. Default is no.
# network.max_connections
#	Maximum number of incoming connections that can be stored.
#	Default is 8.
service.name = rockberry-pi
#	Name used in the zeroconf definition for the RTP MIDI service.
#	Default is 'raveloxmidi'.
# remote.connect
#	Name of remote service to connect to.
#	The value can be one of two formats:
#		To connect to a Bonjour-advertised service, use the format:
#			remote.connect = service
#		To connect directly to a server/port, use the format:
#			remote.connect = [address]:port
#			A port number must be specified if making a direct connection.
# remote.use_control
#	Indicates whether CK (AppleMIDI Feedback) messages are sent to the a remote connection using the control port.
#	Default is yes
client.name = rockberry-pi
#	Name to use when connecting to remote service. If not defined, service.name will be used.
# network.socket_timeout
#	Polling timeout for the listening sockets.
#	Default is 30 seconds.
# discover.timeout
#	Length of time in seconds to wait for new remote services to be seen. Default is 5 seconds.
run_as_daemon = no
#	Specifies that raveloxmidi should run in the background.
#	Default is yes.
# daemon.pid_file
#	If raveloxmidi is run in the background. The pid for the process is written to this file.
#	Default is raveloxmidi.pid.
# logging.enabled=yes
#	Set to yes to write output to a log file. Set to no to disable.
#	Default is "yes".
# logging.log_file=/var/log/rtpmidi.log
#	Name of file to write logging to.
#	Default is stderr.
# logging.log_level=info
#	Threshold for log events. Acceptable values are debug,info,normal,warning and error.
#	Default is normal.
# security.check
#	If set to yes, it is not possible to write the daemon pid to a file with executable permissions.
#	Default is yes.
# inbound_midi
#       Name of file to write inbound MIDI events to. This file is governed by the security check option.
#       Default is /dev/sequencer
# file_mode
#       File permissions on the inbound_midi file if it needs to be created. Specify as Unix octal permissions. 
#	Default is 0640.
# sync.interval
#	Interval in seconds between SYNC commands for timing purposes. Default is 10s.
alsa.output_device=hw0,0,0
## Note! outputdevice should be first virtual device which can be determined with amidi -l
#	Name of the rawmidi ALSA device to send MIDI events to.
alsa.input_device=hw0,1,0
#	Name of the rawmidi ALSA device to read MIDI events from.
# alsa.input_buffer_size
#	Size of the buffer to use for reading data from  the  input  device.
#	Default is 4096. Maximum is 65535.

"

# echo "$rlmidicfg" > raveloxmidi

## Create raveloxmidi service
rlmidisrvc="[Unit]
Description=RTP Midi Protocoll implementation by raveloxmidi.
After=network.target

[Service]
ExecStart=/usr/local/bin/raveloxmidi -d -c /etc/raveloxmidi
StandardOutput=inherit
StandardError=inherit
Restart=always
User=pi

[Install]
WantedBy=multi-user.target

"

# echo "$rlmidisrvc" > raveloxmidi.service
# sudo mv raveloxmidi.service /etc/systemd/system/
# sudo systemctl enable raveloxmidi.service
# sudo systemctl start raveloxmidi.service

# sudo pip3 install Flask
# sudo pip3 install wifi
# sudo pip3 install python-dotenv

## alsaseq is working for connecting virtual midi devices (raveloxmidi) and editing stream inbetween
# sudo pip3 install alsaseq

## reminder to myself: remind me to remove pymidi if it doesn't work
# sudo pip3 install pymidi

## install dnssd = domain name service service discovery
## reminder to myself: 
# sudo pip3 install zeroconf
