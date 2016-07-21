#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import dbus
import platform
import random
import time
import calendar
import datetime
import json
import sys
from subprocess import Popen, PIPE, STDOUT
import os


class TestPump(unittest.TestCase):

	def setUp(self):
		self._settingspath = 'com.victronenergy.settings'
		self._tankpath = 'com.victronenergy.tank.tty40'
		self._pumppath = 'com.victronenergy.pump.startstop0'
		self.systemcalcservice = 'com.victronenergy.system'
		self.bus = dbus.SessionBus() if 'DBUS_SESSION_BUS_ADDRESS' in os.environ else dbus.SystemBus()
		self.start_services('pumpstarter')
		self.start_services('tank')
		self.set_value(self._settingspath, '/Settings/Relay/Function', 3)
		self.retriesonerror = 30
		self.set_value(self._settingspath, '/Settings/Pump0/TankService', 'com.victronenergy.tank/300')
		self.set_value(self._tankpath, '/Level', 100)
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 2)
		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 0)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 0)
		self.firstRun = False

	def tearDown(self):
		self.stop_services('tank')
		self.stop_services('pumpstarter')

	def start_services(self, service):
		if service == 'tank':
			self.tankp = Popen([sys.executable, "dummytank.py"], stdout=PIPE, stderr=STDOUT)
			while True:
				line = self.tankp.stdout.readline()
				#print line.rstrip()
				if not line or ":/Level" in line:
					break
		elif service == 'pumpstarter':
			self.pumpp = Popen([sys.executable, "../dbus_pump.py","-r","30"], stdout=PIPE, stderr=STDOUT)
			while True:
				line = self.pumpp.stdout.readline()
				#print line.rstrip()
				if not line or ":vedbus:registered" in line:
					break

	def stop_services(self, service):
		if service == 'tank':
			try:
				self.tankp.kill()
				self.tankp.wait()
			except (AttributeError, OSError):
				pass
		elif 'pumpstarter':
			try:
				self.pumpp.kill()
				self.pumpp.wait()
			except (AttributeError, OSError):
				pass

	def test_auto(self):

		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 50)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 70)
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 0)
		# Start value not reached, pump must continue off
		self.assertEqual(0, self.get_state(5))
		# Start value reached, pump must start
		self.set_value(self._tankpath, '/Level', 49)
		self.assertEqual(1, self.get_state(5))
		# Start value above start value but was previously started
		# must remain on
		self.set_value(self._tankpath, '/Level', 60)
		self.assertEqual(1, self.get_state(5))
		# Stop value reached, pump must stop
		self.set_value(self._tankpath, '/Level', 70)
		self.assertEqual(0, self.get_state(5))

	def test_auto_inverse(self):
		self.set_value(self._tankpath, '/Level', 40)
		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 70)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 50)
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 0)

		# Start value not reached, pump must continue off
		self.assertEqual(0, self.get_state(5))
		# Start value reached, pump must start
		self.set_value(self._tankpath, '/Level', 71)
		self.assertEqual(1, self.get_state(5))
		# Start value above start value but was previously started
		# must remain on
		self.set_value(self._tankpath, '/Level', 60)
		self.assertEqual(1, self.get_state(5))
		# Stop value reached, pump must stop
		self.set_value(self._tankpath, '/Level', 50)
		self.assertEqual(0, self.get_state(5))

	def test_modes(self):
		# Off mode
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 2)
		self.assertEqual(0, self.get_state(5))

		# On mode
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 1)
		self.assertEqual(1, self.get_state(5))

		# Auto mode, pump must continue on
		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 70)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 50)
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 0)
		self.set_value(self._tankpath, '/Level', 71)
		self.assertEqual(1, self.get_state(5))

		# Off mode again
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 2)
		self.assertEqual(0, self.get_state(5))

	def test_retry_mechanism_off(self):

		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 70)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 50)
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 0)
		self.set_value(self._tankpath, '/Level', 71)
		# Pump started
		self.assertEqual(1, self.get_state(5))

		# Stop tank service, pump must continue on during retriesonerror
		self.stop_services('tank')
		self.assertEqual(1, self.get_state(5))
		# Check after half of the retry timeout passed
		time.sleep(self.retriesonerror / 2)
		self.assertEqual(1, self.get_state(5))
		# Retry timeout, pump must stop
		time.sleep(self.retriesonerror / 2)
		self.assertEqual(0, self.get_state(5))
		self.start_services('tank')

	def test_retry_mechanism_off(self):

		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 70)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 50)
		self.set_value(self._settingspath, '/Settings/Pump0/Mode', 0)
		self.set_value(self._tankpath, '/Level', 71)
		# Pump started
		self.assertEqual(1, self.get_state(5))

		# Stop tank service, pump must continue on during retriesonerror
		self.stop_services('tank')
		self.assertEqual(1, self.get_state(5))
		# Check after half of the retry timeout passed
		time.sleep(self.retriesonerror / 2)
		# Start tank service
		self.start_services('tank')
		self.set_value(self._settingspath, '/Settings/Pump0/StartValue', 70)
		self.set_value(self._settingspath, '/Settings/Pump0/StopValue', 50)
		self.set_value(self._tankpath, '/Level', 71)
		self.assertEqual(1, self.get_state(5))
		# Retry time finish, pump must continue on
		time.sleep(self.retriesonerror / 2)
		self.assertEqual(1, self.get_state(5))

	def wait_and_get(self, setting, delay):
		time.sleep(delay)
		return self.get_value(self._pumppath, setting)

	def get_state(self, delay):
		state = self.wait_and_get('/State', delay)
		state_on_systemcalc = self.get_value(self.systemcalcservice, "/Relay/0/State")
		self.assertEqual(state_on_systemcalc, state)
		return state

	def set_value(self, path, setting, value):
		dbusobject = dbus.Interface(self.bus.get_object(path, setting), None)
		dbusobject.SetValue(value)

	def get_value(self, path, setting):
		dbusobject = dbus.Interface(self.bus.get_object(path, setting), None)
		return dbusobject.GetValue()

if __name__ == '__main__':
	unittest.main(exit=True)
