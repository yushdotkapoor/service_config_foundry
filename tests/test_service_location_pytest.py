import pytest
from service_config_foundry.service_location import ServiceLocation


class TestServiceLocation:
    """Test cases for ServiceLocation enum."""
    
    def test_enum_values(self):
        """Test that all enum values are correctly defined."""
        assert ServiceLocation.GLOBAL.value == 0
        assert ServiceLocation.DEFAULT.value == 1
        assert ServiceLocation.RUNTIME.value == 2
        assert ServiceLocation.USER.value == 3
        assert ServiceLocation.TEST.value == 4
    
    def test_global_directory(self):
        """Test GLOBAL service location directory."""
        assert ServiceLocation.GLOBAL.directory() == "/etc/systemd/system"
    
    def test_default_directory(self):
        """Test DEFAULT service location directory."""
        assert ServiceLocation.DEFAULT.directory() == "/usr/lib/systemd/system"
    
    def test_runtime_directory(self):
        """Test RUNTIME service location directory."""
        assert ServiceLocation.RUNTIME.directory() == "/run/systemd/system"
    
    def test_user_directory(self):
        """Test USER service location directory."""
        assert ServiceLocation.USER.directory() == "~/.config/systemd/user"
    
    def test_test_directory(self):
        """Test TEST service location directory."""
        assert ServiceLocation.TEST.directory() == "./"
    
    def test_all_locations_have_directories(self):
        """Test that all enum values return a directory."""
        for location in ServiceLocation:
            directory = location.directory()
            assert isinstance(directory, str)
            assert len(directory) > 0