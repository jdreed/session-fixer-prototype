#!/usr/bin/env python

from distutils.core import setup
from glob import glob

setup(name='debathena-account-repair',
      version='1.0',
      description='Account Repair Wizard',
      author='Debathena Project',
      author_email='debathena@mit.edu',
      scripts=['account-repair-wizard'],
      data_files=[('/usr/share/debathena-account-repair',
                   ['account-repair-wizard.ui']),
                  ('/usr/share/debathena-account-repair/actions',
                   glob('actions/*')),
                  ('/usr/lib/debathena-account-repair/scripts',
                   glob('scripts/*'))]
)
