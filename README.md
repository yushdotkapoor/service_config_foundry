# service_config_foundry

**service_config_foundry** is a Python-based library that simplifies the process of creating, updating, replacing, and deleting systemd service files for Linux users. With this tool, you can easily manage systemd services programmatically, reducing the complexity of writing and maintaining service configuration files manually.

## Features

- Create and manage non-templated systemd service files
- Support for various systemd file types including `.service`, `.timer`, `.socket`, `.mount`, and more
- Programmatic control over file attributes and configurations
- Replace and update existing services without conflicts
- Fully integrated Python API with no external dependencies

## Installation

You can install the library using `pip` directly from the GitHub repository:

```bash
pip install git+https://github.com/yushdotkapoor/service_config_foundry.git
```

Alternatively, clone the repository to get started:

```bash
git clone https://github.com/yushdotkapoor/service_config_foundry.git
cd service_config_foundry
```

## Usage

Below are detailed examples of how to use `service_config_foundry` to create and manage systemd files of various types.

### Example: Creating a Service, Timer, and Socket

```python
from service_config_foundry import Service, ServiceLocation

# Create a new service instance
service = Service("example", service_location=ServiceLocation.GLOBAL, auto_start=False, enable_at_startup=False, force_overwrite=False)

# Configure the service file
service_file = service.service_file
service_file.unit.description = "Example service for demonstration purposes"
service_file.service.user = "yushrajkapoor"
service_file.service.exec_start = "echo Hello, world >> /tmp/example.log"
service_file.install.wanted_by = "multi-user.target"

# Configure the timer file
timer_file = service.timer_file
timer_file.unit.description = "Example timer for demonstration purposes"
timer_file.timer.on_calendar = "*-*-* *:00:00"
timer_file.install.wanted_by = "timers.target"

# Configure the socket file
socket_file = service.socket_file
socket_file.unit.description = "Example socket for demonstration purposes"
socket_file.socket.listen_stream = "/run/example.sock"
socket_file.install.wanted_by = "sockets.target"

# Create or update the service, timer, and socket files
service.update()

# Enable the service to start at boot time
service.enable_service_at_startup()

# Start the service
service.start_service()

# Display the status of the service
service.status()
```

### Output Files

#### `example.service`
```ini
[Unit]
Description = Example service for demonstration purposes

[Service]
User = yushrajkapoor
ExecStart = echo Hello, world >> /tmp/example.log

[Install]
WantedBy = multi-user.target
```

#### `example.timer`
```ini
[Unit]
Description = Example timer for demonstration purposes

[Timer]
OnCalendar = *-*-* *:00:00

[Install]
WantedBy = timers.target
```

#### `example.socket`
```ini
[Unit]
Description = Example socket for demonstration purposes

[Socket]
ListenStream = /run/example.sock

[Install]
WantedBy = sockets.target
```

### Example: Replacing an Existing Service

If you want to replace an existing service configuration, you can use the `replace()` method. This ensures that any old files are removed and replaced with the new configuration.

```python
# Replace the existing service configuration
service.replace()
```

This is particularly useful when you want to ensure that your updates overwrite any conflicting configurations from previous versions of the service.

### Example: Creating Mount and Automount Files

```python
# Configure the mount file
mount_file = service.mount_file
mount_file.unit.description = "Example mount for demonstration purposes"
mount_file.mount.what = "/dev/sda1"
mount_file.mount.where = "/mnt/example"
mount_file.mount.type = "ext4"
mount_file.install.wanted_by = "multi-user.target"

# Configure the automount file
automount_file = service.automount_file
automount_file.unit.description = "Example automount for demonstration purposes"
automount_file.automount.where = "/mnt/example"
automount_file.install.wanted_by = "multi-user.target"

# Create or update the files
service.update()
```

#### `example.mount`
```ini
[Unit]
Description = Example mount for demonstration purposes

[Mount]
What = /dev/sda1
Where = /mnt/example
Type = ext4

[Install]
WantedBy = multi-user.target
```

#### `example.automount`
```ini
[Unit]
Description = Example automount for demonstration purposes

[Automount]
Where = /mnt/example

[Install]
WantedBy = multi-user.target
```

### Example: Creating Swap and Path Files

```python
# Configure the swap file
swap_file = service.swap_file
swap_file.unit.description = "Example swap for demonstration purposes"
swap_file.swap.what = "/swapfile"
swap_file.install.wanted_by = "multi-user.target"

# Configure the path file
path_file = service.path_file
path_file.unit.description = "Example path for demonstration purposes"
path_file.path.path_exists = "/tmp/example"
path_file.install.wanted_by = "multi-user.target"

# Create or update the files
service.update()
```

#### `example.swap`
```ini
[Unit]
Description = Example swap for demonstration purposes

[Swap]
What = /swapfile

[Install]
WantedBy = multi-user.target
```

#### `example.path`
```ini
[Unit]
Description = Example path for demonstration purposes

[Path]
PathExists = /tmp/example

[Install]
WantedBy = multi-user.target
```

### Example: Creating Slice and Scope Files

```python
# Configure the slice file
slice_file = service.slice_file
slice_file.unit.description = "Example slice for demonstration purposes"

# Configure the scope file
scope_file = service.scope_file
scope_file.unit.description = "Example scope for demonstration purposes"
scope_file.scope.slice = "example.slice"

# Create or update the files
service.update()
```

#### `example.slice`
```ini
[Unit]
Description = Example slice for demonstration purposes
```

#### `example.scope`
```ini
[Unit]
Description = Example scope for demonstration purposes

[Scope]
Slice = example.slice
```

### Deleting a Service

To delete a service and its associated files:

```python
service.delete()
```

This will remove all files matching the service name in the systemd directory.

## Configuration Options

`service_config_foundry` supports multiple systemd file types, including:

- `.service` - Main service configuration
- `.socket` - Socket configuration
- `.timer` - Timer configuration
- `.mount` - Mount point configuration
- `.automount` - Automount configuration
- `.swap` - Swap space configuration
- `.path` - Path configuration
- `.slice` - Slice configuration
- `.scope` - Scope configuration

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvement, please open an issue or submit a pull request.

## Contact

- **Author**: Yush Kapoor  
- **Email**: [yushdotkapoor@gmail.com](mailto:yushdotkapoor@gmail.com)  
- **GitHub**: [https://github.com/yushdotkapoor/service_config_foundry](https://github.com/yushdotkapoor/service_config_foundry)

## Acknowledgments

Special thanks to the Linux and Python communities for their inspiration and support in creating this project.
