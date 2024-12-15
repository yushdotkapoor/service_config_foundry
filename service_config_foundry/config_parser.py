from configparser import ConfigParser, OrderedDict

class CaseSensitiveConfigParser(ConfigParser):
    def __init__(self, *args, **kwargs):
        # Initialize ConfigParser with case sensitivity
        super().__init__(*args, **kwargs)
        self._dict = OrderedDict

    def optionxform(self, optionstr):
        # Override to make keys case-sensitive
        return optionstr

    def _read(self, fp, fpname):
        """Override the _read method to handle duplicate keys."""
        elements_added = set()
        for lineno, line in enumerate(fp, start=1):
            comment_start = line.find("#")
            if comment_start != -1:
                line = line[:comment_start]
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                if section in self._sections:
                    continue
                self.add_section(section)
                elements_added.add(section)
            else:
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key in self._sections[section]:
                    # Append to existing list if key exists
                    if isinstance(self._sections[section][key], list):
                        self._sections[section][key].append(value)
                    else:
                        self._sections[section][key] = [self._sections[section][key], value]
                else:
                    self._sections[section][key] = value

    def write(self, fp):
        """Override the write method to handle lists for duplicate keys."""
        for section in self._sections:
            fp.write(f"[{section}]\n")
            for key, value in self._sections[section].items():
                if isinstance(value, list):
                    for item in value:
                        fp.write(f"{key} = {item}\n")
                else:
                    fp.write(f"{key} = {value}\n")
            fp.write("\n")
