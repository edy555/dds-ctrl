#!/usr/bin/python
# dds control python script
#
# pip install pylibftdi
# refer /Library/Python/2.6/site-packages/pylibftdi

import sys 
from pylibftdi import BitBangDevice
from dds import AD9859

pins = { "sdio":4, "sclk":0, "ioupdate":2, "iosync":6, "reset":7 }
conf = { "pins":pins, "fclk":400e6, "refclk_multiplier":16, "vco_range":1}

freq = 10e6
if len(sys.argv) > 1:
	freq = float(sys.argv[1])

with BitBangDevice(direction = 0xff) as bb:
	spi = AD9859(bb, conf)
	spi.reset()
	spi.setup()
	spi.set_frequency(freq)
	spi.ioupdate()
	
	# spi.send_byte(0x55)
	# print spi.config_compile(spi.CFR1_DEF)
	# print spi.config_compile(spi.CFR2_DEF)
	# spi.assert_sclk()
	# spi.negate_sclk()
	# spi.toggle_sclk()
	# spi.set_bit("sclk", True)
	# spi.set_bit("sclk", False)
		
