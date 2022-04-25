# ADI-AD9548 

Set of tools to interact & program AD9548,AD9547 integrated circuits, by Analog Devices.

Use these tools to interact with newer chipsets
[AD9546/45](https://github.com/gwbres/adi-ad9546)

These scripts are not Windows compatible.   

## Install 

```shell
python setup.py install
```

## Dependencies

* python-smbus

Install requirements with

```shell
pip3 install -r requirements.txt
```

## API

* Each application comes with an `-h` help menu.  
Refer to help menu for specific information. 
* Flags order does not matter
* `flag` is mandatory
* `--flag` describe an optionnal flag, action will not be performed if not passed

## AD9547,48

The two chip share similar functionnalities, except that
AD9548 is more capable than 47.   
Therefore, both can share the following tools, but it is up to the user
to restrict to supported operations, when operating an AD9547.

## Utilities

* `calib.py`: is critical, calibrates clock and internal synthesizers. 
Action required depending on previous user actions and current settings. 
* `distrib.py`: is critical, controls clock distribution and output signals
* `power-down.py` : power saving and management utility
* `profile.py`: very useful, loads / dumps a register map preset,
as desribed in application note
* `reset.py`: to quickly reset the device
* `status.py` : general status monitoring, including on board temperature,
sensors and IRQ flags

## Register map

`regmap.py` allows the user to quickly load an exported
register map from the official A&D graphical tool.
* Support format is `json`.
* `i2c` bus must be specified
* `i2c slave address` must be specified

```shell
regmap.py -h
# load a register map (on bus #0 @0x48)
regmap.py 0 0x48 --load test.json
```

Export current register map to open it in A&D graphical tools:
```shell
regmap.py --dump /tmp/output.json 0 0x48
```

* Use `--quiet` in both cases to disable the progress bar

## Status script

`status.py` is a read only tool, to interact with the integrated chip.  
`i2c` bus number (integer number) and slave address (hex) must be specified.

Use the `help` menu to learn how to use this script:
```shell
status.py -h
usage: status.py [-h] 
    [--info]
    [--serial]
    [--sysclk-pll] [--sysclk-comp]
    [--pll] [-pll0] [--pll1]
    [--refa] [-refaa] [--refb] [--refbb] 
    [--irq] 
    [--iuts] 
    [--temp] 
    [--eeprom] 
    [--misc] 
    bus address

Clock status reporting

positional arguments:
  bus           I2C bus
  address       I2C slv address

optional arguments:
  -h, --help    show this help message and exit
  --info         Device general infos (SN#, ..)
  --serial       Serial port status (I2C/SPI)
  --sysclk-pll   Sys clock synthesis pll
  --sysclk-comp  Sys clock compensation
  --pll          Shared Pll global info
  --pll0         Pll0 specific infos
  --pll1         Pll1 specific infos
  --refa         REF-A signal info
  --refaa        REF-AA signal info
  --refb         REF-B signal info
  --refbb        REF-BB signal info
  --irq          IRQ registers
  --iuts         Report IUTS Status
  --temp         Internal temperature sensor
  --eeprom       EEPROM controller status
  --misc         Auxilary NCOs, DPll and Temp info
```

Several part of the integrated chips can be monitored at once.
Output format is `json` and is streamed to `stdout`.
Example of use:

```shell
# Grab general / high level info (bus=0, 0x4A):
status.py --info --serial --pll 0 0x4A

# General clock infos + ref-a status (bus=1, 0x48):
status.py --pll --sysclk-pll --refa 1 0x48

# IRQ status register
status.py --irq 0 0x4A

# dump status to a file
status.py --info --serial --pll 0 0x4A > /tmp/status.json

# call status.py from another python script;
# evaluate json content (dict) directly from `stdout`
import subprocess
args = ['status.py', '--info', '0', '0x4A']
ret = subprocess.run(args)
if ret.exitcode == 0: # OK
   # grab `stdout`
   status = ret.stdout.decode('utf-8') 
   # build structure directly
   status = eval(status)
   status['info']['vendor'] # eval() is way cool!
```

## Reset script

`reset.py` to perform quick reset operations

```shell
# clear all asserted IRQs
reset.py 0 0x4A --irq
# reset tuning word history + watchdog timer 
reset.py 0 0x4A --watchdog --tuning
```

* `reset.py -h` for complete list of features

## Calibration script

`calib.py` initializes the `sys clock` calibration routine.

```shell
calib.py 0 0x4A
status.py 0 0x4A --sysclk
```

## Clock distribution

`distrib.py` is also an important utility. 
It helps configure the clock path, control output signals
and their behavior.

Control flags:
* `--core`: (optionnal) describes which core we are targetting.
This script only suppports a single `--core` assignment.
One must call `distrib.py` several times to perform multiple clock distribution.

* `--channel`: (optionnal) describes which channel we are targetting for a given core.
This script only suppports a single `--channel` assignment.
One must call `distrib.py` several times to perform multiple channel distribution.
Default to `all`, meaning if `--channel` is not specified, both channel (CH0/CH1)
are assigned the same value.

Action flags: the script supports as many `action` flags as desired.

* `--sync-all`: sends a SYNC order to all distribution dividers.
This action is special, in the sense `--core` and `--channel` are discarded.
It is required to run a `sync-all` in case the current output behavior
is not set to `immediate`.

```shell
# assign a SYNC all, might be required depending on
# current configuration or previously loaded profile
# This one is special, because --core + --channel are discarded
distrib.py --sync-all 0 0x48
```

* `--autosync` : control given channel so called "autosync" behavior.
`--core` is not needed for such operation.
```shell
# set both Pll CH0 & CH1 to "immediate" behavior
distrib.py --autosync immediate 0 0x48
# set both Pll CH0 to "immediate" behavior
distrib.py --autosync immediate --channel 0 0 0x48
#  and Pll CH1 to "manual" behavior
distrib.py --autosync manual --channel 1 0 0x48
```

In the previous example, CH1 is set to manual behavior.  
One must either perform a `sync-all` operation,
a `q-sync` operation on channel 1,
or an Mx-pin operation with dedicated script, to enable this output signal.

* `--q-sync` : initializes a Q Divider synchronization sequence manually. 
This is useful when enabling a channel manually, but without dedicated Mx-pin
control.
`--core` is not needed for such operation.
```shell
# manual Q Sync on both channels
distrib.py --q-sync 0 0x48
# manual Q Sync on channel 1
distrib.py --q-sync --channel 1 0 0x48
```

## Profile

AD9547,48 supports up to 8 profiles.  
A profile comprises:

* the expected input period
* input signal constraints
* input signal quality constraints
* a loop filter profile (4 coefficients: alpha, beta, delta, gamma)

For the loop filter coefficients, the script accepts fractionnal data
directly and converts them internally.

The script only supports reading/writing one profile at a time.

* `--read n` : read current profile `n` (starting at 0) stored internally.
Example:

```shell
# Read current 2nd profile storage
profile.py --read 1 
# outputs all values
```

* `--load n` : load settings into `n` storage location (starting at 0).
The set of value(s) to be loaded must be specified.
Example:

```shell
# define a new profile #0
profile.py 0 0x48 --load 1 \
    # reference period in [s] 
    --period 10E-9 \
    # inner tolerance
    --inner 0.1 \
    # outter tolerance 
    --outter 0.1 \
    # validation timer [s]
    --validation 100E-4 \
    # redetect timer [s]
    --redetect 100E-3 \ 
    # filter coefficients
    --alpha 100E-3 \
    --alpha 12735446E-3 \
    --beta 698672E-5 \
    --delta 750373E-5 \
    --gamma 2015399E-3
```

All parameters are optionnal,
in this example, only `--alpha` and `--outer` tolerance
get loaded

```shell
# complete profile #1 redefinition
profile.py 0 0x48 --load 1 \
    --outter 0.1 \
    --alpha 100E-3
```

## Reset script

To quickly reset the device

* `--soft` : performs a soft reset
* `--sans` : same thing but maintains current registers value 
* `--watchdog` : resets internal watchdog timer
* `-h` for more infos

## Power down script

`power-down.py` perform and recover power down operations.   
Useful to power down non needed channels and internal cores. 

The `--all` flag addresses all internal cores.  
Otherwise, select internal units with related flag

* Power down device entirely
```shell
power-down.py 0 0x4A --all
```
* Recover a complete power down operation
```shell
power-down.py 0 0x4A --all --clear
```

* Wake `-a` references up and put `-b` reference channels to sleep:
```shell
power-down.py 0 0x4A --refb --refbb --refaa
power-down.py 0 0x4A --clear --refa 
```

## IRQ events

`status.py --irq` allows reading the current asserted IRQ flags.  

Clear them with `irq.py`:

* `--all`: clear all flags
* `--pll`: clear all PLL (PLL0 + PLL1 + digital + analog) related events 
* `--pll0`: clear PLL0 (digital + analog) related events 
* `--pll1`: clear PLL1 (digital + analog) related events 
* `--other`: clear events that are not related to the pll subgroup
* `--sysclk`: clear all sysclock related events 
* `-h`: for other known flags

## Misc

`status.py --temp` returns the internal temperature sensor reading.  

* Program a temperature range :

```shell
misc.py --temp-thres-low -10 # [°C]
misc.py --temp-thres-high 80 # [°C]
misc.py --temp-thres-low -30 --temp-thres-high 90
status.py --temp 0 0x48 # current reading [°C] 
```

Related warning events are then retrieved with the `irq.py` utility, refer to related section.
