import struct

class BitBangInterface:
	def __init__(self, device):
		self.device = device
		self.last = None
		self.buf = bytearray()
		
	def set_bit(self, bit, on):
		if on:
			if self.last:
				value = self.last | (1<<bit)
			else:
				value = 1<<bit
		else:
			if self.last:
				value = self.last & ~(1<<bit)
			else:
				value = ~(1<<bit)
		self.buf.append(value)
		self.last = value
		# if on :
		# 	self.bitbang.port |= 
		# else:
		# 	self.bitbang.port &= ~(1<<bit)

	def flush(self):
		#print self.buf
		self.device.write(self.buf)
		self.device.flush()
		self.buf = bytearray()


class SPIDevice:
	def __init__(self, bb, pins, conf = {}):
		self.bitbang = bb
		self.pins = pins
			
	def set_bit(self, bit, on):
		if isinstance(bit, str):
			bit = self.pins.get(bit)
			if bit == None:
				return
		self.bitbang.set_bit(bit, on)

	def flush(self):
		self.bitbang.flush()
		
	def assert_cs(self):
		self.set_bit("cs", False)
	
	def negate_cs(self):
		self.set_bit("cs", True)
	
	def assert_sclk(self):
		self.set_bit("sclk", True)
	
	def negate_sclk(self):
		self.set_bit("sclk", False)
	
	def toggle_sclk(self):
		self.assert_sclk()
		self.negate_sclk()
	
	def assert_reset(self):
		self.set_bit("reset", True)
	
	def negate_reset(self):
		self.set_bit("reset", False)

   	def assert_ioupdate(self):
		self.set_bit("ioupdate", True)
	
	def negate_ioupdate(self):
		self.set_bit("ioupdate", False)
	
	def toggle_ioupdate(self):
		self.assert_ioupdate()
		self.negate_ioupdate()

	def send_bit(self, on):
		self.set_bit("sdio", on)
		self.toggle_sclk()

	def send_byte(self, byte, bits = 8):
		mask = 1 << (bits-1)
		for i in range(bits):
			self.send_bit((byte & mask) != 0)
			mask >>= 1
			
	def send_array(self, data, bits):
		i = 0
		while bits > 0:
			byte = data[i]
			mask = 1 << 7
			while mask > 0 and bits > 0:
				self.send_bit((byte & mask) != 0)
				bits -= 1
				mask >>= 1
			i += 1

class AD9859(SPIDevice):
	PINS_DEFAULT = { "sdio":0, "cs":2, "sclk":4, "ioupdate":5 }
	FCLK_DEFAULT = 400e6
	CONFIG_DEFAULT = { "vco_range":1, "refclk_multiplier":10 }
	
	DIVISOR = 65536.0*65536.0
	ASF_MAX = 0x3fff

	CFR1 = 0x00
	CFR2 = 0x01
	ASF = 0x02
	ARR = 0x03
	FTW0 = 0x04
	POW0 = 0x05
	
	CFR1_DEF = ( ("unused", 5),
               ("load_apr", 1),
               ("osk_enable", 1),
               ("auto_osk_keying", 1),
               ("auto_sync", 1),
               ("software_manual_sync", 1),
               ("unused", 6),
               ("unused", 2),
               ("autoclrphaseaccum", 1),
               ("enable_sine_out", 1),
               ("unused", 1),
               ("clearphaseaccum", 1),
               ("sdio_input_only", 1),
			   "lsb_first",
               "digital_powerdown",
               "unused",
               "dac_powerdown",
               "clockinput_powerdown",
               "external_powerdownmode",
               "unused",
               "syncout_disable",
               "unused" )

	CFR2_DEF = ( ("unused", 8),
				 ("unused", 4),
				 ("high_speed_sync_enable", 1),
				 ("hardware_manual_sync_enable", 1),
				 ("crystal_out_pin_active", 1),
				 ("unused", 1),
				 ("refclk_multiplier", 5),
				 ("vco_range", 1),
				 ("charge_pump_current", 2) )
	
	def get_config_reg(self, bitdef):
		conf = self.conf
		ary = bytearray()
		byte = 0
		i = 8
		for k in bitdef:
			s = 1
			if not isinstance(k, str):
				s = k[1]
				k = k[0]
			i -= s
			#raise if i < 0
			v = conf.get(k)
			if v:
				byte |= v << i
			if i == 0:
				ary.append(byte)
				byte = 0
				i = 8
		return ary

	def __init__(self, bb, conf = {}):
		pins = conf.get("pins") or AD9859.PINS_DEFAULT
		SPIDevice.__init__(self, bb, pins, conf)
		self.conf = conf
		self.fclk = conf["fclk"]

	def reset(self):
		self.negate_cs()
		self.negate_ioupdate()
		self.negate_sclk()
		self.negate_reset()

	def setup(self):
		self.assert_cs()
		cfr1 = self.get_config_reg(AD9859.CFR1_DEF)
		cfr2 = self.get_config_reg(AD9859.CFR2_DEF)
		self.write_reg(AD9859.CFR1, cfr1, 32)
		self.write_reg(AD9859.CFR2, cfr2, 24)
		self.negate_cs()

	def write_reg(self, reg, data, bits):
		self.send_byte(reg, 8)
		self.send_array(data, bits)

	def setFTW0(self, ftw0):
		reg = bytearray(struct.pack('>L', int(ftw0)))
		self.write_reg(AD9859.FTW0, reg, 32)

	def setASF(self, ampl):
		reg = bytearray(struct.pack('>L', int(ampl) & 0x3fff))
		self.write_reg(AD9859.ASF, reg, 16)

	def set_frequency(self, freq):
		self.assert_cs()
		self.setFTW0(freq * AD9859.DIVISOR / self.fclk)
		self.negate_cs()

	def set_amplitude(self, db):
		self.assert_cs()
		if db > 0:
			db = 0
		self.setASF(10.0**(db / 20.0) * AD9859.ASF_MAX)
		self.negate_cs()

	def ioupdate(self):
		self.toggle_ioupdate()
		self.flush()
