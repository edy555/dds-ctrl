#!/usr/bin/python
# dds control python script
#
# pip install pylibftdi
# refer /Library/Python/2.6/site-packages/pylibftdi

import time
from optparse import OptionParser
from pylibftdi import BitBangDevice
from dds import AD9859, BitBangInterface

pins1 = dict(cs=2, sdio=0, sclk=4, ioupdate=5)
pins2 = dict(cs=1, sdio=7, sclk=4, ioupdate=6)

#conf1 = dict(pins=pins1, fclk=400e6, refclk_multiplier=10, vco_range=1)
#conf2 = dict(pins=pins2, fclk=400e6, refclk_multiplier=10, vco_range=1)
#conf2 = dict(pins=pins2, fclk=440e6, refclk_multiplier=11, vco_range=1)

conf1 = dict(pins=pins1, fclk=720e6, refclk_multiplier=18, vco_range=1)
conf2 = dict(pins=pins2, fclk=760e6, refclk_multiplier=19, vco_range=1)
#conf1 = dict(pins=pins1, fclk=520e6, refclk_multiplier=13, vco_range=1)
#conf2 = dict(pins=pins2, fclk=560e6, refclk_multiplier=14, vco_range=1)

class vna:

	def __init__(self, dev):
		dev.baudrate = 115200
		bb = BitBangInterface(dev)
		self.dds1 = AD9859(bb, conf1)
		self.dds2 = AD9859(bb, conf2)
		self.delta = 5000
		self.bitbang = bb
		
	def reset(self):
		self.dds1.reset()
		self.dds2.reset()
		self.bitbang.flush()
		self.dds1.setup()
		self.dds2.setup()
		self.bitbang.flush()

	def set_frequency(self, freq):
		self.dds1.set_frequency(freq)
		self.dds2.set_frequency(freq + self.delta)
		self.dds1.ioupdate()
		self.dds2.ioupdate()

	def set_delta(self, delta):
		self.delta = delta
		
if __name__ == '__main__':
	usage = "usage: %prog [options] [freq(Hz)]"
	parser = OptionParser(usage=usage)
	parser.add_option("-v", "--verbose",
					  action="store_true", dest="verbose", default=False,
					  help="make lots of messages [default]")
	(options, args) = parser.parse_args()

	freq = 10e6
	delta = 5000
	if len(args) >= 1:
		freq = float(args[0])
	if len(args) >= 2:
		delta = float(args[1])

	if options.verbose:
		print "set frequency %gHz" % freq
		
	with BitBangDevice(direction = 0xff) as dev:
		v = vna(dev)
		v.reset()
		v.set_delta(delta)
		v.set_frequency(freq)
