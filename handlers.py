import os
import re
import sys
from watchdog.events import FileSystemEventHandler
from typing import List, Dict, Any
from config import Config


class LogHandler(FileSystemEventHandler):
    def __init__(self, callback, config: Config):
        super().__init__()
        self.callback = callback
        self.config = config
        try:
            self._file = open(self.config.log_file_path, 'r', encoding='utf-8')
        except FileNotFoundError:
            print(f"Log file '{self.config.log_file_path}' not found.")
            sys.exit(1)
        self._file.seek(0, os.SEEK_END)
        self.spell_patterns = []
        for spell in self.config.spells:
            try:
                compiled_regex = re.compile(spell['regex_pattern'], re.IGNORECASE)
                self.spell_patterns.append({
                    'spell_name': spell['spell_name'],
                    'regex': compiled_regex,
                    'message_template': spell.get('message_template', None),
                    'category': spell.get('category', 'damage')
                })
            except re.error as e:
                print(f"Invalid regex pattern for spell '{spell['spell_name']}': {e}")

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == os.path.abspath(self.config.log_file_path):
            lines = self._file.readlines()
            events = []
            for line in lines:
                line = line.strip()
                for pattern in self.spell_patterns:
                    match = pattern['regex'].search(line)
                    if match:
                        if pattern['message_template']:
                            # Special event
                            monster_name = match.group(1)
                            message = pattern['message_template'].format(monster_name=monster_name)
                            events.append({
                                'type': 'special',
                                'spell_name': pattern['spell_name'],
                                'message': message,
                                'category': pattern['category'],
                                'monster_name': monster_name
                            })
                        else:
                            # Damage event
                            monster_name = match.group(1)
                            damage = int(match.group(2))
                            spell_name = pattern['spell_name']
                            category = pattern['category']
                            events.append({
                                'type': 'damage',
                                'spell_name': spell_name,
                                'damage': damage,
                                'category': category,
                                'monster_name': monster_name
                            })
            if events:
                self.callback(events)
