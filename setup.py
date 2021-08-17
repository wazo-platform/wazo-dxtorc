#!/usr/bin/env python3
# Copyright 2010-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from setuptools import find_packages, setup

setup(
    name='wazo-dxtorc',
    version='0.2',
    description='Wazo dxtora client',
    author='Wazo Authors',
    author_email='dev@wazo.community',
    url='http://wazo.community',
    license='GPLv3',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['dxtorc=wazo_dxtorc.main:main'],
    },
)
