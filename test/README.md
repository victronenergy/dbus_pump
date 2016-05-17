dbus_pump test
===================

This test can run on CCGX and PC.
When running on a CCGX the Relay is also tested, on a PC only checks "/State" to know
if the pump is running or not.

Running on a CCGX
--------------------
	./utest.py -v

Running on a PC
---------------
First you need to start:
  * localsettings: https://github.com/victronenergy/localsettings
	* dbus-systemcalc-py: https://github.com/victronenergy/dbus-systemcalc-py/

Then run utest.py

	./utest.py -v
