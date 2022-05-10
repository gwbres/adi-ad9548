#! /usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="adi-ad9548",
    scripts=[
        "ad9548.py",
        "calib.py",
        "distrib.py",
        "dpll.py",
        "irq.py",
        "mx-pin.py",
        "power-down.py",
        "profile.py",
        "ref-input.py",
        "regmap.py",
        "reset.py",
        "status.py",
    ],
)
