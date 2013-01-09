require 'rubygems'
require 'ftdi'

class BitBang
  def initialize(conf = {})
    @ftdi = Ftdi::Context.new
    @last = -1
    @array = []
  end

  def open
    @ftdi.usb_open(0x0403, 0x6001)
    @ftdi.set_bitmode(0xff, :bitbang)
  end

  def close
    #@ftdi.set_bitmode(0xff, :reset)
    @ftdi.usb_close
  end

  def flush
    @ftdi.write_data @array
    @array = []
  end

  def set_bit(bit, on)
    if on
      value = @last | (1 << bit)
    else
      value = @last & ~(1 << bit)
    end
    if value != @last then
      @array.push value
      @last = value
    end
  end

  def reset
    @array = []
  end
end

class SPIDevice
  def initialize(conf = {})
    @bitbang = conf[:bitbang] || BitBang.new(conf)
  end

  def open
    @bitbang.open
  end

  def close
    @bitbang.close
  end

  def reset
    @bitbang.reset
  end

  def set_bit(bit, on)
    @bitbang.set_bit(bit, on)
  end

  def flush
    @bitbang.flush
  end

  def assert_cs
    set_bit(@pins[:cs], false) if @pins[:cs]
  end

  def negate_cs
    set_bit(@pins[:cs], true) if @pins[:cs]
  end

  def assert_ioupdate
    set_bit(@pins[:ioupdate], true)
  end

  def negate_ioupdate
    set_bit(@pins[:ioupdate], false)
  end

  def toggle_ioupdate
    set_bit(@pins[:ioupdate], true)
    set_bit(@pins[:ioupdate], false)
  end

  def assert_sclk
    set_bit(@pins[:sclk], true)
  end

  def negate_sclk
    set_bit(@pins[:sclk], false)
  end

  def toggle_sclk
    set_bit(@pins[:sclk], true)
    set_bit(@pins[:sclk], false)
  end

  def spi_bit(on)
    set_bit(@pins[:sdio], on)
    toggle_sclk
  end

  def spi_byte(byte, bits)
    mask = 1 << (bits-1)
    bits.times {
      spi_bit((byte & mask) != 0)
      mask >>= 1
    }
  end

  def spi_array(data, bits)
    i = 0
    while bits > 0 do
      byte = data[i]
      mask = 1 << 7
      while mask > 0 && bits > 0 do
        spi_bit((byte & mask) != 0)
        bits -= 1
        mask >>= 1
      end
      i += 1
    end
  end
end

class AD9859 < SPIDevice
  PINS_DEFAULT = { :sdio => 0, :cs => 2, :sclk => 4, :ioupdate => 5 }
  FCLK_DEFAULT = 400e6
  CONFIG_DEFAULT = { :vco_range => 1, :refclk_multiplier => 10 }

  DIVISOR = 65536.0*65536.0
  ASF_MAX = 0x3fff

  #CFR1_DEFAULT = [ 0x00, 0x00, 0x00, 0x40 ]
  #CFR2_DEFAULT = [ 0x00, 0x02, 0x54 ] # REFCLK=x10

  CFR1 = 0x00
  CFR2 = 0x01
  ASF = 0x02
  ARR = 0x03
  FTW0 = 0x04
  POW0 = 0x05

  CFR1_DEF = [ [:unused,5],
               [:load_apr,1],
               [:osk_enable,1],
               [:auto_osk_keying,1],

               [:auto_sync,1],
               [:software_manual_sync,1],
               [:unused,6],

               [:unused,2],
               [:autoclrphaseaccum,1],
               [:enable_sine_out,1],
               [:unused,1],
               [:clearphaseaccum,1],
               [:sdio_input_only,1],
               :lsb_first,

               :digital_powerdown,
               :unused,
               :dac_powerdown,
               :clockinput_powerdown,
               :external_powerdownmode,
               :unused,
               :syncout_disable,
               :unused ]

  CFR2_DEF = [ [:unused, 8],

               [:unused, 4],
               [:high_speed_sync_enable, 1],
               [:hardware_manual_sync_enable, 1],
               [:crystal_out_pin_active, 1],
               [:unused, 1],

               [:refclk_multiplier, 5],
               [:vco_range, 1],
               [:charge_pump_current, 2] ]

  def config_compile(conf, bitdef)
    ary = []
    byte = 0
    i = 8
    bitdef.each {|k|
      s = 1
      if k.is_a? Array 
        s = k.at(1)
        k = k.at(0)
      end

      i -= s
      raise if i < 0
      v = conf[k]
      byte |= v << i if v
      if i == 0 then
        ary.push byte
        byte = 0
        i = 8
      end
    }
    ary
  end


  def initialize(conf = {})
    super(conf)
    @conf = CONFIG_DEFAULT.merge conf
    @fclk = @conf[:fclk] || FCLK_DEFAULT
    @pins = @conf[:pins] || PINS_DEFAULT
  end

  def reset
    @bitbang.reset
    negate_cs
    negate_ioupdate
    negate_sclk
  end

  def setup
    assert_cs
    cfr1 = config_compile @conf, CFR1_DEF
    cfr2 = config_compile @conf, CFR2_DEF
    write_reg(CFR1, cfr1, 32)
    write_reg(CFR2, cfr2, 24)
    negate_cs
  end

  def write_reg(reg, data, bits)
    spi_byte(reg, 8)
    spi_array(data, bits)
  end

  def setFTW0(ftw0)
    write_reg(FTW0, [ftw0.to_i].pack('N'), 32)
  end

  def setASF(ampl)
    write_reg(ASF, [ampl.to_i & 0x3fff].pack('n'), 16)
  end

  def set_frequency(freq)
    assert_cs
    setFTW0(freq * DIVISOR / @fclk)
    negate_cs
  end

  def set_amplitude(db)
    assert_cs
    db = 0 if db > 0
    setASF(10.0**(db / 20.0) * ASF_MAX)
    negate_cs
  end

  def ioupdate
    toggle_ioupdate
    flush
  end
end
