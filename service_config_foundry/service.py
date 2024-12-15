import os
from sections import *
from service_location import ServiceLocation
from file_type import FileType
from utils import convert_to_snake_case, merge_dicts
from config_parser import CaseSensitiveConfigParser

# The `Service` class represents a system service with various configuration files
# (e.g., service, socket, timer) and provides methods to create, update, replace,
# and delete these configurations.
class Service:
    # Initializes a Service instance with a name, location, and overwrite flag.
    # Sets up default file types associated with the service.
    def __init__(self, name, service_location=ServiceLocation.GLOBAL, force_overwrite=False):
        self.name = name
        self.service_location = service_location
        self.force_overwrite = force_overwrite
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
    def get_path(self, file):
        return self.service_location.directory() + "/" + file.file_name(self.name)
    
    # Yields the configurations of all file types, optionally checking requirements.
    def file_configs(self, requirement_check=True):
        for file in [self.service_file, self.socket_file, self.mount_file, self.automount_file, self.swap_file, self.path_file, self.timer_file]:
            config = file.get_config(requirement_check=requirement_check)
            if config:
                yield file, config
    
    # Checks if any files for the service name already exist in the directory.
    def service_with_name_exists(self):
        files = []
        for file in os.listdir(self.service_location.directory()):
            if file.startswith(f"{self.name}."):
                files.append(file)
        return files

    # Creates the service configuration files.
    def create(self):
        if self.service_with_name_exists() and not self.force_overwrite:
            raise ValueError(f"Service for {self.name} already exists")
        self.replace()

    # Deletes all files associated with the service name.
    def delete(self):
        for file in os.listdir(self.service_location.directory()):
            if file.startswith(f"{self.name}."):
                try:
                    os.remove(os.path.join(self.service_location.directory(), file))
                except PermissionError:
                    print(f"Permission denied: cannot write to {file}. Try running as root or using sudo.")
                    raise

    # Replaces the existing service configuration files with new ones.
    def replace(self):
        config_and_path = {}
        # Prepare configurations and paths for atomic replacement.
        for file, config in self.file_configs():
            path = self.get_path(file)
            config_and_path[path] = config

        # Delete old configurations before writing new ones.
        self.delete()

        # Write the new configurations to their respective files.
        for path, config in config_and_path.items():
            with open(path, "w") as f:
                config.write(f)
    
    # Adds attributes to a file based on the given configuration.
    def add_attributes(self, file, config):
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
        
    # Updates the service with new configurations.
    def update(self):
        temp_service = Service(name=self.name, service_location=self.service_location, force_overwrite=self.force_overwrite)

        # Find relevant files associated with the service.
        relevant_files = []
        for file in os.listdir(temp_service.service_location.directory()):
            if file.startswith(f"{temp_service.name}."):
                relevant_files.append(file)
        
        if not relevant_files:
            raise ValueError(f"No service found for {temp_service.name}")

        # Collect current and new configurations.
        config_and_path = {}
        for file, config in self.file_configs(requirement_check=False):
            path = self.get_path(file)
            config_and_path[path] = config._sections
        
        # Add attributes from relevant files to the temporary service.
        for file in relevant_files:
            config = CaseSensitiveConfigParser()
            config.read(os.path.join(temp_service.service_location.directory(), file))
            temp_service.add_attributes(file, config)

        # Merge the original and new configurations.
        original_config_and_path = {}
        for file, config in temp_service.file_configs(requirement_check=False):
            path = temp_service.get_path(file)
            original_config_and_path[path] = config._sections
        
        final_config_and_path = {}
        for path in set(original_config_and_path.keys()).union(set(config_and_path.keys())):
            config_dict = config_and_path.get(path, None)
            temp_config_dict = original_config_and_path.get(path, None)
            final_config_and_path[path] = merge_dicts(temp_config_dict, config_dict)
        
        # Update attributes and replace the configuration files.
        for path, _ in final_config_and_path.items():
            file = os.path.basename(path)
            self.add_attributes(file, final_config_and_path[path])

        self.replace()
