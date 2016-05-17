#!/usr/bin/env python

from dbus.mainloop.glib import DBusGMainLoop
import gobject
import argparse
import logging
import sys
import os

# our own packages
sys.path.insert(1, os.path.join(os.path.dirname(__file__), '../ext/velib_python'))
from dbusdummyservice import DbusDummyService

# Argument parsing
parser = argparse.ArgumentParser(
	description='dummy dbus service'
)

parser.add_argument("-n", "--name", help="the D-Bus service you want me to claim",
																				type=str, default="com.victronenergy.tank.tty40")

parser.add_argument("-i", "--instance", help="instance", type=int, default=300)

args = parser.parse_args()

# Init logging
logging.basicConfig(level=logging.DEBUG)
logging.info(__file__ + " is starting up, use -h argument to see optional arguments")

# Have a mainloop, so we can send/receive asynchronous calls to and from dbus
DBusGMainLoop(set_as_default=True)

pvac_output = DbusDummyService(
	servicename=args.name,
	productname='Tank sensor',
	deviceinstance=args.instance,
	paths={
		'/Level': {'initial': 60, 'update': 0},
		'/FluidType': {'initial': 1, 'update': 0},
		'/Capacity': {'initial': 200, 'update': 0},
		'/Remaining': {'initial': 40, 'update': 0}})

print 'Connected to dbus, and switching over to gobject.MainLoop() (= event based)'
mainloop = gobject.MainLoop()
mainloop.run()
