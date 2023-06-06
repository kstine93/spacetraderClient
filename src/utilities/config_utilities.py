
"""
Utilities functions centered around manipulating config files.
"""

#==========
from configparser import ConfigParser

#===========
def get_config(file_path:str) -> ConfigParser:
        """Load config from file. Index into section if provided"""
        config = ConfigParser()
        config.read(file_path)
        return config

#===========
def write_config(config_path:str,config:ConfigParser) -> ConfigParser:
        """Write config to file"""
        with open(config_path, 'w') as configfile:
            config.write(configfile)

#===========
def update_config_file(config_path:str,section:str,data:dict) -> None:
        """Update config file. Add data to given section"""
        config = get_config(config_path)
        config_data = {section:data}
        config.read_dict(config_data)
        write_config(config_path,config)