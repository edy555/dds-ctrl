#!/usr/bin/env ruby -w
require 'dds'
require 'optparse'

step = 10
delta = 5000
interval = 1
do_loop = false
$verbose = false

opt = OptionParser.new
opt.on('-s {steps}') {|v| step = v.to_i }
opt.on('-d {delta}') {|v| delta = v.to_f }
opt.on('-i {interval}') {|v| interval = v.to_f }
opt.on('-l') {|v| do_loop = true }
opt.on('-v') {|v| $verbose = true }
opt.parse!(ARGV)

if ARGV[0]
  start = ARGV[0].to_f
else
  start = 10.000e6
end
if ARGV[1]
  stop = ARGV[1].to_f
else
  stop = start * 2
end

puts "sweep frequency from #{start}Hz to #{stop}Hz with #{step} steps"

pins1 = { :cs => 2, :sdio => 0, :sclk => 4, :ioupdate => 5 }
pins2 = { :cs => 1, :sdio => 7, :sclk => 4, :ioupdate => 6 }

crystal = 40e6
m1 = 18
m2 = 19

bb = BitBang.new
dds1 = nil
dds2 = nil
# dds1 = AD9859.new(:bitbang=>bb, :pins=>pins1, :fclk=>400e6, :refclk_multiplier => 10)
# dds2 = AD9859.new(:bitbang=>bb, :pins=>pins2, :fclk=>440e6, :refclk_multiplier => 11)
dds1 = AD9859.new(:bitbang=>bb, :pins=>pins1, :fclk=>crystal*m1, :refclk_multiplier=>m1)
dds2 = AD9859.new(:bitbang=>bb, :pins=>pins2, :fclk=>crystal*m2, :refclk_multiplier=>m2)

bb.open

begin
  dds1.reset
  dds2.reset
  dds1.setup 
  dds2.setup 
  bb.flush

  begin
    freq = start
    (step+1).times {|i|
      freq = start + i * (stop - start) / step
      puts "#{freq}Hz" if $verbose

      dds1.set_frequency(freq)
      dds2.set_frequency(freq + delta)
      dds1.ioupdate
      dds2.ioupdate
      sleep interval
    }
  end while do_loop
ensure
  bb.close
end

