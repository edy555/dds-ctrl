#!/usr/bin/env ruby -w
require 'dds'
require 'optparse'

$omitinit = false
$disable1 = false
$disable2 = false

opt = OptionParser.new
opt.on('-n') {|v| $omitinit = true }
opt.on('-1') {|v| $disable2 = true }
opt.on('-2') {|v| $disable1 = true }
opt.parse!(ARGV)

$verbose = false
if ARGV[0]
  freq = ARGV[0].to_f
else
  freq = 12.345e6
end
if ARGV[1]
  delta = ARGV[1].to_f
else
  delta = 0
end

puts "set frequency #{freq}Hz and #{freq + delta}Hz"

pins1 = { :cs => 2, :sdio => 0, :sclk => 4, :ioupdate => 5 }
pins2 = { :cs => 1, :sdio => 7, :sclk => 4, :ioupdate => 6 }

bb = BitBang.new
dds1 = nil
dds2 = nil
dds1 = AD9859.new(:bitbang=>bb, :pins=>pins1, :fclk=>400e6, :refclk_multiplier => 10)
#dds2 = AD9859.new(:bitbang=>bb, :pins=>pins2, :fclk=>400e6, :refclk_multiplier => 10)
dds2 = AD9859.new(:bitbang=>bb, :pins=>pins2, :fclk=>440e6, :refclk_multiplier => 11)

bb.open

begin
  dds1.reset
  dds2.reset
  bb.flush

  unless $disable1
    dds1.setup
    dds1.set_frequency(freq)
    dds1.ioupdate
  end

  unless $disable2
    dds2.setup
    dds2.set_frequency(freq + delta)
    dds2.ioupdate
  end
ensure
  bb.close
end

