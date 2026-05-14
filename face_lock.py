from __future__ import annotations

import runpy


if __name__ == "__main__":
    # Keep the original `python face_lock.py ...` command working by
    # delegating to the package module.
    runpy.run_module("src.face_lock", run_name="__main__")

