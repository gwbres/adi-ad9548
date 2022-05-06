# ADI-AD9548 

[![Python application](https://github.com/gwbres/adi-ad9548/actions/workflows/python-app.yml/badge.svg)](https://github.com/gwbres/adi-ad9548/actions/workflows/python-app.yml)
[![PyPI version](https://badge.fury.io/py/adi-ad9548.svg)](http://badge.fury.io/py/adi-ad9548)

Set of tools to interact & program AD9548,AD9547 integrated circuits, by Analog Devices.

Use [these tools](https://github.com/gwbres/adi-ad9546) to interact with AD9546/45 newer chipsets

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

## AD9548/47

The two chip share similar functionnalities, except that
AD9548 is more capable than 47.   
Therefore, both can share the following tools, but it is up to the user
to restrict to supported operations, when operating an AD9547.

## Utilities

* `calib.py`: to initiate a calibration process 
* `distrib.py`: clock distribution and output signal management utility 
* `dpll.py`: Digital PLL management utility, includes history and instantaneous phase control. 
* `irq.py`: IRQ masking & clearing operations 
* `mx-pin.py` : programmable I/O management (Mx pins) 
* `power-down.py` : power saving and management utility
* `profile.py` : profile storage area management and loading interface 
* `regmap.py`: load / dump a register map into device 
* `reset.py`: reset operations 
* `status.py` : status monitoring, includes IRQ status report 

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

## Mx-pin programmable I/O

AD9548 has 8 programmable pin.  
Each pin can operate as an input or an output pin.  
Each pin supports about 20 different macros.

* `pin`: select desired pin from M0 to M7
* `io`: {"input","output"} : programm given pin as an input or an output
* `macro`: select macro (special opmode) to program

The script supports one Pin assignement per call. It is not possible
to program several pins at once

```shell
# M0 will serve as freq lock indicator
mx-pin.py 0 0x4A M0 output dpll-freq-locked
# M1 will serve as phase lock indicator
mx-pin.py 0 0x4A M1 output dpll-phase-locked
# asserting M2 high will have the dpll go into free-running state
mx-pin.py 0 0x4A M2 input dpll-free-running 
# M3 will be an accessible sys clock image 
mx-pin.py 0 0x4A M3 output sysclk/32 
```

## Distribution

`distrib.py` to control clock distribution
and output signals.
All special operations discard the `--channel` argument.

* `--sync`: iniate a distribution SYNC operation manually

```shell
distrib.py 0 0x4A --sync
```

* `--source` is a special operation,
sets clock distribution synchronization source.

```shell
# Set direct sync source
distrib.py 0 0x4A --source direct
# Change sync source
distrib.py 0 0x4A --source dpll-feedback
```

* `--autosync` is a special operation,
sets the autosync behavior

```shell
# disable autosync feature
distrib.py 0 0x4A --autosync disabled
# set to autosync on phase lock
distrib.py 0 0x4A --autosync dpll-phase-lock
```

* All other flags require the `--channel` 
flag to specify which Qx (output divider)
or OUTx (output pin) we are configuring.
It is possible to omit `--channel`, 
in this scenario we assume `all` channels
are targetted.

* `cmos-phase`: phase in CMOS output mode
* `polarity`: OUTx pin polarity 
* `strength`: OUTx pin output current
* `mode`: OUTx pin output mode (LVDS, LVPECL, ...)
* `divider`: Qx division ratio

It is possible to apply several configurations
at once, but only to a single `--channel` target:

```shell
# set all OUTx pins to LVDS output mode
distrib.py 0 0x4A --mode lvds
# set OUT0 to LVPECL output mode
distrib.py 0 0x4A --mode lvpecl --channel 0

# Set OUT1 to CMOS with inverted polarity
distrib.py 0 0x4A --mode cmos --polarity inverted --channel 1

# Program Q0 and Q1 R=10_000_000
# and Q2 and Q3 R=5_000_000
distrib.py 0 0x4A --divider 10000000 --channel 0
distrib.py 0 0x4A --divider 10000000 --channel 1
distrib.py 0 0x4A --divider 5000000 --channel 2
distrib.py 0 0x4A --divider 5000000 --channel 3
```

## DPll: Digital PLL management

`dpll.py` to operate and manage the Digital PLL core.   
`dpll.py` supports all of its operations at once.

* `--free-run` : force clock to free running state manually 
* `--holdover` : force clock to holdover state manually

```shell
# force freerunning state manually
dpll.py 0 0x48 --free-run
```

* `--tuning` : load a new (free running) frequency tuning word
in [Hz]

* `--tuning-apply`: apply (free running) frequency tuning word

These two operations can be conveniently combined

```shell
# set new tuning word
dpll.py 0 0x48 --tuning 10E3
# modify slightly and apply right away
dpll.py 0 0x48 --tuning 10.1E3 --tuning-apply
```

* `--pull-in-low` and `--pull-in-high` set (as binary mask)
the DDS tuning range. These flag expect a hex binary mask

```shell
# limit range
dpll.py 0 0x48 --pull-in-low 0x0FFF
dpll.py 0 0x48 --pull-in-high 0x3FFF
# same operation 
dpll.py 0 0x48 --pull-in-low 0x0FFF --pull-in-high 0x3FFF
```

* `--open-offset` : phase offset applied in open loop, in [% of pi rad] 
```shell
# pi/2 offset 
dpll.py 0 0x48 --open-offset 50
# pi/4 offset 
dpll.py 0 0x48 --open-offset 25 
# 3pi/4 offset 
dpll.py 0 0x48 --open-offset 75 
# complex value
dpll.py 0 0x48 --open-offset 33.333 
```

* `--lock-offset` : phase offset applied in closed loop, in [s]
```shell
# apply static 10E-3 sec offset
dpll.py 0 0x48 --lock-offset 10E-3
# apply static 10E-6 sec offset
dpll.py 0 0x48 --lock-offset 10E-6
```

* `--inc-step-size` : Phase lock offset incremental step size [sec / step]
```shell
# apply 10E-12 (10ps) increment per step
dpll.py 0 0x48 --inc-step-size 10E-12
```

* `--phase-slew-limit` : set phase slew rate limit in sec /sec 
```shell
# set limit to 10E-9 (10 ns)/s
dpll.py 0 0x48 --phase-slew-limit 10E-9
```

* `--history-acc-timer`: history accumulation timer / period in [s]
* `-h` for listing all other supported operations

# Reference input

`ref-input.py` to manage input reference signals.

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
Otherwise, select internal units with related flag.

`--clear` is used to recover (unset) a power down operaion.

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

`irq.py` allows several operations.
* `--pin [mode]` : control how the IRQ output pin operates

```shell
# set CMOS + active high logic
irq.py --pin cmos-high 0 0x43
# set CMOS + active low logic
irq.py --pin cmos-low 0 0x43
```

All other flags are discarded when using `--pin [mode]` because
it is a special opmode.

* `--enable` : to enable some IRQ events.
`--all` will enable all known IRQ events.
Otherwise, user must specify which one to enable:

```shell
# Enable all IRQ events
irq.py --enable --all

# Enable dpll freq lock + phase lock events
irq.py --enable --dpll-freq-lock --dpll-phase-lock
# Enable dpll holdover + free run events
irq.py --enable --dpll-holdover --dpll-free-run
# Enable REFA reference validation event
irq.py --enable --refa-validated
```

Use `-h` to enumerate all known IRQ events.

* `--disable` : to disable some IRQ events.
`--all` will disable all known IRQ events.
Otherwise, user must specify which one to disable:

```shell
# Disable all IRQ events
irq.py --disable all

# Disable refaa/b/bb/c/cc/d/dd related events
# in scenario we're only interested in ref-a
irq.py --disable --refaa \
    --refb --refbb \
    --refc --refcc \
    --refd --refdd
```

* `--clear` : to clear pending IRQ events.
`--all` will clear all known IRQ events (whether it's pending or not).
Otherwise, user must specify which event we are about to clear:

```shell
# clears all possible events
irq.py --clear all 
# clear acknowledged Phase Locking event
irq.py --clear --dpll-phase-lock 
```

## Typical configuration flow

```shell
# load a register map
regmap.py --load data.json --quiet 0 0x4A
# initiate calibration
calib.py 0 0x4A
```
