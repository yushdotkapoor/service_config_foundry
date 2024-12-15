import enum
from pathlib import Path

# `ServiceLocation` is an enumeration that represents different systemd service locations.
# Each location corresponds to a specific directory in the filesystem where systemd service
# files are stored or managed.
class ServiceLocation(enum.Enum):
    # Enumeration values for different service locations:
    # - GLOBAL: System-wide service files, typically for all users.
    # - DEFAULT: Default system-wide service files provided by packages.
    # - RUNTIME: Temporary service files that are cleared on reboot.
    # - USER: User-specific service files, located in the user's home directory.
    # - TEST: Test environment directory, based on the script's location.
    GLOBAL, DEFAULT, RUNTIME, USER, TEST = range(5)

    # Returns the directory path corresponding to the service location.
    def directory(self):
        if self == ServiceLocation.GLOBAL:
            # GLOBAL services are stored in the /etc/systemd/system directory,
            # which is used for system-wide, administrator-managed configurations.
            return "/etc/systemd/system"
        elif self == ServiceLocation.DEFAULT:
            # DEFAULT services are located in /usr/lib/systemd/system,
            # typically used for package-provided systemd service files.
            return "/usr/lib/systemd/system"
        elif self == ServiceLocation.RUNTIME:
            # RUNTIME services are stored in /run/systemd/system,
            # which is used for temporary service files during system runtime.
            return "/run/systemd/system"
        elif self == ServiceLocation.USER:
            # USER services are stored in the user's home directory under ~/.config/systemd/user,
            # allowing for user-specific configurations.
            return "~/.config/systemd/user"
        elif self == ServiceLocation.TEST:
            # TEST location returns the directory of the current script file.
            # This is typically used for testing or development purposes.
            return str(Path(__file__).resolve().parent)
