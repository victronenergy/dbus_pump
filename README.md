dbus_pump
==============

Python script taking care of pump start/stop based on tank level. To be used on the Color Control GX.

The CCGX internal relay can be used to start a pump using its internal relay.

### Debugging and development on a pc

First you need to start:
  * localsettings: https://github.com/victronenergy/localsettings
	* dbus-systemcalc-py: https://github.com/victronenergy/dbus-systemcalc-py/

Then, in another terminal, run the dummy tank sensor by starting ./test/dummytank.py.

And then in a last terminal you can run the project: dbus_pump.py
