class Timer:
    def __init__(self):
        self.unit_name = "Timer"
        self.on_active_sec = None
        self.on_boot_sec = None
        self.on_startup_sec = None
        self.on_unit_active_sec = None
        self.on_unit_inactive_sec = None
        self.on_calendar = None
        self.accuracy_sec = None
        self.unit = None
        self.persistent = None
        self.wake_system = None
