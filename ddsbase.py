#!/usr/bin/python
# dds control python script
#
# pip install pylibftdi
# refer /Library/Python/2.6/site-packages/pylibftdi

import sys
from optparse import OptionParser
from pylibftdi import BitBangDevice
from dds import AD9859

usage = "usage: %prog [options] [freq(Hz)] [amplitude(db)]"
parser = OptionParser(usage=usage)
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=False,
                  help="make lots of messages [default]")
parser.add_option("-m", "--mul", dest="mul", default=16,
				  help="set PLL multiplier [default: %default]")
parser.add_option("-c", metavar="FREQ", dest="crystal", default=25e6,
				  help="set crystal frequency to FREQ [default: %default]")
(options, args) = parser.parse_args()

crystal = options.crystal
mul = options.mul
fclk = mul * crystal

pins = { "sdio":4, "sclk":0, "ioupdate":2, "iosync":6, "reset":7 }
conf = { "pins":pins, "fclk":400e6, "refclk_multiplier":16, "vco_range":1 }

freq = 10e6
ampl = None
if len(args) >= 1:
	freq = float(args[0])
if len(args) >= 2:
	ampl = int(args[1])

if options.verbose:
	print "set frequency %gHz" % freq
	if ampl:
		print "set amplitude %ddB" % ampl
		
with BitBangDevice(direction = 0xff) as bb:
	dds = AD9859(bb, conf)
	dds.reset()
	dds.setup()
	dds.set_frequency(freq)
	#if ampl:
	#	dds.set_amplitude(ampl)
	dds.ioupdate()
	
	# dds.send_byte(0x55)
	# print dds.config_compile(dds.CFR1_DEF)
	# print dds.config_compile(dds.CFR2_DEF)
	# dds.assert_sclk()
	# dds.negate_sclk()
	# dds.toggle_sclk()
	# dds.set_bit("sclk", True)
	# dds.set_bit("sclk", False)
		
