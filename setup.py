#! /usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="adi-ad9548",
    scripts=[
        "calib.py",
        "irq.py",
        "misc.py",
        "mx-pin.py",
        "power-down.py",
        "profile.py",
        "regmap.py",
        "reset.py",
        "status.py",
    ],
)
