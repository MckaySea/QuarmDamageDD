# config.py

import os
import json
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, Any


@dataclass
class Config:
    # Path to your log file (absolute path)
    log_file_path: str = 'log.txt'  # Default value

    # List of spells with their configurations
    spells: List[Dict[str, Any]] = field(default_factory=lambda: [
        {
            'spell_name': 'Dooming Darkness',
            'icon_path': 'resources/icons/doom_darkness.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Dooming Darkness\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Cascading Darkness',
            'icon_path': 'resources/icons/cascading_darkness.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Cascading Darkness\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Spirit of Wolf',
            'icon_path': 'resources/icons/spirit_wolf.png',
            'regex_pattern': r'You feel the spirit of wolf enter you.',
            'message_template': 'Spirit of the wolf',
            'category': 'healing'
        },
        {
            'spell_name': 'Vampiric Curse',
            'icon_path': 'resources/icons/vamp_curse.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Vampiric Curse\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Invoke Fear',
            'icon_path': 'resources/icons/invoke_fear.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Invoke Fear\.',
            'message_template': None,
            'category': 'crowd_control'
        },
        {
            'spell_name': 'Envenomed Bolt',
            'icon_path': 'resources/icons/Envenomed_Bolt.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Envenomed Bolt\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Bond of Death',
            'icon_path': 'resources/icons/bond_of_death.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) has taken (\d+) damage from your Bond of Death\.',
            'message_template': None,
            'category': 'damage'
        },
        {
            'spell_name': 'Screaming Terror',
            'icon_path': 'resources/icons/screaming_terror.png',
            'regex_pattern': r'(\w+(?:\s+\w+)*) begins to scream\.\s*',
            'message_template': '{monster_name} was mezzed!',
            'category': 'crowd_control'
        }
    ])

    # Start positions for each category
    start_positions: Dict[str, Tuple[int, int]] = field(default_factory=lambda: {
        'damage': (960, 100),
        'crowd_control': (960, 300),
        'healing': (960, 500),
    })

    # Per-category appearance settings
    spell_categories: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        'damage': {
            'icon_width': 64,
            'icon_height': 64,
            'font_size': 20,
            'text_color': 'blue',
            'monster_name_font_size': 24,
            'monster_name_text_color': 'white'
        },
        'crowd_control': {
            'icon_width': 64,
            'icon_height': 64,
            'font_size': 20,
            'text_color': 'green',
            'monster_name_font_size': 24,
            'monster_name_text_color': 'white'
        },
        'healing': {
            'icon_width': 64,
            'icon_height': 64,
            'font_size': 20,
            'text_color': 'yellow',
            'monster_name_font_size': 24,
            'monster_name_text_color': 'white'
        }
    })

    animation_duration: int = 4000    # Duration in milliseconds (4 seconds)
    float_distance: int = 150         # Distance in pixels the indicator moves downwards

    padding: int = 10                 # Padding between stacked indicators/groups

    # Total Damage Label Appearance Settings
    total_font_ratio: float = 0.50    # Total damage font size as a ratio of FONT_SIZE
    total_color: str = 'red'          # Color for total damage text

    # Opacity Settings
    opacity: float = 1.0              # Overall opacity (0.1 to 1.0)

    # Font settings
    font_file: str = 'resources/fonts/PressStart2P-Regular.ttf'
    font_family: str = ''  # To be set after loading

    # Configuration file path
    config_file: str = field(init=False)

    # Log file path absolute
    script_dir: str = field(init=False)

    def __post_init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.log_file_path = os.path.join(self.script_dir, self.log_file_path)
        for spell in self.spells:
            spell['icon_path'] = os.path.join(self.script_dir, spell['icon_path'])
        self.config_file = os.path.join(self.script_dir, 'config.json')

    def to_dict(self):
        return {
            'log_file_path': self.log_file_path,
            'spells': self.spells,
            'start_positions': self.start_positions,
            'spell_categories': self.spell_categories,
            'animation_duration': self.animation_duration,
            'float_distance': self.float_distance,
            'padding': self.padding,
            'total_font_ratio': self.total_font_ratio,
            'total_color': self.total_color,
            'opacity': self.opacity,
            'font_file': self.font_file
        }

    def save_to_file(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Failed to save configuration: {e}")

    def load_from_file(self):
        if not os.path.exists(self.config_file):
            print("Configuration file not found. Using default settings.")
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for field_name in self.__dataclass_fields__:
                if field_name in data and field_name not in ('script_dir', 'config_file'):
                    setattr(self, field_name, data[field_name])

            # Ensure that spell_icons paths are absolute
            for spell in self.spells:
                spell['icon_path'] = os.path.join(self.script_dir, os.path.relpath(spell['icon_path'], self.script_dir))

            print(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            print("Using default settings.")
