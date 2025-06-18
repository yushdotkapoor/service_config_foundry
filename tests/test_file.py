import pytest
from service_config_foundry.file_type import File, FileType


class TestFile:
    """Test cases for File class."""
    
    def test_file_initialization(self):
        """Test File class initialization."""
        file = File(FileType.SERVICE)
        assert file._file_type == FileType.SERVICE
        assert file._unit is None
        assert file._install is None
        assert file._service is None
        assert file._socket is None
        assert file._mount is None
        assert file._automount is None
        assert file._swap is None
        assert file._path is None
        assert file._timer is None
    
    def test_service_file_sections(self):
        """Test accessing sections in a service file."""
        file = File(FileType.SERVICE)
        
        # Should be able to access allowed sections
        unit = file.unit
        assert unit.unit_name == "Unit"
        
        service = file.service
        assert service.unit_name == "Service"
        
        install = file.install
        assert install.unit_name == "Install"
        
        # Should not be able to access disallowed sections
        with pytest.raises(ValueError, match="Socket is not allowed"):
            _ = file.socket
    
    def test_socket_file_sections(self):
        """Test accessing sections in a socket file."""
        file = File(FileType.SOCKET)
        
        # Should be able to access allowed sections
        unit = file.unit
        assert unit.unit_name == "Unit"
        
        socket = file.socket
        assert socket.unit_name == "Socket"
        
        install = file.install
        assert install.unit_name == "Install"
        
        # Should not be able to access disallowed sections
        with pytest.raises(ValueError, match="Service is not allowed"):
            _ = file.service
    
    def test_timer_file_sections(self):
        """Test accessing sections in a timer file."""
        file = File(FileType.TIMER)
        
        # Should be able to access allowed sections
        unit = file.unit
        timer = file.timer
        install = file.install
        
        assert unit.unit_name == "Unit"
        assert timer.unit_name == "Timer"
        assert install.unit_name == "Install"
        
        # Should not be able to access disallowed sections
        with pytest.raises(ValueError, match="Service is not allowed"):
            _ = file.service
    
    def test_mount_file_sections(self):
        """Test accessing sections in a mount file."""
        file = File(FileType.MOUNT)
        
        # Should be able to access allowed sections
        unit = file.unit
        mount = file.mount
        install = file.install
        
        assert unit.unit_name == "Unit"
        assert mount.unit_name == "Mount"
        assert install.unit_name == "Install"
    
    def test_automount_file_sections(self):
        """Test accessing sections in an automount file."""
        file = File(FileType.AUTOMOUNT)
        
        # Should be able to access allowed sections
        unit = file.unit
        automount = file.automount
        
        assert unit.unit_name == "Unit"
        assert automount.unit_name == "Automount"
        
        # Install section should not be allowed for automount
        with pytest.raises(ValueError, match="Install is not allowed"):
            _ = file.install
    
    def test_swap_file_sections(self):
        """Test accessing sections in a swap file."""
        file = File(FileType.SWAP)
        
        # Should be able to access allowed sections
        unit = file.unit
        swap = file.swap
        install = file.install
        
        assert unit.unit_name == "Unit"
        assert swap.unit_name == "Swap"
        assert install.unit_name == "Install"
    
    def test_path_file_sections(self):
        """Test accessing sections in a path file."""
        file = File(FileType.PATH)
        
        # Should be able to access allowed sections
        unit = file.unit
        path = file.path
        install = file.install
        
        assert unit.unit_name == "Unit"
        assert path.unit_name == "Path"
        assert install.unit_name == "Install"
    
    def test_slice_file_sections(self):
        """Test accessing sections in a slice file."""
        file = File(FileType.SLICE)
        
        # Should be able to access Unit section
        unit = file.unit
        assert unit.unit_name == "Unit"
        
        # Should not be able to access other sections
        with pytest.raises(ValueError, match="Install is not allowed"):
            _ = file.install
    
    def test_scope_file_sections(self):
        """Test accessing sections in a scope file."""
        file = File(FileType.SCOPE)
        
        # Should be able to access Unit section
        unit = file.unit
        assert unit.unit_name == "Unit"
        
        # Should not be able to access Install section
        with pytest.raises(ValueError, match="Install is not allowed"):
            _ = file.install
    
    def test_get_config_empty_file(self):
        """Test getting configuration from an empty file."""
        file = File(FileType.SERVICE)
        config = file.get_config(requirement_check=False)
        assert config is None
    
    def test_get_config_with_data(self):
        """Test getting configuration from a file with data."""
        file = File(FileType.SERVICE)
        
        # Set some attributes
        file.unit.description = "Test Service"
        file.unit.after = "network.target"
        file.service.type = "simple"
        file.service.exec_start = "/usr/bin/test"
        file.install.wanted_by = "multi-user.target"
        
        config = file.get_config(requirement_check=False)
        
        assert config is not None
        assert "Unit" in config
        assert "Service" in config
        assert "Install" in config
        
        assert config["Unit"]["Description"] == "Test Service"
        assert config["Unit"]["After"] == "network.target"
        assert config["Service"]["Type"] == "simple"
        assert config["Service"]["ExecStart"] == "/usr/bin/test"
        assert config["Install"]["WantedBy"] == "multi-user.target"
    
    def test_get_config_with_requirement_check_valid(self):
        """Test getting configuration with requirement check - valid config."""
        file = File(FileType.SERVICE)
        
        # Set required attributes
        file.unit.description = "Test Service"
        file.service.type = "simple"
        file.install.wanted_by = "multi-user.target"
        
        # Should not raise an exception
        config = file.get_config(requirement_check=True)
        assert config is not None
    
    def test_get_config_with_requirement_check_invalid(self):
        """Test getting configuration with requirement check - invalid config."""
        file = File(FileType.SERVICE)
        
        # Set only some required attributes (missing Service section)
        file.unit.description = "Test Service"
        file.install.wanted_by = "multi-user.target"
        
        # Should raise an exception due to missing Service section
        with pytest.raises(ValueError, match="Section Service is required"):
            file.get_config(requirement_check=True)
    
    def test_lazy_loading_sections(self):
        """Test that sections are lazy-loaded."""
        file = File(FileType.SERVICE)
        
        # Initially, sections should be None
        assert file._unit is None
        assert file._service is None
        assert file._install is None
        
        # Accessing a section should create it
        unit = file.unit
        assert file._unit is not None
        assert unit is file._unit
        
        # Accessing the same section again should return the same instance
        unit2 = file.unit
        assert unit is unit2
    
    def test_camel_case_conversion_in_config(self):
        """Test that snake_case attributes are converted to CamelCase in config."""
        file = File(FileType.SERVICE)
        
        # Set attributes with snake_case names
        file.service.exec_start = "/usr/bin/test"
        file.service.working_directory = "/tmp"
        file.install.wanted_by = "multi-user.target"
        
        config = file.get_config(requirement_check=False)
        
        # Should be converted to CamelCase
        assert "ExecStart" in config["Service"]
        assert "WorkingDirectory" in config["Service"]
        assert "WantedBy" in config["Install"]
    
    def test_none_values_excluded_from_config(self):
        """Test that None values are excluded from configuration."""
        file = File(FileType.SERVICE)
        
        # Set some attributes, leave others as None
        file.unit.description = "Test Service"
        file.unit.after = None  # This should be excluded
        file.service.type = "simple"
        file.service.user = None  # This should be excluded
        
        config = file.get_config(requirement_check=False)
        
        # Only non-None values should be included
        assert "Description" in config["Unit"]
        assert "After" not in config["Unit"]
        assert "Type" in config["Service"]
        assert "User" not in config["Service"]
    
    def test_different_file_types_have_different_allowed_sections(self):
        """Test that different file types have different allowed sections."""
        service_file = File(FileType.SERVICE)
        socket_file = File(FileType.SOCKET)
        timer_file = File(FileType.TIMER)
        slice_file = File(FileType.SLICE)
        
        # Service file should allow Service section
        service_section = service_file.service
        assert service_section is not None
        
        # Socket file should allow Socket section but not Service
        socket_section = socket_file.socket
        assert socket_section is not None
        
        with pytest.raises(ValueError):
            _ = socket_file.service
        
        # Timer file should allow Timer section
        timer_section = timer_file.timer
        assert timer_section is not None
        
        # Slice file should not allow Install section
        with pytest.raises(ValueError):
            _ = slice_file.install
