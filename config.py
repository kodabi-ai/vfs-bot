import os
import yaml

class FlexibleConfig:
    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path
        self.config_data = {}
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = yaml.safe_load(f) or {}
            self.apply_env_overrides()
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found.")

    def apply_env_overrides(self):
        """
        Applies environment variable overrides to the loaded config data.
        Format: CONFIG_KEY or CONFIG__NESTED__KEY (where keys are uppercase).
        """
        flat_config = self._flatten_config(self.config_data)
        
        for key, value in flat_config.items():
            # Determine env var name: replace dots with __ and uppercase
            env_var_name = key.upper().replace('.', '__')
            env_value = os.getenv(env_var_name)
            
            if env_value is not None:
                # Handle type casting for basic types
                if isinstance(value, int):
                    try:
                        self._set_nested_value(self.config_data, key, int(env_value))
                    except ValueError:
                        pass # Keep string if conversion fails
                elif isinstance(value, bool):
                    self._set_nested_value(self.config_data, key, env_value.lower() in ('true', '1', 'yes'))
                else:
                    self._set_nested_value(self.config_data, key, env_value)

    def _flatten_config(self, data, parent_key='', sep='.'):
        items = {}
        for k, v in data.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.update(self._flatten_config(v, new_key, sep=sep))
            else:
                items[new_key] = v
        return items

    def _set_nested_value(self, data, key_path, value):
        keys = key_path.split('.')
        d = data
        for k in keys[:-1]:
            d = d[k]
        d[keys[-1]] = value

    def get(self, key, default=None):
        """
        Retrieve a configuration value using dot notation.
        Example: config.get('vfs_global.urls.base')
        """
        keys = key.split('.')
        data = self.config_data
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        return data

    def reload(self):
        """
        Reload configuration from file.
        """
        self.load_config()

# Global instance
config = FlexibleConfig()
# Dynamic attribute exposure for backward compatibility
EMAIL = config.get('vfs_global.credentials.email', '')
PASSWORD = config.get('vfs_global.credentials.password', '')
PHONE = config.get('vfs_global.credentials.phone', '')
USER_AGENT = config.get('vfs_global.stealth.user_agent', '')
VIEWPORT = config.get('vfs_global.browser.viewport', {})
