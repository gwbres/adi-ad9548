# ADI-AD9548 

[![Python application](https://github.com/gwbres/adi-ad9548/actions/workflows/python-app.yml/badge.svg)](https://github.com/gwbres/adi-ad9548/actions/workflows/python-app.yml)
[![PyPI version](https://badge.fury.io/py/adi-ad9548.svg)](http://badge.fury.io/py/adi-ad9548)

Set of tools to interact & program AD9548,AD9547 integrated circuits, by Analog Devices.

Use these tools to interact with newer chipsets
[AD9546/45](https://github.com/gwbres/adi-ad9546)

These scripts are not Windows compatible.   
These scripts expect a `/dev/i2c-X` entry, they do not manage the device
through SPI at the moment.

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
* `flag` is a mandatory flag
* `--flag` is an optionnal flag: action will not be performed if not passed

## AD9547,48

The two chip share similar functionnalities, except that
AD9548 is more capable than 47.   
Therefore, both can share the following tools, but it is up to the user
to restrict to supported operations, when operating an AD9547.

## Utilities

* `calib.py`: to initiate a calibration process 
* `distrib.py`: clock distribution and output signal management utility 
* `irq.py`: IRQ masking & clearing operations 
* `power-down.py` : power saving and management utility
* `regmap.py`: load / dump a register map into device 
* `reset.py`: reset the device 
* `status.py` : generate status monitoring, includes IRQ status report 

## Register map

`regmap.py` allows the user to load an exported
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
# determine known options
status.py -h

# general info
status.py 0 0x4A --info
# IRQ + dpll status report
status.py 0 0x4A --irq --dpll
```

The output uses `json` format and is streamed to stdout directly.
One can either dump it to a file, or directly loaded into
another python script:

```shell
import subprocess
args = ['status.py', '--info', '0', '0x4A']
ret = subprocess.run(args)
if ret.exitcode == 0: # OK
   # grab `stdout`
   status = ret.stdout.decode('utf-8') 
   # build structure directly
   status = eval(status)
   print(status['info']['vendor'])
```

## Reset script

`reset.py` to perform reset operations

* `--soft` : performs a soft reset but maintains current registers value
* `--irq` : clears all IRQ
* `--phase` : resets DDS accumulator 
* `--history` : resets tuning word history 
* `-h` for more infos

```shell
# clear all asserted IRQs
reset.py 0 0x4A --irq
# reset tuning word history + watchdog timer 
reset.py --tuning --watchdog 0 0x4A
```

## Calibration script

`calib.py` initializes / calibrates the clock: 

```shell
calib.py 0 0x4A
```

## Profile

AD9548 supports up to 8 internal profiles.  
A profile comprises:

* the expected input period
* input signal constraints
* input signal quality constraints
* a loop filter profile (4 coefficients: alpha, beta, delta, gamma)

For the loop filter coefficients, the script accepts fractionnal data
directly and converts them internally.

The script only supports reading/writing one profile at a time.

* `--read n` : read current profile `n` (starting at 0) stored internally.
When using this flag, all other flags are discarded and get left out.

Example:

```shell
# read settings contained in `0` profile storage
profile.py 1 0x43 --read 0 
# read 3rd profile
profile.py 1 0x43 --read 2 
```

* `--load n` : load settings into `n` storage location (starting at 0).
The set of value(s) to be loaded must be specified.
Example:

```shell
# define a new profile #0
profile.py 0 0x48 --load 1 \
    # reference freq [Hz] 
    --freq 1E8 \
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

## Power down script

`power-down.py` perform and recover power down operations.   
Useful to power down non needed channels and internal cores. 

The `--all` flag addresses all internal cores.  
Otherwise, select internal units with related flag

* Power down device entirely
```shell
power-down.py 0 0x4A --all
```
* Recover
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


## Typical configuration flow

```shell
# load a register map
regmap.py --load data.json --quiet 0 0x4A
# initiate calibration
calib.py 0 0x4A
```
