#!/usr/bin/env python3

# CRITICAL: Import Unicode safety layer FIRST to prevent encoding errors
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from utils.unicode_safe_output import setup_unicode_safe_output
setup_unicode_safe_output()

import streamlit as st
import time
from threading import Thread


class WorkerThread(Thread):
    def __init__(self, delay):
        super().__init__()
        self.delay = delay
        self.return_value = None

    def run(self):
        start_time = time.time()
        time.sleep(self.delay)
        end_time = time.time()
        self.return_value = f"start: {start_time}, end: {end_time}"


delays = [5, 4, 3, 2, 1]
threads = [WorkerThread(delay) for delay in delays]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
for i, thread in enumerate(threads):
    st.header(f"Thread {i}")
    st.write(thread.return_value)

st.button("Rerun")
