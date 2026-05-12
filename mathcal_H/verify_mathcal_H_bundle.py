#!/usr/bin/env python3
"""Public-facing wrapper for the mathcal_H hidden-continuation bundle verifier.

This wrapper preserves the internal verifier implementation while giving
README/SUPPORT_INDEX a stable mathcal_H-facing command name.
"""
from __future__ import annotations

import os
import runpy

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, "verify_stage6_bundle.py")
runpy.run_path(TARGET, run_name="__main__")
