"""
Body (Bloodstream)

Acts as the main hub and signal carrier for the system. The body (bloodstream) routes data, events, and signals between all other modules, ensuring that every part of Lyra Blackwall is connected and synchronized. It is the central communication and integration layer.

Core Responsibilities:
- Central hub for all body part modules (e.g., eyes, ears, hands).
- Passes messages between brainstem and peripheral systems.
- Regulates pulse (heartbeat) and distributes heartbeat signals.
- Interconnects spine, nerves, skin, and external interface layers.

Special Design Notes:
- Body operates as neutral carrier — does not transform data, only transmits.
- Serves as root dispatcher and heartbeat propagator.
- Can dynamically include new modules if added to the body schema.

Module Interface Expectations:
- Routable modules should implement:
    - receive_signal(source, payload): handle incoming messages
    - pulse(interval): respond to heartbeat (optional)
    - act(command): perform an action (for output modules)
    - speak(response, fragment_weights): output a response (for mouth)

Event System:
- Modules can register callbacks for named events (e.g., 'heartbeat', 'state_update').
- Body will notify all registered listeners when an event is emitted.
"""

class Body:
    def __init__(self):
        """Initialize body state, module registry, and event listeners."""
        self.state = {}
        self.modules = {}  # Registry of connected modules
        self.event_listeners = {}  # event_name -> list of callbacks

    def register_module(self, name, module):
        """Register a new module for routing/signaling."""
        self.modules[name] = module

    def route_signal(self, source, destination, payload):
        """Handle inter-module messaging."""
        if destination in self.modules:
            dest_module = self.modules[destination]
            if hasattr(dest_module, 'receive_signal'):
                dest_module.receive_signal(source, payload)
        # Optionally log or handle missing destination

    def distribute_heartbeat(self, interval):
        """Emit cycle beat to activate or pulse fragments/modules."""
        for module in self.modules.values():
            if hasattr(module, 'pulse'):
                module.pulse(interval)
        self.emit_event('heartbeat', interval=interval)

    def update_internal_state(self, metrics):
        """Integrate metrics from lungs, heart, etc."""
        self.state.update(metrics)
        self.emit_event('state_update', metrics=metrics)

    def receive_input(self, sensor_data):
        """Receive and format input from eyes, ears, etc."""
        if 'brainstem' in self.modules:
            self.modules['brainstem'].relay_input(sensor_data)
        self.emit_event('input_received', data=sensor_data)

    def send_output(self, action_request):
        """Send actions to mouth, hands, etc."""
        if 'mouth' in self.modules:
            self.modules['mouth'].speak(action_request, {})
        if 'hands' in self.modules:
            self.modules['hands'].act(action_request)
        self.emit_event('output_sent', action=action_request)

    # --- Event/Callback System ---
    def on(self, event_name, callback):
        """Register a callback for a named event."""
        if event_name not in self.event_listeners:
            self.event_listeners[event_name] = []
        self.event_listeners[event_name].append(callback)

    def emit_event(self, event_name, **kwargs):
        """Notify all listeners of a named event."""
        for callback in self.event_listeners.get(event_name, []):
            callback(**kwargs)

# --- Example: Dynamic Module Registration and Event Listening ---
if __name__ == "__main__":
    class DummyModule:
        def receive_signal(self, source, payload):
            print(f"[DummyModule] Received from {source}: {payload}")
        def pulse(self, interval):
            print(f"[DummyModule] Pulse received: {interval}s")
    body = Body()
    dummy = DummyModule()
    body.register_module('dummy', dummy)
    body.on('heartbeat', lambda interval: print(f"[Event] Heartbeat: {interval}s"))
    body.route_signal('test_source', 'dummy', {'msg': 'Hello'})
    body.distribute_heartbeat(1.0)
