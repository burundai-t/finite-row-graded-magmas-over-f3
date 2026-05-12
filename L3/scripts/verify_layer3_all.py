#!/usr/bin/env python3
"""Lean cumulative Layer 3 verifier runner.

Runs the cumulative verifier stack without relying on packaged logs or manifest files.
Sympy-dependent early scripts are reported explicitly as dependency-skipped if sympy is absent.
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=ROOT/"scripts"
STACK=[
 "verify_layer3_linearization_final.py",
 "verify_layer3_frontA.py",
 "verify_layer3_frontB.py",
 "verify_layer3_frontB_envelope.py",
 "verify_layer3_frontC.py",
 "verify_layer3_frontF.py",
 "verify_layer3_frontD.py",
 "verify_layer3_frontE.py",
 "verify_layer3_frontG.py",
 "verify_layer3_frontH.py",
]
def run(script):
    path=SCRIPTS/script
    if not path.exists(): return "FAIL","missing script"
    proc=subprocess.run([sys.executable,str(path)],cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=240)
    out=proc.stdout.strip()
    if proc.returncode==0 and "PASS" in out: return "PASS",out.splitlines()[0]
    if "ModuleNotFoundError: No module named 'sympy'" in out: return "SKIP","optional dependency missing: sympy"
    return "FAIL",out[-1000:].replace("\n"," | ")
def main():
    rows=[]
    for script in STACK:
        status,detail=run(script); rows.append((script,status,detail)); print(f"{status:4} {script} :: {detail}")
    if any(s=="FAIL" for _,s,_ in rows):
        print("Layer 3 cumulative verifier clean runner: FAIL"); return 1
    if any(s=="SKIP" for _,s,_ in rows):
        print("Layer 3 cumulative verifier clean runner: PASS with explicit dependency skips"); return 0
    print("Layer 3 cumulative verifier clean runner: PASS"); return 0
if __name__=="__main__":
    raise SystemExit(main())
