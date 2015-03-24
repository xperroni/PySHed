#! /usr/bin/env python
#coding=utf-8

r'''Python binding interface to the shell environment.

    This module makes possible to "import" commands and executables available at
    the underlying shell environment as Python functions. These can then be called
    with options passed as argument lists, eg:

    from pyshed import git

    git('status', '-s')

    All functions imported in the manner above return a batch object when called, which
    serves as an interface to the underlying shell process. See below for more details.
    Functions also support the following optional, named arguments:

    * daemon - if False, the underlying process remains even after the calling script
      terminates (until it terminates by itself, of course).

    * delay - if present, execution halts for the given number of seconds after the
      requested shell call is made.

    * stderr - specifies the standard error channel for the underlying process. Legal
      values are PIPE (which pipes output into the batch object's stderr attribute),
      STDOUT (which redirects output to the same handler used for standard output),
      STDNUL (which sends all output to the null device, i.e. discards it), an existing
      file descriptor (a positive integer), an existing file object, or a string
      containing a file path, which will be open in rewrite mode and be used to record
      outputs.

    * stdout - specifies the standard output channel for the underlying process. Legal
      values are PIPE (which pipes output into the batch object's stderr attribute),
      STDNUL (which sends all output to the null device, i.e. discards it), an existing
      file descriptor (a positive integer), an existing file object, or a string
      containing a file path, which will be open in rewrite mode and be used to record
      outputs.
'''

__license__ = r'''
Copyright (c) Helio Perroni Filho <xperroni@gmail.com>

This file is part of Skeye.

Skeye is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Skeye is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Skeye. If not, see <http://www.gnu.org/licenses/>.
'''

__version__ = '2015-03-24'

import subprocess
import sys

from os.path import dirname, exists
from os.path import join as joinpath
from platform import system
from subprocess import Popen
from sys import modules
from time import sleep


PIPE = subprocess.PIPE
STDOUT = subprocess.STDOUT
STDNUL = open('NUL' if system() == 'Windows' else '/dev/null', 'w')


class batch(Popen):
    r'''A running shell command or script.

        The batch class inherits from Popen, adding several customizations and
        extensions:

        * By default both standard and error outputs are collected in the stdout
          attribute. This can be changed at instantiation time using the named
          arguments 'stdout' and 'stderr';

        * Whereas Popen objects try to remain alive for as long as the
          underlying process is active, batch objects work the other way around
          by terminating the process (if not yet finished) when they're selected
          for garbage collection (the original behaviour can be restored by
          entering the 'daemon' named argument with a value of False);

        * batch objects are iterable, returning the next (right-trimmed) line
          of output at each iteration;

        * batch objects are also their own context managers, terminating the
          underlying process (if not yet finished) when the context is exited;

        * Finally, batch objects implement the close() method, which terminates the
          underlying process if it hasn't yet finished, and does nothing otherwise.
    '''
    def __init__(self, command, *args, **options):
        args = (command,) + args
        options.setdefault('stdout', PIPE)
        options.setdefault('stderr', STDOUT)

        if isinstance(options['stdout'], basestring):
            options['stdout'] = open(options['stdout'], 'w')

        self.daemon = options.pop('daemon', True)
        Popen.__init__(self, args, **options)

    def __del__(self):
        if self.daemon:
            self.close()
        else:
            Popen.__del__(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def __iter__(self):
        return self

    def close(self):
        if self.returncode != None:
            return

        try:
            self.terminate()
        except:
            pass

    def next(self):
        return self.stdout.next().rstrip()


class batcher(object):
    r'''Interface for a command or executable accessible from the underlying shell environment.

        batcher objects are created automatically in response to import requests to the pyshed
        module.
    '''
    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **options):
        delay = options.pop('delay', 0)

        process = batch(self.name, *[str(arg) for arg in args], **options)

        if delay > 0:
            sleep(delay)

        return process


class pyshed_module(object):
    def __init__(self, module):
        self.module = module

    def __getattr__(self, name):
        try:
            return getattr(self.module, name)
        except AttributeError:
            pass

        command = batcher(name)
        setattr(self.module, name, command)
        return command


# Replaces the stock module object with a customized one.
modules[__name__] = pyshed_module(modules[__name__])
