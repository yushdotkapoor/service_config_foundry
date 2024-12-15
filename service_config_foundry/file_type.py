import enum
from .sections import *
from .utils import convert_to_camel_case
from .config_parser import CaseSensitiveConfigParser

# `FileType` is an enumeration that defines various systemd file types, such as service, socket, and timer.
# Each file type corresponds to a specific configuration file in the systemd ecosystem.
class FileType(enum.Enum):
    # Defines the file types with their associated integer values.
    SERVICE, SOCKET, TARGET, MOUNT, AUTOMOUNT, SWAP, PATH, TIMER, DEVICE, SLICE, SCOPE = range(11)

    # Initializes default attributes for each file type. These attributes represent sections
    # that may be included in the configuration for a file type.
    def __init__(self, *args):
        self._unit = None
        self._install = None
        self._service = None
        self._socket = None
        self._mount = None
        self._automount = None
        self._swap = None
        self._path = None
        self._timer = None

    # Returns a list of required sections for a specific file type.
    def requirements(self):
        if self == FileType.SERVICE:
            return ["Unit", "Service", "Install"]
        elif self == FileType.SOCKET:
            return ["Unit", "Socket", "Install"]
        elif self == FileType.TARGET:
            return ["Unit", "Install"]
        elif self == FileType.MOUNT:
            return ["Unit", "Mount", "Install"]
        elif self == FileType.AUTOMOUNT:
            return ["Unit", "Automount"]
        elif self == FileType.SWAP:
            return ["Unit", "Swap", "Install"]
        elif self == FileType.PATH:
            return ["Unit", "Path", "Install"]
        elif self == FileType.TIMER:
            return ["Unit", "Timer", "Install"]
        elif self == FileType.DEVICE:
            return ["Unit"]
        elif self == FileType.SLICE:
            return ["Unit"]
        elif self == FileType.SCOPE:
            return ["Unit"]

    # Generates a file name for the given file type using the provided `name`.
    # The file name format is `{name}.{file_type}` (e.g., `my_service.service`).
    def file_name(self, name):
        tag = ""
        if self == FileType.SERVICE:
            tag = "service"
        elif self == FileType.SOCKET:
            tag = "socket"
        elif self == FileType.TARGET:
            tag = "target"
        elif self == FileType.MOUNT:
            tag = "mount"
        elif self == FileType.AUTOMOUNT:
            tag = "automount"
        elif self == FileType.SWAP:
            tag = "swap"
        elif self == FileType.PATH:
            tag = "path"
        elif self == FileType.TIMER:
            tag = "timer"
        elif self == FileType.DEVICE:
            tag = "device"
        elif self == FileType.SLICE:
            tag = "slice"
        elif self == FileType.SCOPE:
            tag = "scope"

        return f"{name}.{tag}"
    
    # Checks if the required sections are present in the provided configuration dictionary.
    def check_requirements(self, config_dict):
        required = self.requirements()
        for section in required:
            if section not in config_dict:
                raise ValueError(f"Section {section} is required in {self} file")
    
    # Creates a configuration parser from the object's attributes and validates the requirements if specified.
    def get_config(self, requirement_check):
        config_dict = {}
        # Whitelist specifies which attributes should be included in the configuration.
        whitelist = ["_unit", "_install", "_service", "_socket", "_mount", "_automount", "_swap", "_path", "_timer"]
        for section, unit in self.__dict__.items():
            if section in whitelist and unit:
                blacklist = ["unit_name"]  # Exclude specific keys from the configuration.
                for key, value in unit.__dict__.items():
                    if key not in blacklist and value:
                        # Convert keys to camel case and add them to the config dictionary.
                        config_dict.setdefault(unit.unit_name, {})[convert_to_camel_case(key)] = value
        
        # If the configuration dictionary is empty, return None.
        if not config_dict:
            return None
        
        # Validate the configuration against the required sections if `requirement_check` is True.
        if requirement_check:
            self.check_requirements(config_dict)

        # Create and populate a case-sensitive configuration parser with the dictionary.
        config = CaseSensitiveConfigParser()
        config.read_dict(config_dict, source='<string>')
        
        return config

    # Determines if a given section is allowed in the current file type.
    def is_allowed(self, section):
        if self == FileType.SERVICE:
            return section in ["Unit", "Install", "Service"]
        elif self == FileType.SOCKET:
            return section in ["Unit", "Socket", "Install"]
        elif self == FileType.TARGET:
            return section in ["Unit", "Install"]
        elif self == FileType.MOUNT:
            return section in ["Unit", "Mount", "Install"]
        elif self == FileType.AUTOMOUNT:
            return section in ["Unit", "Automount"]
        elif self == FileType.SWAP:
            return section in ["Unit", "Swap", "Install"]
        elif self == FileType.PATH:
            return section in ["Unit", "Path", "Install"]
        elif self == FileType.TIMER:
            return section in ["Unit", "Timer", "Install"]
        elif self == FileType.DEVICE:
            return section in ["Unit"]
        elif self == FileType.SLICE:
            return section in ["Unit", "Slice"]
        elif self == FileType.SCOPE:
            return section in ["Unit"]

    # Lazy-loaded property that provides access to the `Unit` section.
    @property
    def unit(self):
        if not self.is_allowed("Unit"):
            raise ValueError(f"Unit is not allowed in {self} file")
        
        self._unit = self._unit or Unit()
        return self._unit
    
    # Lazy-loaded property that provides access to the `Install` section.
    @property
    def install(self):
        if not self.is_allowed("Install"):
            raise ValueError(f"Install is not allowed in {self} file")
        
        self._install = self._install or Install()
        return self._install
    
    # Lazy-loaded property that provides access to the `Service` section.
    @property
    def service(self):
        if not self.is_allowed("Service"):
            raise ValueError(f"Service is not allowed in this {self} file")
        
        self._service = self._service or ServiceSection()
        return self._service
    
    # Lazy-loaded property that provides access to the `Socket` section.
    @property
    def socket(self):
        if not self.is_allowed("Socket"):
            raise ValueError(f"Socket is not allowed in {self} file")
        
        self._socket = self._socket or Socket()
        return self._socket
    
    # Lazy-loaded property that provides access to the `Mount` section.
    @property
    def mount(self):
        if not self.is_allowed("Mount"):
            raise ValueError(f"Mount is not allowed in {self} file")
        
        self._mount = self._mount or Mount()
        return self._mount
    
    # Lazy-loaded property that provides access to the `Automount` section.
    @property
    def automount(self):
        if not self.is_allowed("Automount"):
            raise ValueError(f"Automount is not allowed in {self} file")
        
        self._automount = self._automount or Automount()
        return self._automount
    
    # Lazy-loaded property that provides access to the `Swap` section.
    @property
    def swap(self):
        if not self.is_allowed("Swap"):
            raise ValueError(f"Swap is not allowed in {self} file")
        
        self._swap = self._swap or Swap()
        return self._swap
    
    # Lazy-loaded property that provides access to the `Path` section.
    @property
    def path(self):
        if not self.is_allowed("Path"):
            raise ValueError(f"Path is not allowed in {self} file")
        
        self._path = self._path or Path()
        return self._path
    
    # Lazy-loaded property that provides access to the `Timer` section.
    @property
    def timer(self):
        if not self.is_allowed("Timer"):
            raise ValueError(f"Timer is not allowed in {self} file")
        
        self._timer = self._timer or Timer()
        return self._timer
