import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock, mock_open
from service_config_foundry.service import Service
from service_config_foundry.service_location import ServiceLocation
from service_config_foundry.file_type import FileType


class TestServiceInitialization:
    """Test cases for Service class initialization."""
    
    def test_default_initialization(self):
        """Test Service initialization with default parameters."""
        service = Service("test-service")
        assert service.name == "test-service"
        assert service._service_location == ServiceLocation.GLOBAL
        assert service._auto_start is True
        assert service._enable_at_startup is False
        assert service._force_overwrite is False
    
    def test_custom_initialization(self):
        """Test Service initialization with custom parameters."""
        service = Service(
            "custom-service",
            service_location=ServiceLocation.USER,
            auto_start=False,
            enable_at_startup=True,
            force_overwrite=True
        )
        assert service.name == "custom-service"
        assert service._service_location == ServiceLocation.USER
        assert service._auto_start is False
        assert service._enable_at_startup is True
        assert service._force_overwrite is True
    
    def test_file_objects_creation(self):
        """Test that all file objects are created during initialization."""
        service = Service("test-service")
        assert service.service_file._file_type == FileType.SERVICE
        assert service.socket_file._file_type == FileType.SOCKET
        assert service.target_file._file_type == FileType.TARGET
        assert service.mount_file._file_type == FileType.MOUNT
        assert service.automount_file._file_type == FileType.AUTOMOUNT
        assert service.swap_file._file_type == FileType.SWAP
        assert service.path_file._file_type == FileType.PATH
        assert service.timer_file._file_type == FileType.TIMER
        assert service.device_file._file_type == FileType.DEVICE
        assert service.slice_file._file_type == FileType.SLICE
        assert service.scope_file._file_type == FileType.SCOPE


class TestServicePaths:
    """Test cases for Service path generation."""
    
    def test_get_path_global_location(self):
        """Test path generation for global service location."""
        service = Service("test-service", service_location=ServiceLocation.GLOBAL)
        path = service._Service__get_path(service.service_file)
        expected_path = "/etc/systemd/system/test-service.service"
        assert path == expected_path
    
    def test_get_path_user_location(self):
        """Test path generation for user service location."""
        service = Service("test-service", service_location=ServiceLocation.USER)
        path = service._Service__get_path(service.service_file)
        expected_path = "~/.config/systemd/user/test-service.service"
        assert path == expected_path
    
    def test_get_path_test_location(self):
        """Test path generation for test service location."""
        service = Service("test-service", service_location=ServiceLocation.TEST)
        path = service._Service__get_path(service.timer_file)
        expected_path = ".//test-service.timer"  # The actual implementation adds double slash
        assert path == expected_path


class TestServiceFileExistence:
    """Test cases for checking service file existence."""
    
    @patch('service_config_foundry.service.os.listdir')
    def test_service_with_name_exists_true(self, mock_listdir):
        """Test when service files with the name exist."""
        mock_listdir.return_value = [
            "test-service.service", 
            "test-service.timer", 
            "other-service.service"
        ]
        service = Service("test-service", service_location=ServiceLocation.TEST)
        existing_files = service._Service__service_with_name_exists()
        expected_files = ["test-service.service", "test-service.timer"]
        assert existing_files == expected_files
    
    @patch('service_config_foundry.service.os.listdir')
    def test_service_with_name_exists_false(self, mock_listdir):
        """Test when no service files with the name exist."""
        mock_listdir.return_value = [
            "other-service.service", 
            "another-service.timer"
        ]
        service = Service("test-service", service_location=ServiceLocation.TEST)
        existing_files = service._Service__service_with_name_exists()
        assert existing_files == []
    
    @patch('service_config_foundry.service.os.listdir')
    def test_service_with_name_exists_empty_directory(self, mock_listdir):
        """Test when directory is empty."""
        mock_listdir.return_value = []
        service = Service("test-service", service_location=ServiceLocation.TEST)
        existing_files = service._Service__service_with_name_exists()
        assert existing_files == []


class TestServiceSystemctlCommands:
    """Test cases for systemctl command execution."""
    
    @patch('service_config_foundry.service.run_command')
    def test_enable_service_at_startup(self, mock_run_command):
        """Test enabling service at startup."""
        service = Service("test-service")
        service.enable_service_at_startup()
        mock_run_command.assert_called_once_with("systemctl enable test-service")
    
    @patch('service_config_foundry.service.run_command')
    def test_start_service(self, mock_run_command):
        """Test starting service."""
        service = Service("test-service")
        service.start_service()
        mock_run_command.assert_called_once_with("systemctl restart test-service")
    
    @patch('service_config_foundry.service.run_command')
    def test_status(self, mock_run_command):
        """Test getting service status."""
        service = Service("test-service")
        service.status()
        mock_run_command.assert_called_once_with("systemctl status test-service", use_sudo=False)


class TestServiceCreate:
    """Test cases for service creation."""
    
    @patch('service_config_foundry.service.Service._Service__service_with_name_exists')
    @patch('service_config_foundry.service.Service.replace')
    def test_create_new_service(self, mock_replace, mock_exists):
        """Test creating a new service when none exists."""
        mock_exists.return_value = []
        service = Service("test-service")
        service.create()
        mock_replace.assert_called_once()
    
    @patch('service_config_foundry.service.Service._Service__service_with_name_exists')
    def test_create_existing_service_without_force(self, mock_exists):
        """Test creating service when it already exists without force flag."""
        mock_exists.return_value = ["test-service.service"]
        service = Service("test-service", force_overwrite=False)
        with pytest.raises(ValueError, match="Service for test-service already exists"):
            service.create()
    
    @patch('service_config_foundry.service.Service._Service__service_with_name_exists')
    @patch('service_config_foundry.service.Service.replace')
    def test_create_existing_service_with_force(self, mock_replace, mock_exists):
        """Test creating service when it already exists with force flag."""
        mock_exists.return_value = ["test-service.service"]
        service = Service("test-service", force_overwrite=True)
        service.create()
        mock_replace.assert_called_once()


class TestServiceDelete:
    """Test cases for service deletion."""
    
    @patch('service_config_foundry.service.os.listdir')
    @patch('service_config_foundry.service.os.remove')
    @patch('service_config_foundry.service.os.path.join')
    def test_delete_service_files(self, mock_join, mock_remove, mock_listdir):
        """Test deleting service files."""
        mock_listdir.return_value = [
            "test-service.service", 
            "test-service.timer", 
            "other-service.service"
        ]
        mock_join.side_effect = lambda dir, file: f"{dir}/{file}"
        
        service = Service("test-service", service_location=ServiceLocation.TEST)
        service.delete()
        
        # Should only remove files starting with service name
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call(".//test-service.service")
        mock_remove.assert_any_call(".//test-service.timer")
    
    @patch('service_config_foundry.service.os.listdir')
    @patch('service_config_foundry.service.os.remove')
    @patch('service_config_foundry.service.sys.exit')
    def test_delete_permission_error(self, mock_exit, mock_remove, mock_listdir):
        """Test handling permission errors during deletion."""
        mock_listdir.return_value = ["test-service.service"]
        mock_remove.side_effect = PermissionError("Permission denied")
        
        service = Service("test-service", service_location=ServiceLocation.TEST)
        service.delete()
        
        mock_exit.assert_called_once_with(1)


class TestServiceReplace:
    """Test cases for service replacement."""
    
    @patch('service_config_foundry.service.Service.delete')
    @patch('service_config_foundry.service.Service._Service__file_configs')
    @patch('service_config_foundry.service.Service._Service__get_path')
    @patch('service_config_foundry.service.run_command')
    @patch('builtins.open', new_callable=mock_open)
    def test_replace_service_basic(self, mock_file, mock_run_command, mock_get_path, 
                                   mock_file_configs, mock_delete):
        """Test basic service replacement."""
        # Mock file configurations
        mock_file_configs.return_value = [
            (MagicMock(), {"Unit": {"Description": "Test"}, "Service": {"Type": "simple"}})
        ]
        mock_get_path.return_value = "/test/path/test-service.service"
        
        service = Service("test-service", auto_start=False, enable_at_startup=False)
        service.replace()
        
        # Verify delete was called
        mock_delete.assert_called_once()
        
        # Verify file was written
        mock_file.assert_called_with("/test/path/test-service.service", "w")
        
        # Verify systemctl daemon-reload was called
        mock_run_command.assert_called_with("systemctl daemon-reload")
    
    @patch('service_config_foundry.service.Service.delete')
    @patch('service_config_foundry.service.Service._Service__file_configs')
    @patch('service_config_foundry.service.Service._Service__get_path')
    @patch('service_config_foundry.service.Service.start_service')
    @patch('service_config_foundry.service.Service.enable_service_at_startup')
    @patch('service_config_foundry.service.run_command')
    @patch('builtins.open', new_callable=mock_open)
    def test_replace_with_auto_start_and_enable(self, mock_file, mock_run_command, 
                                                mock_enable, mock_start, mock_get_path, 
                                                mock_file_configs, mock_delete):
        """Test service replacement with auto start and enable at startup."""
        mock_file_configs.return_value = []
        
        service = Service("test-service", auto_start=True, enable_at_startup=True)
        service.replace()
        
        # Verify start and enable were called
        mock_start.assert_called_once()
        mock_enable.assert_called_once()


class TestServiceUpdate:
    """Test cases for service updates."""
    
    @patch('service_config_foundry.service.os.listdir')
    def test_update_no_existing_service(self, mock_listdir):
        """Test updating when no existing service files are found."""
        mock_listdir.return_value = []
        service = Service("test-service", service_location=ServiceLocation.TEST)
        
        with pytest.raises(ValueError, match="No service found for test-service"):
            service.update()
    
    @patch('service_config_foundry.service.os.listdir')
    @patch('service_config_foundry.service.CaseSensitiveConfigParser')
    @patch('service_config_foundry.service.Service._Service__file_configs')
    @patch('service_config_foundry.service.Service._Service__add_attributes')
    @patch('service_config_foundry.service.Service.replace')
    @patch('service_config_foundry.service.merge_dicts')
    def test_update_existing_service(self, mock_merge, mock_replace, mock_add_attrs, 
                                     mock_file_configs, mock_config_parser, mock_listdir):
        """Test updating an existing service."""
        mock_listdir.return_value = ["test-service.service"]
        mock_file_configs.return_value = []
        mock_merge.return_value = {}
        
        service = Service("test-service", service_location=ServiceLocation.TEST)
        service.update()
        
        # Verify configuration was read and service was replaced
        mock_config_parser.assert_called()
        mock_replace.assert_called_once()


class TestServiceFileConfigs:
    """Test cases for file configuration generation."""
    
    def test_file_configs_generator(self):
        """Test the file configs generator method."""
        service = Service("test-service")
        
        # Configure a service file
        service.service_file.unit.description = "Test Service"
        service.service_file.service.type = "simple"
        service.service_file.install.wanted_by = "multi-user.target"
        
        # Get configurations
        configs = list(service._Service__file_configs(requirement_check=False))
        
        # Should have at least one configuration
        assert len(configs) > 0
        
        # Each config should be a tuple of (file, config_dict)
        for file, config_dict in configs:
            assert hasattr(file, '_file_type')
            assert isinstance(config_dict, dict)


class TestServiceBooleanHandling:
    """Test cases for boolean value handling in service files."""
    
    @patch('service_config_foundry.service.Service.delete')
    @patch('service_config_foundry.service.Service._Service__file_configs')
    @patch('service_config_foundry.service.Service._Service__get_path')
    @patch('service_config_foundry.service.run_command')
    @patch('builtins.open', new_callable=mock_open)
    def test_boolean_values_converted_to_lowercase_single_values(self, mock_file, mock_run_command, 
                                                                mock_get_path, mock_file_configs, mock_delete):
        """Test that single boolean values are converted to lowercase."""
        # Mock file configurations with boolean values
        mock_file_configs.return_value = [
            (MagicMock(), {
                "Timer": {
                    "Persistent": True,
                    "WakeSystem": False,
                    "OnCalendar": "daily"
                }
            })
        ]
        mock_get_path.return_value = "/test/path/test-service.timer"
        
        service = Service("test-service", auto_start=False, enable_at_startup=False)
        service.replace()
        
        # Verify that write was called with lowercase boolean values
        mock_file.assert_called_with("/test/path/test-service.timer", "w")
        handle = mock_file.return_value.__enter__.return_value
        
        # Check all write calls for correct boolean formatting
        write_calls = [call.args[0] for call in handle.write.call_args_list]
        content = ''.join(write_calls)
        
        assert "Persistent=true" in content, f"Expected 'Persistent=true', got: {content}"
        assert "WakeSystem=false" in content, f"Expected 'WakeSystem=false', got: {content}"
        assert "Persistent=True" not in content, "Found uppercase 'True' instead of lowercase"
        assert "WakeSystem=False" not in content, "Found uppercase 'False' instead of lowercase"
    
    @patch('service_config_foundry.service.Service.delete')
    @patch('service_config_foundry.service.Service._Service__file_configs')
    @patch('service_config_foundry.service.Service._Service__get_path')
    @patch('service_config_foundry.service.run_command')
    @patch('builtins.open', new_callable=mock_open)
    def test_boolean_values_converted_to_lowercase_list_values(self, mock_file, mock_run_command, 
                                                               mock_get_path, mock_file_configs, mock_delete):
        """Test that boolean values in lists are converted to lowercase."""
        # Mock file configurations with boolean values in lists
        mock_file_configs.return_value = [
            (MagicMock(), {
                "Service": {
                    "RemainAfterExit": [True],
                    "PrivateNetwork": [False],
                    "Type": ["simple"]
                }
            })
        ]
        mock_get_path.return_value = "/test/path/test-service.service"
        
        service = Service("test-service", auto_start=False, enable_at_startup=False)
        service.replace()
        
        # Verify that write was called with lowercase boolean values
        handle = mock_file.return_value.__enter__.return_value
        write_calls = [call.args[0] for call in handle.write.call_args_list]
        content = ''.join(write_calls)
        
        assert "RemainAfterExit=true" in content, f"Expected 'RemainAfterExit=true', got: {content}"
        assert "PrivateNetwork=false" in content, f"Expected 'PrivateNetwork=false', got: {content}"
        assert "RemainAfterExit=True" not in content, "Found uppercase 'True' instead of lowercase"
        assert "PrivateNetwork=False" not in content, "Found uppercase 'False' instead of lowercase"