#!/usr/bin/env ruby -w
require 'dds'
require 'optparse'

$verbose = false
freq = -1
crystal = 25e6
mul = 16

opt = OptionParser.new
opt.on('-m {multiplier}') {|v| mul = v.to_i }
opt.on('-c {crystal freq}') {|v| crystal = v.to_i }
opt.on('-v') {|v| $verbose = true }
opt.parse!(ARGV)

unless ARGV[0]
  puts "usage: #{$0} {frequency(Hz)} [amplitude(dB)]"
  exit(-1)
end

if ARGV[0]
  freq = ARGV[0].to_f
end
if ARGV[1]
  db = ARGV[1].to_f
else
  db = 0
end

puts "set frequency #{freq}Hz" if $verbose

pins = { :sdio => 4, :sclk => 0, :ioupdate => 2, :iosync => 6, :reset => 7 }
fclk = crystal * mul

puts "fclk frequency #{fclk}Hz" if $verbose

dds = AD9859.new(:pins => pins, :fclk => fclk, :refclk_multiplier => mul, :osk_enable => 1)
dds.open

begin
  dds.reset
  dds.setup
  dds.flush

  dds.set_frequency(freq)
  dds.set_amplitude(db)
  dds.ioupdate
ensure
  dds.close
end

