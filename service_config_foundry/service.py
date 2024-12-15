import os
import sys
from collections import defaultdict
from .sections import *
from .service_location import ServiceLocation
from .file_type import FileType
from .utils import convert_to_snake_case, merge_dicts, run_command
from .config_parser import CaseSensitiveConfigParser

# The `Service` class represents a system service with various configuration files
# (e.g., service, socket, timer) and provides methods to create, update, replace,
# and delete these configurations.
class Service:
    # Initializes a Service instance with a name, location, and overwrite flag.
    # Sets up default file types associated with the service.
    def __init__(self, name, service_location=ServiceLocation.GLOBAL, auto_start=True, enable_at_startup=False, force_overwrite=False):
        self.name = name
        self._service_location = service_location
        self._force_overwrite = force_overwrite
        self._auto_start = auto_start
        self._enable_at_startup = enable_at_startup
        # Define file types associated with the service.
        self.service_file = FileType.SERVICE
        self.socket_file = FileType.SOCKET
        self.target_file = FileType.TARGET
        self.mount_file = FileType.MOUNT
        self.automount_file = FileType.AUTOMOUNT
        self.swap_file = FileType.SWAP
        self.path_file = FileType.PATH
        self.timer_file = FileType.TIMER
        self.device_file = FileType.DEVICE
        self.slice_file = FileType.SLICE
        self.scope_file = FileType.SCOPE

    # Returns the full path for a specific configuration file.
    def __get_path(self, file):
        return self._service_location.directory() + "/" + file.file_name(self.name)
    
    # Yields the configurations of all file types, optionally checking requirements.
    def __file_configs(self, requirement_check=True):
        for file in [self.service_file, self.socket_file, self.mount_file, self.automount_file, self.swap_file, self.path_file, self.timer_file]:
            config = file.get_config(requirement_check=requirement_check)
            if config:
                yield file, config
    
    # Checks if any files for the service name already exist in the directory.
    def __service_with_name_exists(self):
        files = []
        for file in os.listdir(self._service_location.directory()):
            if file.startswith(f"{self.name}."):
                files.append(file)
        return files
    
    # Adds attributes to a file based on the given configuration.
    def __add_attributes(self, file, config):
        file_tag = file.split(".")[-1]
        for section, unit in config.items():
            for key, value in unit.items():
                file_tag_dict = {
                    "service": self.service_file, 
                    "socket": self.socket_file, 
                    "target": self.target_file, 
                    "mount": self.mount_file, 
                    "automount": self.automount_file, 
                    "swap": self.swap_file, 
                    "path": self.path_file, 
                    "timer": self.timer_file,
                    "device": self.device_file,
                    "slice": self.slice_file,
                    "scope": self.scope_file
                }

                file_type = file_tag_dict.get(file_tag, None)
                if not file_type:
                    continue

                section_obj = getattr(file_type, section.lower(), None)
                if section_obj:
                    setattr(section_obj, convert_to_snake_case(key), value)
    
    # Enables the service to start at boot time.
    def enable_service_at_startup(self):
        run_command(f"systemctl enable {self.name}")
    
    # Starts the service.
    def start_service(self):
        # Restart the service to apply the new configurations. This will work even if the service is new.
        run_command(f"systemctl restart {self.name}")
    
    # Displays the status of the service.
    def status(self):
        run_command(f"systemctl status {self.name}", use_sudo=False)

    # Creates the service configuration files.
    def create(self):
        if self.__service_with_name_exists() and not self._force_overwrite:
            raise ValueError(f"Service for {self.name} already exists")
        
        self.replace()

    # Deletes all files associated with the service name.
    def delete(self):
        for file in os.listdir(self._service_location.directory()):
            if file.startswith(f"{self.name}."):
                try:
                    os.remove(os.path.join(self._service_location.directory(), file))
                except PermissionError:
                    print(f"Permission denied: cannot write to {file}. Try running as root or using sudo.")
                    sys.exit(1)

    # Replaces the existing service configuration files with new ones.
    def replace(self):
        config_and_path = {}
        # Prepare configurations and paths for atomic replacement.
        for file, config in self.__file_configs():
            path = self.__get_path(file)
            config_dict = defaultdict(list)
            for section, options in config._sections.items():
                config_dict[section] = defaultdict(list, options)
            config_and_path[path] = config_dict

        # Delete old configurations before writing new ones.
        self.delete()

        # Write the new configurations to their respective files.
        for path, config in config_and_path.items():
            try:
                with open(path, "w") as f:
                    config.write(f)
            except PermissionError:
                print(f"Permission denied: cannot write to {path}. Try running as root or using sudo.")
                sys.exit(1)
        
        run_command(f"systemctl daemon-reload")

        if self._auto_start:
            self.start_service()

        if self._enable_at_startup:
            self.enable_service_at_startup()

    # Updates the service with new configurations.
    def update(self):
        temp_service = Service(name=self.name, service_location=self._service_location, force_overwrite=self._force_overwrite)

        # Find relevant files associated with the service.
        relevant_files = []
        for file in os.listdir(temp_service.service_location.directory()):
            if file.startswith(f"{temp_service.name}."):
                relevant_files.append(file)
        
        if not relevant_files:
            raise ValueError(f"No service found for {temp_service.name}")

        # Collect current and new configurations.
        config_and_path = {}
        for file, config in self.__file_configs(requirement_check=False):
            path = self.__get_path(file)
            config_dict = defaultdict(list)
            for section, options in config._sections.items():
                config_dict[section] = defaultdict(list, options)
            config_and_path[path] = config_dict
        
        # Add attributes from relevant files to the temporary service.
        for file in relevant_files:
            config = CaseSensitiveConfigParser()
            config.read(os.path.join(temp_service.service_location.directory(), file))
            temp_service.__add_attributes(file, config)

        # Merge the original and new configurations.
        original_config_and_path = {}
        for file, config in temp_service.__file_configs(requirement_check=False):
            path = temp_service.__get_path(file)
            config_dict = defaultdict(list)
            for section, options in config._sections.items():
                config_dict[section] = defaultdict(list, options)
            original_config_and_path[path] = config_dict
        
        final_config_and_path = {}
        for path in set(original_config_and_path.keys()).union(set(config_and_path.keys())):
            config_dict = config_and_path.get(path, None)
            temp_config_dict = original_config_and_path.get(path, None)
            final_config_and_path[path] = merge_dicts(temp_config_dict, config_dict)
        
        # Update attributes and replace the configuration files.
        for path, _ in final_config_and_path.items():
            file = os.path.basename(path)
            self.__add_attributes(file, final_config_and_path[path])

        self.replace()
