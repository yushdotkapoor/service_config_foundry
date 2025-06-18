import pytest
import tempfile
import os
import shutil
from unittest.mock import patch, MagicMock
from service_config_foundry import Service, ServiceLocation


class TestServiceIntegration:
    """Integration tests for the Service class."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()
        self.original_test_dir = ServiceLocation.TEST.directory()
        # Monkey patch the TEST directory to our temp directory
        ServiceLocation.TEST.directory = lambda: self.test_dir
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Restore original directory function
        ServiceLocation.TEST.directory = lambda: self.original_test_dir
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('service_config_foundry.service.run_command')
    def test_create_simple_service(self, mock_run_command):
        """Test creating a simple service file."""
        service = Service("test-app", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure the service
        service.service_file.unit.description = "Test Application"
        service.service_file.unit.after = "network.target"
        service.service_file.service.type = "simple"
        service.service_file.service.exec_start = "/usr/bin/test-app"
        service.service_file.service.user = "testuser"
        service.service_file.service.restart = "always"
        service.service_file.install.wanted_by = "multi-user.target"
        
        # Create the service
        service.create()
        
        # Verify the file was created
        service_file_path = os.path.join(self.test_dir, "test-app.service")
        assert os.path.exists(service_file_path)
        
        # Verify the file content
        with open(service_file_path, 'r') as f:
            content = f.read()
            assert "[Unit]" in content
            assert "Description=Test Application" in content
            assert "After=network.target" in content
            assert "[Service]" in content
            assert "Type=simple" in content
            assert "ExecStart=/usr/bin/test-app" in content
            assert "User=testuser" in content
            assert "Restart=always" in content
            assert "[Install]" in content
            assert "WantedBy=multi-user.target" in content
        
        # Verify systemctl daemon-reload was called
        mock_run_command.assert_called_with("systemctl daemon-reload")
    
    @patch('service_config_foundry.service.run_command')
    def test_create_service_with_timer(self, mock_run_command):
        """Test creating a service with a timer file."""
        service = Service("backup-job", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure the service
        service.service_file.unit.description = "Backup Job"
        service.service_file.service.type = "oneshot"
        service.service_file.service.exec_start = "/usr/local/bin/backup.sh"
        
        # Configure the timer
        service.timer_file.unit.description = "Backup Job Timer"
        service.timer_file.timer.on_calendar = "daily"
        service.timer_file.timer.persistent = True
        service.timer_file.install.wanted_by = "timers.target"
        
        # Create the service
        service.create()
        
        # Verify both files were created
        service_file_path = os.path.join(self.test_dir, "backup-job.service")
        timer_file_path = os.path.join(self.test_dir, "backup-job.timer")
        
        assert os.path.exists(service_file_path)
        assert os.path.exists(timer_file_path)
        
        # Verify timer file content
        with open(timer_file_path, 'r') as f:
            content = f.read()
            assert "[Unit]" in content
            assert "Description=Backup Job Timer" in content
            assert "[Timer]" in content
            assert "OnCalendar=daily" in content
            assert "Persistent=true" in content  # systemd expects lowercase boolean values
            assert "[Install]" in content
            assert "WantedBy=timers.target" in content
    
    @patch('service_config_foundry.service.run_command')
    def test_create_service_with_socket(self, mock_run_command):
        """Test creating a service with a socket file."""
        service = Service("web-server", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure the service
        service.service_file.unit.description = "Web Server"
        service.service_file.service.type = "notify"
        service.service_file.service.exec_start = "/usr/bin/web-server"
        service.service_file.install.wanted_by = "multi-user.target"
        
        # Configure the socket
        service.socket_file.unit.description = "Web Server Socket"
        service.socket_file.socket.listen_stream = "8080"
        service.socket_file.socket.socket_user = "www-data"
        service.socket_file.socket.socket_group = "www-data"
        service.socket_file.install.wanted_by = "sockets.target"
        
        # Create the service
        service.create()
        
        # Verify both files were created
        service_file_path = os.path.join(self.test_dir, "web-server.service")
        socket_file_path = os.path.join(self.test_dir, "web-server.socket")
        
        assert os.path.exists(service_file_path)
        assert os.path.exists(socket_file_path)
        
        # Verify socket file content
        with open(socket_file_path, 'r') as f:
            content = f.read()
            assert "[Unit]" in content
            assert "Description=Web Server Socket" in content
            assert "[Socket]" in content
            assert "ListenStream=8080" in content
            assert "SocketUser=www-data" in content
            assert "SocketGroup=www-data" in content
            assert "[Install]" in content
            assert "WantedBy=sockets.target" in content
    
    @patch('service_config_foundry.service.run_command')
    def test_update_existing_service(self, mock_run_command):
        """Test updating an existing service."""
        service = Service("update-test", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure and create initial service
        service.service_file.unit.description = "Initial Description"
        service.service_file.service.type = "simple"
        service.service_file.service.exec_start = "/usr/bin/initial-app"
        service.service_file.install.wanted_by = "multi-user.target"
        service.create()
        
        # Create a new service instance for update
        updated_service = Service("update-test", service_location=ServiceLocation.TEST, 
                                 auto_start=False, enable_at_startup=False)
        
        # Configure new attributes
        updated_service.service_file.unit.description = "Updated Description"
        updated_service.service_file.service.exec_start = "/usr/bin/updated-app"
        updated_service.service_file.service.user = "newuser"
        
        # Update the service
        updated_service.update()
        
        # Verify the file was updated
        service_file_path = os.path.join(self.test_dir, "update-test.service")
        with open(service_file_path, 'r') as f:
            content = f.read()
            assert "Description=Updated Description" in content
            assert "ExecStart=/usr/bin/updated-app" in content
            assert "User=newuser" in content
            assert "Type=simple" in content  # Should preserve original value
            assert "WantedBy=multi-user.target" in content  # Should preserve original value
    
    @patch('service_config_foundry.service.run_command')
    def test_replace_existing_service(self, mock_run_command):
        """Test replacing an existing service."""
        service = Service("replace-test", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure and create initial service
        service.service_file.unit.description = "Original Service"
        service.service_file.service.type = "simple"
        service.service_file.service.exec_start = "/usr/bin/original-app"
        service.service_file.install.wanted_by = "multi-user.target"
        service.create()
        
        # Configure timer for initial service
        service.timer_file.unit.description = "Original Timer"
        service.timer_file.timer.on_calendar = "hourly"
        service.timer_file.install.wanted_by = "timers.target"
        service.replace()
        
        # Verify both files exist
        service_file_path = os.path.join(self.test_dir, "replace-test.service")
        timer_file_path = os.path.join(self.test_dir, "replace-test.timer")
        assert os.path.exists(service_file_path)
        assert os.path.exists(timer_file_path)
        
        # Create new service with completely different configuration
        new_service = Service("replace-test", service_location=ServiceLocation.TEST, 
                             auto_start=False, enable_at_startup=False)
        new_service.service_file.unit.description = "Completely New Service"
        new_service.service_file.service.type = "forking"
        new_service.service_file.service.exec_start = "/usr/bin/new-app"
        new_service.service_file.service.pid_file = "/var/run/new-app.pid"
        new_service.service_file.install.wanted_by = "multi-user.target"
        
        # Replace (should remove timer file)
        new_service.replace()
        
        # Verify service file was replaced
        with open(service_file_path, 'r') as f:
            content = f.read()
            assert "Description=Completely New Service" in content
            assert "Type=forking" in content
            assert "ExecStart=/usr/bin/new-app" in content
            assert "PidFile=/var/run/new-app.pid" in content
        
        # Timer file should no longer exist
        assert not os.path.exists(timer_file_path)
    
    @patch('service_config_foundry.service.run_command')
    def test_delete_service(self, mock_run_command):
        """Test deleting a service."""
        service = Service("delete-test", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure and create service with multiple files
        service.service_file.unit.description = "Service to Delete"
        service.service_file.service.type = "simple"
        service.service_file.service.exec_start = "/usr/bin/delete-app"
        service.service_file.install.wanted_by = "multi-user.target"
        
        service.timer_file.unit.description = "Timer to Delete"
        service.timer_file.timer.on_calendar = "daily"
        service.timer_file.install.wanted_by = "timers.target"
        
        service.socket_file.unit.description = "Socket to Delete"
        service.socket_file.socket.listen_stream = "9090"
        service.socket_file.install.wanted_by = "sockets.target"
        
        service.create()
        
        # Verify files were created
        service_file_path = os.path.join(self.test_dir, "delete-test.service")
        timer_file_path = os.path.join(self.test_dir, "delete-test.timer")
        socket_file_path = os.path.join(self.test_dir, "delete-test.socket")
        
        assert os.path.exists(service_file_path)
        assert os.path.exists(timer_file_path)
        assert os.path.exists(socket_file_path)
        
        # Delete the service
        service.delete()
        
        # Verify all files were deleted
        assert not os.path.exists(service_file_path)
        assert not os.path.exists(timer_file_path)
        assert not os.path.exists(socket_file_path)
    
    @patch('service_config_foundry.service.run_command')
    def test_create_mount_and_automount(self, mock_run_command):
        """Test creating mount and automount files."""
        service = Service("mount-test", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Configure mount
        service.mount_file.unit.description = "Test Mount"
        service.mount_file.mount.what = "/dev/sdb1"
        service.mount_file.mount.where = "/mnt/test"
        service.mount_file.mount.type = "ext4"
        service.mount_file.mount.options = "defaults"
        service.mount_file.install.wanted_by = "multi-user.target"
        
        # Configure automount
        service.automount_file.unit.description = "Test Automount"
        service.automount_file.automount.where = "/mnt/test"
        service.automount_file.automount.timeout_idle_sec = "60"
        
        service.create()
        
        # Verify both files were created
        mount_file_path = os.path.join(self.test_dir, "mount-test.mount")
        automount_file_path = os.path.join(self.test_dir, "mount-test.automount")
        
        assert os.path.exists(mount_file_path)
        assert os.path.exists(automount_file_path)
        
        # Verify mount file content
        with open(mount_file_path, 'r') as f:
            content = f.read()
            assert "[Mount]" in content
            assert "What=/dev/sdb1" in content
            assert "Where=/mnt/test" in content
            assert "Type=ext4" in content
            assert "Options=defaults" in content
        
        # Verify automount file content
        with open(automount_file_path, 'r') as f:
            content = f.read()
            assert "[Automount]" in content
            assert "Where=/mnt/test" in content
            assert "TimeoutIdleSec=60" in content
    
    def test_force_overwrite_behavior(self):
        """Test force overwrite behavior."""
        # Create initial service
        service1 = Service("force-test", service_location=ServiceLocation.TEST, 
                          auto_start=False, enable_at_startup=False, force_overwrite=False)
        service1.service_file.unit.description = "Initial Service"
        service1.service_file.service.exec_start = "/usr/bin/initial"
        service1.service_file.install.wanted_by = "multi-user.target"
        service1.create()
        
        # Try to create again without force - should raise error
        service2 = Service("force-test", service_location=ServiceLocation.TEST, 
                          auto_start=False, enable_at_startup=False, force_overwrite=False)
        with pytest.raises(ValueError, match="Service for force-test already exists"):
            service2.create()
        
        # Create with force - should succeed
        service3 = Service("force-test", service_location=ServiceLocation.TEST, 
                          auto_start=False, enable_at_startup=False, force_overwrite=True)
        service3.service_file.unit.description = "Forced Service"
        service3.service_file.service.exec_start = "/usr/bin/forced"
        service3.service_file.install.wanted_by = "multi-user.target"
        service3.create()  # Should not raise error
        
        # Verify the file was overwritten
        service_file_path = os.path.join(self.test_dir, "force-test.service")
        with open(service_file_path, 'r') as f:
            content = f.read()
            assert "Description=Forced Service" in content
            assert "ExecStart=/usr/bin/forced" in content
    
    def test_boolean_conversion_to_lowercase(self):
        """Test that boolean values are converted to lowercase in systemd files."""
        service = Service("bool-test", service_location=ServiceLocation.TEST, 
                         auto_start=False, enable_at_startup=False)
        
        # Set boolean values
        service.timer_file.timer.persistent = True  # Python True
        service.timer_file.timer.wake_system = False  # Python False
        service.timer_file.timer.on_calendar = "daily"  # Add required timer config
        service.timer_file.unit.description = "Boolean Test Timer"
        service.timer_file.install.wanted_by = "timers.target"
        
        # Create the service
        service.create()
        
        timer_path = os.path.join(self.test_dir, "bool-test.timer")
        
        try:
            # Verify the file was created and contains lowercase booleans
            assert os.path.exists(timer_path), f"Timer file not found at {timer_path}"
            
            with open(timer_path, 'r') as f:
                content = f.read()
                # Check that booleans are lowercase
                assert "Persistent=true" in content, f"Expected lowercase 'true', got content: {content}"
                assert "WakeSystem=false" in content, f"Expected lowercase 'false', got content: {content}"
                # Ensure uppercase versions are NOT present
                assert "Persistent=True" not in content, "Found uppercase 'True' instead of lowercase 'true'"
                assert "WakeSystem=False" not in content, "Found uppercase 'False' instead of lowercase 'false'"
        
        finally:
            # Clean up
            if os.path.exists(timer_path):
                os.remove(timer_path)
