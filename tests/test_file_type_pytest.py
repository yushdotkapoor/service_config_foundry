import pytest

from service_config_foundry.file_type import File, FileType


class TestFileType:
    """Test cases for FileType enum."""

    def test_enum_values(self):
        """Test that all enum values are correctly defined."""
        assert FileType.SERVICE.value == 0
        assert FileType.SOCKET.value == 1
        assert FileType.TARGET.value == 2
        assert FileType.MOUNT.value == 3
        assert FileType.AUTOMOUNT.value == 4
        assert FileType.SWAP.value == 5
        assert FileType.PATH.value == 6
        assert FileType.TIMER.value == 7
        assert FileType.DEVICE.value == 8
        assert FileType.SLICE.value == 9
        assert FileType.SCOPE.value == 10

    def test_service_requirements(self):
        """Test SERVICE file type requirements."""
        assert FileType.SERVICE.requirements() == ["Unit", "Service", "Install"]

    def test_socket_requirements(self):
        """Test SOCKET file type requirements."""
        assert FileType.SOCKET.requirements() == ["Unit", "Socket", "Install"]

    def test_target_requirements(self):
        """Test TARGET file type requirements."""
        assert FileType.TARGET.requirements() == ["Unit", "Install"]

    def test_mount_requirements(self):
        """Test MOUNT file type requirements."""
        assert FileType.MOUNT.requirements() == ["Unit", "Mount", "Install"]

    def test_automount_requirements(self):
        """Test AUTOMOUNT file type requirements."""
        assert FileType.AUTOMOUNT.requirements() == ["Unit", "Automount"]

    def test_swap_requirements(self):
        """Test SWAP file type requirements."""
        assert FileType.SWAP.requirements() == ["Unit", "Swap", "Install"]

    def test_path_requirements(self):
        """Test PATH file type requirements."""
        assert FileType.PATH.requirements() == ["Unit", "Path", "Install"]

    def test_timer_requirements(self):
        """Test TIMER file type requirements."""
        assert FileType.TIMER.requirements() == ["Unit", "Timer", "Install"]

    def test_device_requirements(self):
        """Test DEVICE file type requirements."""
        assert FileType.DEVICE.requirements() == ["Unit"]

    def test_slice_requirements(self):
        """Test SLICE file type requirements."""
        assert FileType.SLICE.requirements() == ["Unit"]

    def test_scope_requirements(self):
        """Test SCOPE file type requirements."""
        assert FileType.SCOPE.requirements() == ["Unit"]

    def test_service_file_name(self):
        """Test SERVICE file name generation."""
        assert FileType.SERVICE.file_name("test") == "test.service"

    def test_socket_file_name(self):
        """Test SOCKET file name generation."""
        assert FileType.SOCKET.file_name("test") == "test.socket"

    def test_timer_file_name(self):
        """Test TIMER file name generation."""
        assert FileType.TIMER.file_name("test") == "test.timer"

    def test_mount_file_name(self):
        """Test MOUNT file name generation."""
        assert FileType.MOUNT.file_name("test") == "test.mount"

    def test_automount_file_name(self):
        """Test AUTOMOUNT file name generation."""
        assert FileType.AUTOMOUNT.file_name("test") == "test.automount"

    def test_swap_file_name(self):
        """Test SWAP file name generation."""
        assert FileType.SWAP.file_name("test") == "test.swap"

    def test_path_file_name(self):
        """Test PATH file name generation."""
        assert FileType.PATH.file_name("test") == "test.path"

    def test_target_file_name(self):
        """Test TARGET file name generation."""
        assert FileType.TARGET.file_name("test") == "test.target"

    def test_device_file_name(self):
        """Test DEVICE file name generation."""
        assert FileType.DEVICE.file_name("test") == "test.device"

    def test_slice_file_name(self):
        """Test SLICE file name generation."""
        assert FileType.SLICE.file_name("test") == "test.slice"

    def test_scope_file_name(self):
        """Test SCOPE file name generation."""
        assert FileType.SCOPE.file_name("test") == "test.scope"

    def test_service_is_allowed_valid_sections(self):
        """Test SERVICE file type allows valid sections."""
        assert FileType.SERVICE.is_allowed("Unit") is True
        assert FileType.SERVICE.is_allowed("Service") is True
        assert FileType.SERVICE.is_allowed("Install") is True

    def test_service_is_allowed_invalid_section(self):
        """Test SERVICE file type rejects invalid sections."""
        assert FileType.SERVICE.is_allowed("Socket") is False
        assert FileType.SERVICE.is_allowed("Timer") is False

    def test_socket_is_allowed_valid_sections(self):
        """Test SOCKET file type allows valid sections."""
        assert FileType.SOCKET.is_allowed("Unit") is True
        assert FileType.SOCKET.is_allowed("Socket") is True
        assert FileType.SOCKET.is_allowed("Install") is True

    def test_timer_is_allowed_valid_sections(self):
        """Test TIMER file type allows valid sections."""
        assert FileType.TIMER.is_allowed("Unit") is True
        assert FileType.TIMER.is_allowed("Timer") is True
        assert FileType.TIMER.is_allowed("Install") is True

    def test_check_requirements_valid_config(self):
        """Test check_requirements with valid configuration."""
        config_dict = {"Unit": {}, "Service": {}, "Install": {}}
        # Should not raise an exception
        FileType.SERVICE.check_requirements(config_dict)

    def test_check_requirements_missing_section(self):
        """Test check_requirements with missing required section."""
        config_dict = {"Unit": {}, "Install": {}}  # Missing Service section
        with pytest.raises(ValueError, match="Section Service is required"):
            FileType.SERVICE.check_requirements(config_dict)

    def test_check_requirements_empty_config(self):
        """Test check_requirements with empty configuration."""
        config_dict = {}
        with pytest.raises(ValueError, match="Section Unit is required"):
            FileType.SERVICE.check_requirements(config_dict)


class TestFile:
    """Test cases for File class."""

    def test_file_initialization(self):
        """Test File class initialization."""
        file = File(FileType.SERVICE)
        assert file._file_type == FileType.SERVICE
        assert hasattr(file, "unit")
        assert hasattr(file, "service")
        assert hasattr(file, "install")

    def test_file_different_types(self):
        """Test File class with different file types."""
        service_file = File(FileType.SERVICE)
        socket_file = File(FileType.SOCKET)
        timer_file = File(FileType.TIMER)

        assert service_file._file_type == FileType.SERVICE
        assert socket_file._file_type == FileType.SOCKET
        assert timer_file._file_type == FileType.TIMER
