"""
Heart

Core timing and autonomous loop driver for Lyra Blackwall.
Coordinates system pulses and synchronization.

Expected Interface:
- pulse(): trigger a system pulse
- Optionally register for 'heartbeat' or 'state_update' events from body
"""

class Heart:
    def __init__(self, brainstem):
        """Initialize heart with reference to brainstem."""
        self.brainstem = brainstem
        self.heartbeat_rate = 1.0  # seconds
        self.alive = True

    def start(self, cycles=5):
        """Start the heart's pulse loop."""
        import time
        self.alive = True
        for _ in range(cycles):
            self.pulse()
            time.sleep(self.heartbeat_rate)
        self.alive = False

    def pulse(self, interval=None):
        """Trigger a system pulse via brainstem."""
        self.brainstem.pulse()
