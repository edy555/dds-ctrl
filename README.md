dds-ctrl script
===============

# What is this?

This folder contains sample script to control Digital Direct
Synthesizer(DDS) of Analog Devices(AD) with SPI via FT232R BitBang Device.

# Requirements

## Software

 * libftdi.rb

## Hardware

 * FT232RL device
 * DDS Board

# Preparation

    $ gem install libftdi-ruby
  	$ sudo kextunload /System/Library/Extensions/FTDIUSBSerialDriver.kext

# How to run

  	$ ./ddsbase.rb 10e6
