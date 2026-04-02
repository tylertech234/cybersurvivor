import pygame
import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW, BLACK
from src.systems.weapons import WEAPONS


# Interesting upgrades — a mix of stats, powerful passives, and risky gambles
LEVEL_UPGRADES = [
    # Stat upgrades
    {"name": "Iron Skin",       "icon": "H", "color": (180, 180, 200), "effect": "max_hp",       "value": 25,  "desc": "+25 Max HP and instant heal"},
    {"name": "Power Surge",     "icon": "D", "color": (255, 80, 60),   "effect": "damage",       "value": 8,   "desc": "+8 base damage"},
    {"name": "Quick Trigger",   "icon": "C", "color": (180, 140, 255), "effect": "cooldown",     "value": 60,  "desc": "-60ms attack cooldown"},
    {"name": "Full Repair",     "icon": "+", "color": (50, 220, 50),   "effect": "heal",         "value": 0,   "desc": "Restore all HP"},
    {"name": "Leg Servos",      "icon": "S", "color": (80, 180, 255),  "effect": "speed",        "value": 0.5, "desc": "+0.5 movement speed"},
    # Risky / high-impact
    {"name": "Glass Cannon",    "icon": "G", "color": (255, 50, 50),   "effect": "glass_cannon", "value": 0,   "desc": "+30% damage but lose 20 Max HP"},
    # Passive abilities
    {"name": "Vampiric Strike", "icon": "V", "color": (200, 0, 80),    "effect": "passive", "value": "vampiric_strike", "desc": "Heal 3 HP on each hit"},
    {"name": "Chain Lightning", "icon": "Z", "color": (100, 200, 255), "effect": "passive", "value": "chain_lightning", "desc": "Hits arc to 2 nearby enemies"},
    {"name": "Thorns",          "icon": "T", "color": (180, 100, 50),  "effect": "passive", "value": "thorns",          "desc": "Reflect 30% melee damage taken"},
    {"name": "Second Wind",     "icon": "L", "color": (255, 100, 100), "effect": "passive", "value": "second_wind",     "desc": "Revive once at 30% HP on death"},
    {"name": "Nano Regen",      "icon": "N", "color": (100, 255, 100), "effect": "passive", "value": "nano_regen",      "desc": "Regenerate 1 HP every 2 seconds"},
    {"name": "Berserker",       "icon": "B", "color": (255, 60, 60),   "effect": "passive", "value": "berserker",       "desc": "+50% damage when below 30% HP"},
    {"name": "Shield Matrix",   "icon": "M", "color": (100, 150, 255), "effect": "passive", "value": "shield_matrix",   "desc": "Block one hit every 10 seconds"},
    {"name": "Explosive Kills", "icon": "E", "color": (255, 150, 0),   "effect": "passive", "value": "explosive_kills", "desc": "25% chance for enemies to explode on death"},
    {"name": "Magnetic Field",  "icon": "F", "color": (150, 150, 255), "effect": "passive", "value": "magnetic_field",  "desc": "Pickups fly to you from further away"},
    {"name": "Adrenaline Rush", "icon": "A", "color": (0, 255, 100),   "effect": "passive", "value": "adrenaline",      "desc": "+30% speed for 3s after each kill"},
]


class LevelUpScreen:
    """Pauses the game and presents 3 random upgrade choices."""

    def __init__(self):
        self.active = False
        self.choices: list[dict] = []
        self.selected = 0
        self.font_big = pygame.font.SysFont("consolas", 32, bold=True)
        self.font = pygame.font.SysFont("consolas", 18)
        self.font_small = pygame.font.SysFont("consolas", 14)

    def activate(self, player_weapon_name: str, player_class: str = "knight",
                 player_passives: list = None):
        """Generate 3 random choices: mix of stat upgrades, passives, and weapon swaps."""
        self.active = True
        self.selected = 0
        owned = set(player_passives or [])
        pool = []

        # Add stat + passive upgrades (filter out already-owned passives)
        for u in LEVEL_UPGRADES:
            if u["effect"] == "passive" and u["value"] in owned:
                continue
            if u["effect"] == "glass_cannon" and "glass_cannon" in owned:
                continue
            pool.append({"type": "stat", **u})

        # Add 1-2 weapon options (class-appropriate weapons the player doesn't currently have)
        available_weapons = [k for k in WEAPONS
                           if k != player_weapon_name
                           and WEAPONS[k].get("class") == player_class]
        if available_weapons:
            wpn_picks = random.sample(available_weapons, min(2, len(available_weapons)))
            for wk in wpn_picks:
                w = WEAPONS[wk]
                pool.append({
                    "type": "weapon",
                    "name": w["name"],
                    "icon": "W",
                    "color": w["blade_color"],
                    "effect": "weapon",
                    "value": wk,
                    "desc": w["desc"],
                })

        # Pick 3
        self.choices = random.sample(pool, min(3, len(pool)))

    def handle_event(self, event: pygame.event.Event) -> dict | None:
        """Returns the chosen upgrade dict, or None if still choosing."""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self.selected = (self.selected - 1) % len(self.choices)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self.selected = (self.selected + 1) % len(self.choices)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                choice = self.choices[self.selected]
                self.active = False
                return choice
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                idx = event.key - pygame.K_1
                if 0 <= idx < len(self.choices):
                    choice = self.choices[idx]
                    self.active = False
                    return choice
        return None

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        # Title
        title = self.font_big.render("LEVEL UP — Choose an Upgrade", True, YELLOW)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 120))

        # Cards
        card_w, card_h = 380, 90
        start_y = 200
        for i, choice in enumerate(self.choices):
            cy = start_y + i * (card_h + 15)
            cx = SCREEN_WIDTH // 2 - card_w // 2

            # Highlight selected
            if i == self.selected:
                pygame.draw.rect(surface, (60, 60, 80), (cx - 4, cy - 4, card_w + 8, card_h + 8), border_radius=8)
                pygame.draw.rect(surface, YELLOW, (cx - 4, cy - 4, card_w + 8, card_h + 8), 2, border_radius=8)

            # Card background
            pygame.draw.rect(surface, (30, 30, 40), (cx, cy, card_w, card_h), border_radius=6)
            pygame.draw.rect(surface, choice.get("color", (150, 150, 150)), (cx, cy, card_w, card_h), 2, border_radius=6)

            # Number
            num = self.font.render(f"[{i + 1}]", True, (120, 120, 120))
            surface.blit(num, (cx + 10, cy + 10))

            # Icon
            icon_color = choice.get("color", WHITE)
            icon = self.font_big.render(choice["icon"], True, icon_color)
            surface.blit(icon, (cx + 50, cy + 15))

            # Name
            name = self.font.render(choice["name"], True, WHITE)
            surface.blit(name, (cx + 95, cy + 15))

            # Description
            desc = choice.get("desc", "")
            if desc:
                desc_surf = self.font_small.render(desc, True, (160, 160, 160))
                surface.blit(desc_surf, (cx + 95, cy + 42))

            # Type tag
            tag = "WEAPON" if choice["type"] == "weapon" else "STAT"
            tag_surf = self.font_small.render(tag, True, (100, 100, 100))
            surface.blit(tag_surf, (cx + card_w - tag_surf.get_width() - 10, cy + 65))

        # Hint
        hint = self.font_small.render("W/S or Up/Down to select  |  Enter/Space or 1-3 to confirm", True, (120, 120, 120))
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, start_y + 3 * (card_h + 15) + 20))
