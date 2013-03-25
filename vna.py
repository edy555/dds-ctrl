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

conf = [dict(
	     conf1= dict(pins=pins1, fclk=720e6, refclk_multiplier=18, vco_range=1),
	     conf2= dict(pins=pins2, fclk=760e6, refclk_multiplier=19, vco_range=1)),
		dict(
		 conf1= dict(pins=pins1, fclk=520e6, refclk_multiplier=13, vco_range=1),
		 conf2= dict(pins=pins2, fclk=560e6, refclk_multiplier=14, vco_range=1)),
		dict(
		 conf1= dict(pins=pins1, fclk=600e6, refclk_multiplier=15, vco_range=1),
		 conf2= dict(pins=pins2, fclk=640e6, refclk_multiplier=16, vco_range=1))]

class vna:

	def __init__(self, dev):
		dev.baudrate = 115200
		bb = BitBangInterface(dev)
		self.delta = 5000
		self.bitbang = bb
		self.conf = None
		self.force_conf = None
		
	def reset(self):
		conf = self.conf
		self.dds1 = AD9859(self.bitbang, conf["conf1"])
		self.dds2 = AD9859(self.bitbang, conf["conf2"])
		self.dds1.reset()
		self.dds2.reset()
		self.bitbang.flush()
		self.dds1.setup()
		self.dds2.setup()
		self.bitbang.flush()

	def find_conf(self, freq):
		if self.force_conf:
			return conf[self.force_conf-1]
        #if 1380e6 < freq and freq < 1660e6:
		elif 1360e6 < freq and freq < 1760e6:
			return conf[2]
		elif 640e6 < freq and freq < 880e6:
			return conf[1]
		else:
			return conf[0]

	def select_conf(self, sel):
		self.force_conf = sel
	
	def set_frequency(self, freq):
		conf = self.find_conf(freq)
		if conf != self.conf:
			self.conf = conf
			self.reset()
		self.dds1.set_frequency(freq)
		self.dds2.set_frequency(freq + self.delta)
		self.dds1.ioupdate()
		self.dds2.ioupdate()

	def set_delta(self, delta):
		self.delta = delta
		
	def select_signal(self, thru):
		if thru:
			self.bitbang.set_bit(3, 1)
		else:
			self.bitbang.set_bit(3, 0)
		
if __name__ == '__main__':
	usage = "usage: %prog [options] [freq(Hz)]"
	parser = OptionParser(usage=usage)
	parser.add_option("-v", "--verbose",
					  action="store_true", dest="verbose", default=False,
					  help="make lots of messages [default]")
	parser.add_option("-t", action="store_true", dest="thru", default=False,
					  help="select thrugh signal(s21) [default: %default]")
	parser.add_option("-c", metavar="CONF", dest="conf", type="int", default=0,
					  help="select dds configuration [default: 0 (auto)]")
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
		#v.reset()
		v.select_signal(options.thru)
		v.select_conf(options.conf)
		v.set_delta(delta)
		v.set_frequency(freq)
