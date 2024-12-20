import os
from config import Config
from .indicators import DamageIndicator, SpecialIndicator, TotalDamageLabel, MonsterNameLabel

class GroupIndicator:
    def __init__(self, damage_events, overlay, category_offset, config: Config, category: str, monster_name: str):
        self.damage_events = damage_events
        self.overlay = overlay
        self.category_offset = category_offset  # Starting vertical offset for this category
        self.config = config
        self.font_family = config.font_family
        self.category = category
        self.monster_name = monster_name
        self.indicators = []
        self.total_label = None
        self.monster_label = None
        self.used_height = 0
        self.init_group()

    def init_group(self):
        start_x, base_start_y = self.config.start_positions.get(self.category, (960, 100))

        # The actual start_y for this group is base_start_y + category_offset
        start_y = base_start_y + self.category_offset

        cat_conf = self.config.spell_categories[self.category]
        monster_name_font_size = cat_conf['monster_name_font_size']

        # Place monster name label at the top
        monster_label_y = start_y
        self.monster_label = MonsterNameLabel(
            self.monster_name,
            start_x,
            monster_label_y,
            self.font_family,
            self.config,
            self.category
        )
        self.monster_label.show()

        current_y = monster_label_y + self.monster_label.height() + self.config.padding

        # Place damage and special indicators
        for event in self.damage_events:
            if event['type'] == 'damage':
                damage = event['damage']
                spell_name = event['spell_name']
                icon_path = self.config.spells_dict.get(spell_name, {}).get('icon_path', None)
                if not icon_path or not os.path.exists(icon_path):
                    continue

                indicator = DamageIndicator(
                    damage,
                    icon_path,
                    start_x,
                    current_y,
                    self.font_family,
                    self.config,
                    self.category
                )
                indicator.show()
                self.indicators.append({'widget': indicator, 'category': self.category})
                current_y += indicator.height() + self.config.padding

            elif event['type'] == 'special':
                message = event['message']
                spell_name = event['spell_name']
                icon_path = self.config.spells_dict.get(spell_name, {}).get('icon_path', None)
                if not icon_path or not os.path.exists(icon_path):
                    continue

                indicator = SpecialIndicator(
                    message,
                    icon_path,
                    start_x,
                    current_y,
                    self.font_family,
                    self.config,
                    self.category
                )
                indicator.show()
                self.indicators.append({'widget': indicator, 'category': self.category})
                current_y += indicator.height() + self.config.padding

        # Calculate total damage if needed
        category_damage = sum(e['damage'] for e in self.damage_events if e['type'] == 'damage')
        damage_event_count = len([event for event in self.damage_events if event['type'] == 'damage'])

        if damage_event_count >= 2:
            self.total_label = TotalDamageLabel(
                category_damage,
                start_x,
                current_y,
                self.font_family,
                self.config,
                self.category,
                monster_name=self.monster_name
            )
            self.total_label.show()
            current_y += self.total_label.height() + self.config.padding

        # Track how much vertical space this group used
        self.used_height = current_y - monster_label_y

    def final_group_height(self):
        # Return the total vertical space consumed by this group
        return self.used_height

    def is_active(self):
        active = True
        if self.monster_label and not self.monster_label.isVisible():
            active = False
        for ind in self.indicators:
            if not ind['widget'].isVisible():
                active = False
        if self.total_label and not self.total_label.isVisible():
            active = False
        return active
