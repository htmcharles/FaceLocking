from __future__ import annotations

import utils.http_session
import utils.transport
import utils.session
import runpy


if __name__ == "__main__":
    # Keep the original `python face_lock.py ...` command working by
    # delegating to the package module.
    runpy.run_module("src.face_lock", run_name="__main__")

