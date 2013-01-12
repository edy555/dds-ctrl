#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Audio Fft 2
# Generated: Tue Jan  8 20:28:37 2013
##################################################

from gnuradio import audio
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import numbersink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class audio_fft_2(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Audio Fft 2")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 48000

		##################################################
		# Blocks
		##################################################
		self.wxgui_numbersink2_0_0 = numbersink2.number_sink_f(
			self.GetWin(),
			unit="deg",
			minval=-90,
			maxval=90,
			factor=90/3.14159,
			decimal_places=10,
			ref_level=0,
			sample_rate=samp_rate,
			number_rate=15,
			average=False,
			avg_alpha=None,
			label="Angle",
			peak_hold=False,
			show_gauge=True,
		)
		self.Add(self.wxgui_numbersink2_0_0.win)
		self.wxgui_numbersink2_0 = numbersink2.number_sink_f(
			self.GetWin(),
			unit="mag",
			minval=-100,
			maxval=0,
			factor=20,
			decimal_places=10,
			ref_level=0,
			sample_rate=samp_rate,
			number_rate=15,
			average=False,
			avg_alpha=None,
			label="Magnitude",
			peak_hold=False,
			show_gauge=True,
		)
		self.Add(self.wxgui_numbersink2_0.win)
		self.wxgui_fftsink2_0_0 = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Reflect",
			peak_hold=False,
			win=window.hamming,
		)
		self.Add(self.wxgui_fftsink2_0_0.win)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="Reference",
			peak_hold=False,
			win=window.hamming,
		)
		self.Add(self.wxgui_fftsink2_0.win)
		self.gr_nlog10_ff_0 = gr.nlog10_ff(1, 1, 0)
		self.gr_divide_xx_0 = gr.divide_cc(1)
		self.gr_complex_to_mag_0 = gr.complex_to_mag(1)
		self.gr_complex_to_arg_0 = gr.complex_to_arg(1)
		self.band_pass_filter_0_0 = gr.fir_filter_fcc(1, firdes.complex_band_pass(
			1, samp_rate, 4.8e3, 5.2e3, 100, firdes.WIN_HAMMING, 6.76))
		self.band_pass_filter_0 = gr.fir_filter_fcc(1, firdes.complex_band_pass(
			1, samp_rate, 4.8e3, 5.2e3, 100, firdes.WIN_HAMMING, 6.76))
		self.audio_source_0 = audio.source(samp_rate, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.audio_source_0, 0), (self.band_pass_filter_0, 0))
		self.connect((self.band_pass_filter_0, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.audio_source_0, 1), (self.band_pass_filter_0_0, 0))
		self.connect((self.band_pass_filter_0_0, 0), (self.wxgui_fftsink2_0_0, 0))
		self.connect((self.band_pass_filter_0, 0), (self.gr_divide_xx_0, 0))
		self.connect((self.band_pass_filter_0_0, 0), (self.gr_divide_xx_0, 1))
		self.connect((self.gr_divide_xx_0, 0), (self.gr_complex_to_arg_0, 0))
		self.connect((self.gr_complex_to_arg_0, 0), (self.wxgui_numbersink2_0_0, 0))
		self.connect((self.gr_complex_to_mag_0, 0), (self.gr_nlog10_ff_0, 0))
		self.connect((self.gr_nlog10_ff_0, 0), (self.wxgui_numbersink2_0, 0))
		self.connect((self.band_pass_filter_0_0, 0), (self.gr_complex_to_mag_0, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.band_pass_filter_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, 4.8e3, 5.2e3, 100, firdes.WIN_HAMMING, 6.76))
		self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
		self.wxgui_fftsink2_0_0.set_sample_rate(self.samp_rate)
		self.band_pass_filter_0_0.set_taps(firdes.complex_band_pass(1, self.samp_rate, 4.8e3, 5.2e3, 100, firdes.WIN_HAMMING, 6.76))

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = audio_fft_2()
	tb.Run(True)

