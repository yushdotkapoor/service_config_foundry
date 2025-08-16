import pytest

from service_config_foundry.sections import (Automount, Install, Mount, Path,
                                             Scope, ServiceSection, Slice,
                                             Socket, Swap, Timer, Unit)


class TestUnit:
    """Test cases for Unit section."""

    def test_unit_initialization(self):
        """Test Unit section initialization."""
        unit = Unit()
        assert unit.unit_name == "Unit"
        assert unit.description is None
        assert unit.documentation is None
        assert unit.requires is None
        assert unit.wants is None
        assert unit.binds_to is None
        assert unit.before is None
        assert unit.after is None
        assert unit.conflicts is None
        assert unit.condition is None
        assert unit.assert_ is None

    def test_unit_attribute_setting(self):
        """Test setting Unit section attributes."""
        unit = Unit()
        unit.description = "Test Service"
        unit.after = "network.target"
        unit.wants = "multi-user.target"

        assert unit.description == "Test Service"
        assert unit.after == "network.target"
        assert unit.wants == "multi-user.target"


class TestServiceSection:
    """Test cases for ServiceSection section."""

    def test_service_initialization(self):
        """Test ServiceSection section initialization."""
        service = ServiceSection()
        assert service.unit_name == "Service"
        assert hasattr(service, "type")
        assert hasattr(service, "exec_start")
        assert hasattr(service, "exec_stop")
        assert hasattr(service, "user")
        assert hasattr(service, "working_directory")
        assert hasattr(service, "restart")
        assert hasattr(service, "timeout_start_sec")
        assert hasattr(service, "watchdog_sec")

    def test_service_attribute_setting(self):
        """Test setting ServiceSection section attributes."""
        service = ServiceSection()
        service.type = "simple"
        service.exec_start = "/usr/bin/test"
        service.user = "testuser"
        service.restart = "always"

        assert service.type == "simple"
        assert service.exec_start == "/usr/bin/test"
        assert service.user == "testuser"
        assert service.restart == "always"


class TestInstall:
    """Test cases for Install section."""

    def test_install_initialization(self):
        """Test Install section initialization."""
        install = Install()
        assert install.unit_name == "Install"
        assert hasattr(install, "wanted_by")
        assert hasattr(install, "required_by")
        assert hasattr(install, "alias")
        assert hasattr(install, "also")

    def test_install_attribute_setting(self):
        """Test setting Install section attributes."""
        install = Install()
        install.wanted_by = "multi-user.target"
        install.required_by = "graphical.target"
        install.alias = "test-service"

        assert install.wanted_by == "multi-user.target"
        assert install.required_by == "graphical.target"
        assert install.alias == "test-service"


class TestSocket:
    """Test cases for Socket section."""

    def test_socket_initialization(self):
        """Test Socket section initialization."""
        socket = Socket()
        assert socket.unit_name == "Socket"
        assert hasattr(socket, "listen_stream")
        assert hasattr(socket, "listen_datagram")
        assert hasattr(socket, "listen_sequential_packet")
        assert hasattr(socket, "socket_user")
        assert hasattr(socket, "socket_group")
        assert hasattr(socket, "socket_mode")
        assert hasattr(socket, "accept")
        assert hasattr(socket, "service")

    def test_socket_attribute_setting(self):
        """Test setting Socket section attributes."""
        socket = Socket()
        socket.listen_stream = "0.0.0.0:8080"
        socket.socket_user = "www-data"
        socket.socket_group = "www-data"
        socket.socket_mode = "0660"

        assert socket.listen_stream == "0.0.0.0:8080"
        assert socket.socket_user == "www-data"
        assert socket.socket_group == "www-data"
        assert socket.socket_mode == "0660"


class TestTimer:
    """Test cases for Timer section."""

    def test_timer_initialization(self):
        """Test Timer section initialization."""
        timer = Timer()
        assert timer.unit_name == "Timer"
        assert hasattr(timer, "on_active_sec")
        assert hasattr(timer, "on_boot_sec")
        assert hasattr(timer, "on_startup_sec")
        assert hasattr(timer, "on_unit_active_sec")
        assert hasattr(timer, "on_unit_inactive_sec")
        assert hasattr(timer, "on_calendar")
        assert hasattr(timer, "accuracy_sec")
        assert hasattr(timer, "persistent")
        assert hasattr(timer, "wake_system")
        assert hasattr(timer, "unit")

    def test_timer_attribute_setting(self):
        """Test setting Timer section attributes."""
        timer = Timer()
        timer.on_calendar = "*-*-* 02:00:00"
        timer.persistent = True
        timer.accuracy_sec = "1us"

        assert timer.on_calendar == "*-*-* 02:00:00"
        assert timer.persistent is True
        assert timer.accuracy_sec == "1us"


class TestMount:
    """Test cases for Mount section."""

    def test_mount_initialization(self):
        """Test Mount section initialization."""
        mount = Mount()
        assert mount.unit_name == "Mount"
        assert hasattr(mount, "what")
        assert hasattr(mount, "where")
        assert hasattr(mount, "type")
        assert hasattr(mount, "options")
        assert hasattr(mount, "sloppy_options")
        assert hasattr(mount, "directory_mode")
        assert hasattr(mount, "timeout_sec")

    def test_mount_attribute_setting(self):
        """Test setting Mount section attributes."""
        mount = Mount()
        mount.what = "/dev/sda1"
        mount.where = "/mnt/data"
        mount.type = "ext4"
        mount.options = "defaults"

        assert mount.what == "/dev/sda1"
        assert mount.where == "/mnt/data"
        assert mount.type == "ext4"
        assert mount.options == "defaults"


class TestAutomount:
    """Test cases for Automount section."""

    def test_automount_initialization(self):
        """Test Automount section initialization."""
        automount = Automount()
        assert automount.unit_name == "Automount"
        assert hasattr(automount, "where")
        assert hasattr(automount, "directory_mode")

    def test_automount_attribute_setting(self):
        """Test setting Automount section attributes."""
        automount = Automount()
        automount.where = "/mnt/auto"
        automount.directory_mode = "0755"

        assert automount.where == "/mnt/auto"
        assert automount.directory_mode == "0755"


class TestSwap:
    """Test cases for Swap section."""

    def test_swap_initialization(self):
        """Test Swap section initialization."""
        swap = Swap()
        assert swap.unit_name == "Swap"
        assert hasattr(swap, "what")
        assert hasattr(swap, "priority")
        assert hasattr(swap, "options")
        assert hasattr(swap, "timeout_sec")

    def test_swap_attribute_setting(self):
        """Test setting Swap section attributes."""
        swap = Swap()
        swap.what = "/swapfile"
        swap.priority = "100"
        swap.options = "defaults"

        assert swap.what == "/swapfile"
        assert swap.priority == "100"
        assert swap.options == "defaults"


class TestPath:
    """Test cases for Path section."""

    def test_path_initialization(self):
        """Test Path section initialization."""
        path = Path()
        assert path.unit_name == "Path"
        assert hasattr(path, "path_exists")
        assert hasattr(path, "path_exists_glob")
        assert hasattr(path, "path_changed")
        assert hasattr(path, "path_modified")
        assert hasattr(path, "directory_not_empty")
        assert hasattr(path, "unit")
        assert hasattr(path, "make_directory")
        assert hasattr(path, "directory_mode")

    def test_path_attribute_setting(self):
        """Test setting Path section attributes."""
        path = Path()
        path.path_exists = "/tmp/trigger"
        path.unit = "test.service"
        path.make_directory = True

        assert path.path_exists == "/tmp/trigger"
        assert path.unit == "test.service"
        assert path.make_directory is True


class TestSlice:
    """Test cases for Slice section."""

    def test_slice_initialization(self):
        """Test Slice section initialization."""
        slice_obj = Slice()
        assert slice_obj.unit_name == "Slice"
        assert hasattr(slice_obj, "c_p_u_accounting")
        assert hasattr(slice_obj, "memory_accounting")
        assert hasattr(slice_obj, "block_i_o_accounting")

    def test_slice_is_instantiable(self):
        """Test that Slice can be instantiated."""
        slice_obj = Slice()
        assert slice_obj is not None


class TestScope:
    """Test cases for Scope section."""

    def test_scope_initialization(self):
        """Test Scope section initialization."""
        scope = Scope()
        assert scope.unit_name == "Scope"
        assert hasattr(scope, "c_p_u_accounting")
        assert hasattr(scope, "memory_accounting")
        assert hasattr(scope, "block_i_o_accounting")

    def test_scope_attribute_setting(self):
        """Test setting Scope section attributes."""
        scope = Scope()
        scope.c_p_u_accounting = True
        scope.memory_accounting = True

        assert scope.c_p_u_accounting is True
        assert scope.memory_accounting is True
