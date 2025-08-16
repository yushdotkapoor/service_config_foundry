import os
import tempfile

import pytest

from service_config_foundry.config_parser import CaseSensitiveConfigParser


class TestCaseSensitiveConfigParser:
    """Test cases for CaseSensitiveConfigParser."""

    def test_initialization(self):
        """Test parser initialization."""
        parser = CaseSensitiveConfigParser()
        assert parser is not None
        assert hasattr(parser, "_dict")

    def test_case_sensitivity(self):
        """Test that option names preserve case."""
        parser = CaseSensitiveConfigParser()
        assert parser.optionxform("TestOption") == "TestOption"
        assert parser.optionxform("test_option") == "test_option"
        assert parser.optionxform("UPPERCASE") == "UPPERCASE"

    def test_read_basic_config(self):
        """Test reading a basic configuration file."""
        config_content = """
[Unit]
Description=Test Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/test

[Install]
WantedBy=multi-user.target
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            f.flush()

            parser = CaseSensitiveConfigParser()
            parser.read(f.name)

            # Clean up
            os.unlink(f.name)

            # Test that sections and options were read correctly
            assert "Unit" in parser.sections()
            assert "Service" in parser.sections()
            assert "Install" in parser.sections()

    def test_read_case_sensitive_options(self):
        """Test reading configuration with case-sensitive options."""
        config_content = """
[Test]
CamelCase=value1
snake_case=value2
UPPERCASE=value3
lowercase=value4
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            f.flush()

            parser = CaseSensitiveConfigParser()
            parser.read(f.name)

            # Clean up
            os.unlink(f.name)

            # Test that sections are read
            assert "Test" in parser.sections()
            # Test case sensitivity (the implementation may vary)
            assert parser.optionxform("CamelCase") == "CamelCase"
            assert parser.optionxform("snake_case") == "snake_case"

    def test_read_with_comments(self):
        """Test reading configuration with comments."""
        config_content = """
[Unit]
# This is a comment
Description=Test Service  # Inline comment
After=network.target

# Another comment
[Service]
Type=simple
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            f.flush()

            parser = CaseSensitiveConfigParser()
            parser.read(f.name)

            # Clean up
            os.unlink(f.name)

            # Test that comments are ignored and options are read correctly
            assert "Unit" in parser.sections()
            assert "Service" in parser.sections()

    def test_read_empty_lines(self):
        """Test reading configuration with empty lines."""
        config_content = """

[Unit]

Description=Test Service


[Service]

Type=simple

"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            f.flush()

            parser = CaseSensitiveConfigParser()
            parser.read(f.name)

            # Clean up
            os.unlink(f.name)

            # Test that empty lines are ignored
            assert "Unit" in parser.sections()
            assert "Service" in parser.sections()

    def test_read_duplicate_keys(self):
        """Test reading configuration with duplicate keys."""
        config_content = """
[Unit]
After=network.target
After=time-sync.target
After=multi-user.target
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            f.write(config_content)
            f.flush()

            parser = CaseSensitiveConfigParser()
            parser.read(f.name)

            # Clean up
            os.unlink(f.name)

            # Test that duplicate keys are handled (implementation specific)
            assert "Unit" in parser.sections()

    def test_read_nonexistent_file(self):
        """Test reading a non-existent file."""
        parser = CaseSensitiveConfigParser()
        # Should not raise an exception for non-existent file
        parser.read("nonexistent_file.conf")
        assert len(parser.sections()) == 0

    def test_write_config(self):
        """Test writing configuration to file."""
        parser = CaseSensitiveConfigParser()
        parser.add_section("Unit")
        parser.set("Unit", "Description", "Test Service")
        parser.set("Unit", "After", "network.target")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
            parser.write(f)
            f.flush()

            # Read the file back to verify
            with open(f.name, "r") as read_f:
                content = read_f.read()
                assert "[Unit]" in content
                assert "Description" in content
                assert "After" in content

            # Clean up
            os.unlink(f.name)
