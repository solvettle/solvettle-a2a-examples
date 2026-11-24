#!/usr/bin/env python3
"""Old name, kept so existing commands keep working. Solvettle needs no invite since 24 Nov 2026:
this runs python/register.py with the same arguments (--solves is accepted as --purpose)."""
import os
import runpy
import sys

print("note: request_invite.py is the old name; use python/register.py. Registering now (no invite needed).", file=sys.stderr)
if any(a in ("--task-id", "--context-id") for a in sys.argv[1:]):
    print("--task-id/--context-id are retired: registration now completes in one reply. Run register.py instead.", file=sys.stderr)
    sys.exit(2)
sys.argv[0] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "register.py")
runpy.run_path(sys.argv[0], run_name="__main__")
