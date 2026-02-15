#!/usr/bin/env python
# -*- coding: utf-8 -*- #

"""Backward-compatible wrapper for Yak Barber.

This script delegates to the yakbarber package. It exists so that
existing shell scripts (like site_build4.sh) continue to work.
"""

from yakbarber.cli import main

if __name__ == "__main__":
    main()
