#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Vna Probe
# Generated: Sat Jan 12 03:07:08 2013
##################################################

from pylibftdi import BitBangDevice
from vna import vna

from gnuradio import audio
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
import gnuradio.gr.gr_threading as _threading
import time
from optparse import OptionParser

class vna_probe(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self)

		##################################################
		# Variables
		##################################################
		self.signal_freq = signal_freq = 5000
		self.samp_rate = samp_rate = 48000
		self.bw = bw = 200

		##################################################
		# Blocks
		##################################################
		self.gr_probe_mag = gr.probe_signal_f()
		self.gr_probe_arg = gr.probe_signal_f()
		self.gr_nlog10_ff_0 = gr.nlog10_ff(1, 1, 0)
		self.gr_divide_xx_0 = gr.divide_cc(1)
		self.gr_complex_to_mag_0 = gr.complex_to_mag(1)
		self.gr_complex_to_arg_0 = gr.complex_to_arg(1)
		self.band_pass_filter_0_0 = gr.fir_filter_fcc(1, firdes.complex_band_pass(
			1, samp_rate, signal_freq-bw/2, signal_freq+bw/2, 100, firdes.WIN_BLACKMAN, 6.76))
		self.band_pass_filter_0 = gr.fir_filter_fcc(1, firdes.complex_band_pass(
			1, samp_rate, signal_freq-bw/2, signal_freq+bw/2, 100, firdes.WIN_BLACKMAN, 6.76))
		self.audio_source_0 = audio.source(samp_rate, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.band_pass_filter_0_0, 0), (self.gr_complex_to_mag_0, 0))
		self.connect((self.gr_complex_to_mag_0, 0), (self.gr_nlog10_ff_0, 0))
		self.connect((self.gr_divide_xx_0, 0), (self.gr_complex_to_arg_0, 0))
		self.connect((self.band_pass_filter_0_0, 0), (self.gr_divide_xx_0, 1))
		self.connect((self.band_pass_filter_0, 0), (self.gr_divide_xx_0, 0))
		self.connect((self.audio_source_0, 1), (self.band_pass_filter_0_0, 0))
		self.connect((self.audio_source_0, 0), (self.band_pass_filter_0, 0))
		self.connect((self.gr_nlog10_ff_0, 0), (self.gr_probe_mag, 0))
		self.connect((self.gr_complex_to_arg_0, 0), (self.gr_probe_arg, 0))

	def get_signal_freq(self):
		return self.signal_freq

	def set_signal_freq(self, signal_freq):
		self.signal_freq = signal_freq
		self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, self.signal_freq-self.bw/2, self.signal_freq+self.bw/2, 100, firdes.WIN_BLACKMAN, 6.76))
		self.band_pass_filter_0_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, self.signal_freq-self.bw/2, self.signal_freq+self.bw/2, 100, firdes.WIN_BLACKMAN, 6.76))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, self.signal_freq-self.bw/2, self.signal_freq+self.bw/2, 100, firdes.WIN_BLACKMAN, 6.76))
		self.band_pass_filter_0_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, self.signal_freq-self.bw/2, self.signal_freq+self.bw/2, 100, firdes.WIN_BLACKMAN, 6.76))

	def get_bw(self):
		return self.bw

	def set_bw(self, bw):
		self.bw = bw
		self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, self.signal_freq-self.bw/2, self.signal_freq+self.bw/2, 100, firdes.WIN_BLACKMAN, 6.76))
		self.band_pass_filter_0_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, self.signal_freq-self.bw/2, self.signal_freq+self.bw/2, 100, firdes.WIN_BLACKMAN, 6.76))

class top_block_runner(_threading.Thread):
    def __init__(self, tb):
        _threading.Thread.__init__(self)
        self.setDaemon(1)
        self.tb = tb
        self.done = False
        self.start()

    def run(self):
        self.tb.run()
        self.done = True

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("-v", "--verbose",
					  action="store_true", dest="verbose", default=False,
					  help="make lots of messages [default]")
	parser.add_option("-m", "--mul", dest="mul", default=16,
					  help="set PLL multiplier [default: %default]")
	parser.add_option("-c", metavar="FREQ", dest="crystal", default=25e6,
					  help="set crystal frequency to FREQ [default: %default]")
	parser.add_option("-s", metavar="FREQ", dest="start", type="float", default=0e6,
					  help="sweep start FREQ [default: %default]")
	parser.add_option("-e", metavar="FREQ", dest="end", type="float", default=200e6,
					  help="sweep stop FREQ [default: %default]")
	parser.add_option("-n", metavar="STEP", dest="step", type="int", default=50,
					  help="sweep STEPs [default: %default]")
	parser.add_option("-i", metavar="SEC", dest="interval", type="float", default=0.1,
					  help="set measuring interval [default: %default]")
	(options, args) = parser.parse_args()
	tb = vna_probe()
	runner = top_block_runner(tb)
	with BitBangDevice(direction=0xff, sync=False) as dev:
		v = vna(dev)
		v.reset()
		start = options.start
		end = options.end
		step = options.step
		# if options.verbose:
		# 	print "Sweep from %gHz to %gHz with %d steps"%(start,end,step)
		for i in range(step + 1):
			freq = start + (end - start)/step*i
			v.set_frequency(freq)
			time.sleep(options.interval)
			print "%d" % freq,
			print "%f" % (tb.gr_probe_arg.level() / 3.14 + 1),
			print "%f" % (tb.gr_probe_mag.level() + 4)
