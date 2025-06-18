import pytest
import subprocess
from unittest.mock import patch, MagicMock
from service_config_foundry.utils import (
    convert_to_camel_case, 
    convert_to_snake_case, 
    merge_dicts, 
    run_command
)


class TestConvertToCamelCase:
    """Test cases for convert_to_camel_case function."""
    
    def test_single_word(self):
        """Test converting a single word."""
        assert convert_to_camel_case("test") == "Test"
    
    def test_two_words(self):
        """Test converting two words with underscore."""
        assert convert_to_camel_case("test_case") == "TestCase"
    
    def test_multiple_words(self):
        """Test converting multiple words with underscores."""
        assert convert_to_camel_case("this_is_a_test") == "ThisIsATest"
    
    def test_empty_string(self):
        """Test converting an empty string."""
        assert convert_to_camel_case("") == ""
    
    def test_single_underscore(self):
        """Test converting a single underscore."""
        assert convert_to_camel_case("_") == ""
    
    def test_multiple_underscores(self):
        """Test converting multiple consecutive underscores."""
        assert convert_to_camel_case("test__case") == "TestCase"


class TestConvertToSnakeCase:
    """Test cases for convert_to_snake_case function."""
    
    def test_single_word(self):
        """Test converting a single word."""
        assert convert_to_snake_case("Test") == "test"
    
    def test_camel_case(self):
        """Test converting CamelCase to snake_case."""
        assert convert_to_snake_case("TestCase") == "test_case"
    
    def test_multiple_words(self):
        """Test converting multiple CamelCase words."""
        assert convert_to_snake_case("ThisIsATest") == "this_is_a_test"
    
    def test_already_snake_case(self):
        """Test that snake_case stays snake_case."""
        assert convert_to_snake_case("test_case") == "test_case"
    
    def test_empty_string(self):
        """Test converting an empty string."""
        assert convert_to_snake_case("") == ""
    
    def test_all_uppercase(self):
        """Test converting all uppercase."""
        assert convert_to_snake_case("TEST") == "t_e_s_t"


class TestMergeDicts:
    """Test cases for merge_dicts function."""
    
    def test_merge_simple_dicts(self):
        """Test merging two simple dictionaries."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        result = merge_dicts(dict1, dict2)
        expected = {"a": 1, "b": 2, "c": 3, "d": 4}
        assert result == expected
    
    def test_merge_overlapping_keys(self):
        """Test merging dictionaries with overlapping keys."""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = merge_dicts(dict1, dict2)
        expected = {"a": 1, "b": 3, "c": 4}
        assert result == expected
    
    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        dict1 = {"a": 1, "b": {"x": 2, "y": 3}}
        dict2 = {"b": {"y": 4, "z": 5}, "c": 6}
        result = merge_dicts(dict1, dict2)
        expected = {"a": 1, "b": {"x": 2, "y": 4, "z": 5}, "c": 6}
        assert result == expected
    
    def test_merge_with_none_dict1(self):
        """Test merging when first dictionary is None."""
        dict1 = None
        dict2 = {"a": 1, "b": 2}
        result = merge_dicts(dict1, dict2)
        assert result == dict2
    
    def test_merge_with_none_dict2(self):
        """Test merging when second dictionary is None."""
        dict1 = {"a": 1, "b": 2}
        dict2 = None
        result = merge_dicts(dict1, dict2)
        assert result == dict1
    
    def test_merge_empty_dicts(self):
        """Test merging empty dictionaries."""
        dict1 = {}
        dict2 = {}
        result = merge_dicts(dict1, dict2)
        assert result == {}


class TestRunCommand:
    """Test cases for run_command function."""
    
    @patch('service_config_foundry.utils.subprocess.Popen')
    def test_run_command_success(self, mock_popen):
        """Test successful command execution."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("output", "")
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = run_command("echo hello", use_sudo=False)
        
        assert result.returncode == 0
        assert result.stdout == "output"
        assert result.stderr == ""
        mock_popen.assert_called_once()
    
    @patch('service_config_foundry.utils.subprocess.Popen')
    def test_run_command_with_sudo(self, mock_popen):
        """Test command execution with sudo."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("output", "")
        mock_process.returncode = 0
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = run_command("echo hello", use_sudo=True)
        
        mock_popen.assert_called_once()
        # Check that sudo was prepended
        call_args = mock_popen.call_args[0][0]
        assert call_args.startswith("sudo ")
    
    @patch('service_config_foundry.utils.subprocess.Popen')
    def test_run_command_with_error(self, mock_popen):
        """Test command execution with error."""
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("", "error message")
        mock_process.returncode = 1
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = run_command("false", use_sudo=False)
        
        assert result.returncode == 1
        assert result.stderr == "error message"
    
    @patch('service_config_foundry.utils.subprocess.Popen')
    @patch('service_config_foundry.utils.os.killpg')
    def test_run_command_keyboard_interrupt(self, mock_killpg, mock_popen):
        """Test command execution with keyboard interrupt."""
        mock_process = MagicMock()
        mock_process.communicate.side_effect = [KeyboardInterrupt(), ("", "")]
        mock_process.returncode = 1
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = run_command("sleep 10", use_sudo=False)
        
        mock_killpg.assert_called_once()
        mock_process.terminate.assert_called()
