from collections import OrderedDict, defaultdict
from configparser import ConfigParser


class CaseSensitiveConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        # Disable interpolation to prevent issues with list values
        kwargs["interpolation"] = None
        super().__init__(*args, **kwargs)
        self._dict = OrderedDict

    def optionxform(self, optionstr):
        # Preserve case sensitivity for option names
        return optionstr

    def _read(self, fp, fpname):
        """Override _read to allow duplicate keys."""
        cur_section = None
        for lineno, line in enumerate(fp, start=1):
            comment_start = line.find("#")
            if comment_start != -1:
                line = line[:comment_start]
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                cur_section = line[1:-1].strip()
                if cur_section not in self._sections:
                    self._sections[cur_section] = defaultdict(list)
            else:
                if cur_section is None:
                    raise ValueError(
                        f"Missing section header in {fpname} at line {lineno}"
                    )
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                self._sections[cur_section][key].append(value)

    def get(self, section, option, *, raw=False, vars=None, fallback=None):
        """Override `get` to handle list values."""
        if section not in self._sections:
            if fallback is not None:
                return fallback
            raise KeyError(f"Section '{section}' not found")
        if option not in self._sections[section]:
            if fallback is not None:
                return fallback
            raise KeyError(f"Option '{option}' not found in section '{section}'")

        values = self._sections[section][option]
        if isinstance(values, list):
            # Join list values into a single string for compatibility
            return "\n".join(values) if not raw else values
        return values

    def items(self, section=None, *, raw=False, vars=None):
        """Override items to handle list values for both section-specific and global cases."""
        if section is None:
            # Global case: return all sections and their items
            return [(s, dict(self.items(s))) for s in self._sections]
        if section not in self._sections:
            raise KeyError(f"Section '{section}' not found")
        # Section-specific case: return all key-value pairs in the section
        return (
            (key, "\n".join(values) if isinstance(values, list) else values)
            for key, values in self._sections[section].items()
        )

    def write(self, fp):
        """Override the write method to handle lists for duplicate keys."""
        for section in self._sections:
            fp.write(f"[{section}]\n")
            for key, values in self._sections[section].items():
                for value in values:
                    if type(values) is bool:
                        value = str(value).lower()
                    fp.write(f"{key}={value}\n")
            fp.write("\n")
