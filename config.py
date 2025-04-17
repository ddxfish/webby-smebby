import json
import os

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_config = {
            'check_frequency': 300,  # seconds
            'check_dns': True,
            'check_ssl': True,
            'check_http': True,
            'check_string': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0',
            'db_file': 'uptime.db',
            'csv_file': 'websites.csv',
            'dark_mode': False  # Default to light mode
        }
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return self.default_config.copy()
        else:
            self.save_config(self.default_config)
            return self.default_config.copy()
    
    def save_config(self, config=None):
        if config is None:
            config = self.config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception:
            pass
    
    def get(self, key):
        return self.config.get(key, self.default_config.get(key))
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()