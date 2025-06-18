import pytest
import tempfile
import os
import shutil
from unittest.mock import MagicMock
from service_config_foundry.service_location import ServiceLocation


@pytest.fixture
def temp_service_directory():
    """Create a temporary directory for testing service files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_service_location(temp_service_directory):
    """Mock the ServiceLocation.TEST to use a temporary directory."""
    original_directory = ServiceLocation.TEST.directory
    ServiceLocation.TEST.directory = lambda: temp_service_directory
    yield temp_service_directory
    ServiceLocation.TEST.directory = original_directory


@pytest.fixture
def sample_service_config():
    """Provide a sample service configuration for testing."""
    return {
        "Unit": {
            "Description": "Test Service",
            "After": "network.target"
        },
        "Service": {
            "Type": "simple",
            "ExecStart": "/usr/bin/test-app",
            "User": "testuser",
            "Restart": "always"
        },
        "Install": {
            "WantedBy": "multi-user.target"
        }
    }


@pytest.fixture
def sample_timer_config():
    """Provide a sample timer configuration for testing."""
    return {
        "Unit": {
            "Description": "Test Timer"
        },
        "Timer": {
            "OnCalendar": "daily",
            "Persistent": "true"
        },
        "Install": {
            "WantedBy": "timers.target"
        }
    }


@pytest.fixture
def sample_socket_config():
    """Provide a sample socket configuration for testing."""
    return {
        "Unit": {
            "Description": "Test Socket"
        },
        "Socket": {
            "ListenStream": "8080",
            "SocketUser": "www-data",
            "SocketGroup": "www-data"
        },
        "Install": {
            "WantedBy": "sockets.target"
        }
    }


@pytest.fixture
def mock_run_command():
    """Mock the run_command function to prevent actual systemctl calls."""
    with pytest.mock.patch('service_config_foundry.service.run_command') as mock:
        mock.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock


@pytest.fixture
def mock_os_operations():
    """Mock OS operations for testing without file system effects."""
    with pytest.mock.patch('service_config_foundry.service.os.listdir') as mock_listdir, \
         pytest.mock.patch('service_config_foundry.service.os.remove') as mock_remove, \
         pytest.mock.patch('service_config_foundry.service.os.path.join') as mock_join:
        
        mock_listdir.return_value = []
        mock_join.side_effect = lambda a, b: f"{a}/{b}"
        
        yield {
            'listdir': mock_listdir,
            'remove': mock_remove,
            'join': mock_join
        }


# Test markers for categorizing tests
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
