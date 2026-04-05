import pygame
import math
import random
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, YELLOW
from src.systems.weapons import WEAPONS
from src.ui.tooltip import Tooltip


# Big upgrades that can come from boss chests
CHEST_UPGRADES = [
    # Stat boosts (stronger than level-up versions)
    {"name": "Overclocked Blade",  "icon": "D", "color": (255, 80, 60),   "effect": "damage",   "value": 15},
    {"name": "Extended Reach",     "icon": "R", "color": (255, 200, 50),  "effect": "range",    "value": 20},
    {"name": "Turbo Hands",        "icon": "C", "color": (180, 140, 255), "effect": "cooldown", "value": 100},
    {"name": "Reinforced Chassis", "icon": "H", "color": (220, 50, 220),  "effect": "max_hp",   "value": 60},
    {"name": "Emergency Repair",   "icon": "+", "color": (50, 220, 50),   "effect": "heal",     "value": 0},
    {"name": "Overdrive",          "icon": "S", "color": (80, 180, 255),  "effect": "speed",    "value": 1.0},
    # Powerful passive upgrades
    {"name": "Nano Regen",         "icon": "N", "color": (100, 255, 100), "effect": "passive",  "value": "nano_regen"},
    {"name": "Berserker Core",     "icon": "B", "color": (255, 60, 60),   "effect": "passive",  "value": "berserker"},
    {"name": "Shield Matrix",      "icon": "M", "color": (100, 150, 255), "effect": "passive",  "value": "shield_matrix"},
    {"name": "Vampiric Circuits",  "icon": "V", "color": (200, 0, 80),    "effect": "passive",  "value": "vampiric_strike"},
    {"name": "Chain Lightning",    "icon": "Z", "color": (100, 230, 255), "effect": "passive",  "value": "chain_lightning"},
    {"name": "Second Wind",        "icon": "L", "color": (255, 100, 100), "effect": "passive",  "value": "second_wind"},
    {"name": "Explosive Rounds",   "icon": "E", "color": (255, 150, 0),   "effect": "passive",  "value": "explosive_kills"},
]


class BossChest:
    """A glowing chest dropped by a boss, containing 1-5 upgrades."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.alive = True
        self.spawn_time = pygame.time.get_ticks()
        self.size = 28
        self.opened = False

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2,
                           self.size, self.size)

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        if not self.alive:
            return
        now = pygame.time.get_ticks()
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        bob = math.sin(now * 0.003) * 4

        # Outer glow
        glow_r = int(20 + 6 * math.sin(now * 0.004))
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (255, 200, 50, 40), (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (sx - glow_r, int(sy + bob) - glow_r))

        # Chest body
        half = self.size // 2
        body_rect = pygame.Rect(sx - half, int(sy + bob) - half // 2, self.size, half + 4)
        pygame.draw.rect(surface, (120, 80, 30), body_rect, border_radius=3)
        pygame.draw.rect(surface, (180, 140, 50), body_rect, 2, border_radius=3)

        # Lid
        lid_rect = pygame.Rect(sx - half - 2, int(sy + bob) - half // 2 - 6, self.size + 4, 8)
        pygame.draw.rect(surface, (160, 120, 40), lid_rect, border_radius=2)
        pygame.draw.rect(surface, (200, 160, 60), lid_rect, 1, border_radius=2)

        # Lock/gem
        pygame.draw.circle(surface, (255, 220, 50),
                          (sx, int(sy + bob) - half // 2 + 2), 4)
        pygame.draw.circle(surface, (255, 255, 200),
                          (sx, int(sy + bob) - half // 2 + 2), 2)

        # Sparkles
        for i in range(3):
            angle = now * 0.002 + i * 2.1
            sr = 16 + math.sin(now * 0.005 + i) * 4
            sparkx = sx + int(math.cos(angle) * sr)
            sparky = int(sy + bob) + int(math.sin(angle) * sr)
            ss = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(ss, (255, 255, 200, 160), (2, 2), 2)
            surface.blit(ss, (sparkx - 2, sparky - 2))


class ChestRewardScreen:
    """Boss chest — pick one weapon or upgrade from 3 choices. Reroll with coins."""

    def __init__(self):
        self.active = False
        self.rewards: list[dict] = []       # legacy compat; holds [chosen]
        self.font_big = pygame.font.SysFont("consolas", 28, bold=True)
        self.font = pygame.font.SysFont("consolas", 18)
        self.font_small = pygame.font.SysFont("consolas", 14)
        self.font_icon = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_huge = pygame.font.SysFont("consolas", 48, bold=True)
        self.open_time = 0
        self.phase = "idle"  # buildup | choose
        self._sound_manager = None
        self._tooltip = Tooltip()
        self._buildup_duration = 1500
        self._particles: list[dict] = []
        self._player_class = "knight"
        # Choice state
        self._choices: list[dict] = []
        self._selected = 0
        self._reroll_count = 0
        self._reroll_cost = 1
        self._player_ref = None
        self._player_weapon_name = "sword"
        self._upgrade_tiers: dict = {}
        self._arsenal: list = []
        self._reroll_hover = False

    def open_chest(self, player_class: str, player_passives: list = None, sounds=None,
                   player_weapon_name: str = "sword", upgrade_tiers: dict = None,
                   arsenal: list = None, player=None):
        """Start the chest-opening sequence, generating 3 weapon/upgrade choices."""
        self.active = True
        self.open_time = pygame.time.get_ticks()
        self._sound_manager = sounds
        self._player_class = player_class
        self._player_ref = player
        self._player_weapon_name = player_weapon_name
        self._upgrade_tiers = upgrade_tiers or {}
        self._arsenal = arsenal or []
        self._reroll_count = 0
        self._reroll_cost = 1
        self.rewards = []
        self.phase = "buildup"
        self._particles = []
        self._selected = 0
        self._generate_weapon_choices(player_passives)
        if sounds:
            sounds.play("chest_open")

    def _generate_weapon_choices(self, player_passives=None):
        """Build a pool of weapon swaps + weapon upgrades, pick 3."""
        # Lazy import to avoid circular dependency at module load time
        from src.ui.levelup import WEAPON_UPGRADES
        owned_passives = set(player_passives or [])
        tiers = self._upgrade_tiers
        pool = []
        seen = set()

        # Weapon upgrades for equipped + arsenal weapons
        weapons_to_check = ([self._player_weapon_name] +
                            [k for k in self._arsenal if k != self._player_weapon_name])
        for wk in weapons_to_check:
            if wk not in WEAPON_UPGRADES:
                continue
            for wu in WEAPON_UPGRADES[wk]:
                wu_name = wu["name"]
                if wu_name in seen:
                    continue
                current_tier = tiers.get(wu_name, 0)
                if current_tier >= 3:
                    seen.add(wu_name)
                    continue
                next_tier = current_tier + 1
                tier_mult = {1: 1.0, 2: 1.5, 3: 2.0}[next_tier]
                tier_label = {1: "I", 2: "II", 3: "III"}[next_tier]
                entry = dict(wu)
                entry["type"] = "weapon_upgrade"
                entry["tier"] = next_tier
                entry["base_name"] = wu_name
                if next_tier > 1:
                    entry["name"] = f"{wu_name} {tier_label}"
                    sv = wu["value"]
                    if isinstance(sv, (int, float)) and sv != 0:
                        sv = type(sv)(sv * tier_mult)
                    entry["value"] = sv
                pool.append(entry)
                seen.add(wu_name)

        # Weapon swaps (class-appropriate, not currently equipped)
        available = [k for k in WEAPONS
                     if k != self._player_weapon_name
                     and WEAPONS[k].get("class") == self._player_class
                     and k not in (self._arsenal or [])]
        for wk in available:
            w = WEAPONS[wk]
            pool.append({
                "type": "weapon",
                "name": w["name"],
                "icon": "W",
                "color": w.get("blade_color", (200, 200, 200)),
                "effect": "weapon",
                "value": wk,
                "desc": w.get("desc", ""),
            })

        if not pool:
            # Fallback: a flat +10 damage boost
            pool = [{"name": "Emergency Overlock", "icon": "D", "color": (255, 80, 60),
                     "effect": "damage", "value": 10,
                     "desc": "+10 base damage", "type": "stat"}]
        self._choices = random.sample(pool, min(3, len(pool)))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.active:
            return False

        if self.phase == "buildup":
            # Skip buildup on click/key
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    or event.type == pygame.KEYDOWN
                    and event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e)):
                self.phase = "choose"
            return False

        if self.phase == "choose":
            card_w, card_h = 360, 140
            gap = 18
            n = len(self._choices)
            start_x = SCREEN_WIDTH // 2 - (n * card_w + (n - 1) * gap) // 2
            card_y = SCREEN_HEIGHT // 2 - card_h // 2 - 30
            btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, card_y + card_h + 28, 280, 44)

            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                self._reroll_hover = btn_rect.collidepoint(mx, my)
                for i in range(n):
                    cx = start_x + i * (card_w + gap)
                    if cx <= mx <= cx + card_w and card_y <= my <= card_y + card_h:
                        self._selected = i
                        break

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self._selected = (self._selected - 1) % n
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self._selected = (self._selected + 1) % n
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self.rewards = [self._choices[self._selected]]
                    self.active = False
                    if self._sound_manager:
                        self._sound_manager.play("wheel_stop")
                    return True
                elif event.key in (pygame.K_1, pygame.K_KP1): self._selected = 0
                elif event.key in (pygame.K_2, pygame.K_KP2): self._selected = min(1, n - 1)
                elif event.key in (pygame.K_3, pygame.K_KP3): self._selected = min(2, n - 1)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Check card clicks
                for i in range(n):
                    cx2 = start_x + i * (card_w + gap)
                    if cx2 <= mx <= cx2 + card_w and card_y <= my <= card_y + card_h:
                        self.rewards = [self._choices[i]]
                        self.active = False
                        if self._sound_manager:
                            self._sound_manager.play("wheel_stop")
                        return True
                # Check reroll button
                if btn_rect.collidepoint(mx, my):
                    player_coins = getattr(self._player_ref, "coins", 0)
                    if player_coins >= self._reroll_cost:
                        if self._player_ref:
                            self._player_ref.coins -= self._reroll_cost
                        self._reroll_count += 1
                        self._reroll_cost = (1, 2, 4, 8, 15, 25, 40, 60)[min(self._reroll_count, 7)]
                        self._generate_weapon_choices()
                        self._selected = 0
                        self._spawn_explosion()
                        if self._sound_manager:
                            self._sound_manager.play("wheel_tick")
        return False

    def get_rewards(self) -> list[dict]:
        return list(self.rewards)

    def _spawn_explosion(self):
        """Spawn 300+ firework particles for jackpot (5-item roll)."""
        cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        COLORS = [
            (255, 220, 50), (255, 200, 20), (255, 255, 150),
            (255, 120, 50), (255, 255, 255), (200, 255, 100),
            (255, 160, 220), (120, 220, 255),
        ]
        # Central burst — 150 confetti in all directions
        for _ in range(150):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 14)
            self._particles.append({
                "x": float(cx), "y": float(cy),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(0.8, 2.2),
                "age": 0.0,
                "color": random.choice(COLORS),
                "size": random.randint(3, 7),
            })
        # 6 upward fountain rockets — launched from spread positions
        for k in range(6):
            rx = cx + (k - 2.5) * 80
            for _ in range(25):
                angle = random.uniform(-math.pi * 0.7, -math.pi * 0.3)
                speed = random.uniform(8, 18)
                self._particles.append({
                    "x": float(rx), "y": float(cy + 60),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": random.uniform(1.0, 2.5),
                    "age": 0.0,
                    "color": random.choice(COLORS),
                    "size": random.randint(3, 6),
                })
        # Bottom-edge celebration shower
        for _ in range(60):
            bx = random.uniform(0, SCREEN_WIDTH)
            by = float(SCREEN_HEIGHT)
            angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
            speed = random.uniform(10, 20)
            self._particles.append({
                "x": bx, "y": by,
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed,
                "life": random.uniform(1.2, 2.8),
                "age": 0.0,
                "color": random.choice(COLORS),
                "size": random.randint(2, 5),
            })

    def _update_particles(self, dt_s: float):
        alive = []
        for p in self._particles:
            p["age"] += dt_s
            if p["age"] < p["life"]:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 5 * dt_s  # gravity
                alive.append(p)
        self._particles = alive

    def draw(self, surface: pygame.Surface):
        if not self.active:
            return
        now = pygame.time.get_ticks()
        elapsed = now - self.open_time

        # Auto-advance buildup
        if self.phase == "buildup" and elapsed >= self._buildup_duration:
            self.phase = "choose"

        # Particle update
        self._update_particles(1 / 60)

        # Darken background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 210))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        if self.phase == "buildup":
            self._draw_buildup(surface, cx, cy, now, elapsed)
        else:
            self._draw_choices(surface, cx, cy, now)

        # Draw particles
        for p in self._particles:
            alpha = max(0, int(255 * (1 - p["age"] / p["life"])))
            ps = pygame.Surface((p["size"] * 2, p["size"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*p["color"], alpha),
                               (p["size"], p["size"]), p["size"])
            surface.blit(ps, (int(p["x"]) - p["size"], int(p["y"]) - p["size"]))

    def _draw_buildup(self, surface, cx, cy, now, elapsed):
        """Dramatic chest opening anticipation."""
        progress = min(1.0, elapsed / self._buildup_duration)

        # Pulsing glow expanding from center
        glow_r = int(50 + 150 * progress)
        glow_alpha = int(30 + 70 * progress * (0.5 + 0.5 * math.sin(now * 0.01)))
        glow_s = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (255, 200, 50, glow_alpha),
                           (glow_r, glow_r), glow_r)
        surface.blit(glow_s, (cx - glow_r, cy - glow_r))

        # Chest icon (growing)
        chest_size = int(30 + 30 * progress)
        half = chest_size // 2
        # Body
        body_r = pygame.Rect(cx - half, cy - half // 2, chest_size, half + 6)
        pygame.draw.rect(surface, (120, 80, 30), body_r, border_radius=3)
        pygame.draw.rect(surface, (200, 160, 60), body_r, 2, border_radius=3)
        # Lid opening
        lid_open = int(12 * progress)
        lid_r = pygame.Rect(cx - half - 2, cy - half // 2 - 6 - lid_open,
                            chest_size + 4, 8)
        pygame.draw.rect(surface, (160, 120, 40), lid_r, border_radius=2)
        pygame.draw.rect(surface, (200, 160, 60), lid_r, 1, border_radius=2)
        # Lock
        pygame.draw.circle(surface, (255, 220, 50),
                           (cx, cy - half // 2 + 2), 4)

        # Light rays from chest
        if progress > 0.3:
            ray_alpha = int(100 * (progress - 0.3) / 0.7)
            for i in range(8):
                angle = now * 0.001 + i * math.pi / 4
                rx = cx + math.cos(angle) * glow_r * 0.8
                ry = cy + math.sin(angle) * glow_r * 0.8 - 20
                ls = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(ls, (255, 255, 200, ray_alpha), (3, 3), 3)
                surface.blit(ls, (int(rx) - 3, int(ry) - 3))

        # Title
        title = self.font_big.render("BOSS CHEST", True, (255, 220, 50))
        surface.blit(title, (cx - title.get_width() // 2, cy - 120))

        # Suspense text
        dots = "." * (1 + (now // 400) % 3)
        hint = self.font.render(f"Opening{dots}", True, (200, 200, 200))
        surface.blit(hint, (cx - hint.get_width() // 2, cy + 80))

    def _draw_choices(self, surface, cx, cy, now):
        """Draw 3 weapon/upgrade choice cards + reroll button."""
        card_w, card_h = 360, 140
        gap = 18
        n = len(self._choices)
        total_w = n * card_w + (n - 1) * gap
        start_x = cx - total_w // 2
        card_y = cy - card_h // 2 - 30

        # Title
        title = self.font_big.render("BOSS CHEST — CHOOSE ONE", True, (255, 220, 50))
        surface.blit(title, (cx - title.get_width() // 2, card_y - 52))

        for i, choice in enumerate(self._choices):
            hovered = (i == self._selected)
            c_col = tuple(choice.get("color", (180, 180, 200)))
            cx2 = start_x + i * (card_w + gap)

            # Card background
            bg = (40, 44, 55, 235) if hovered else (22, 24, 32, 215)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, bg, (0, 0, card_w, card_h), border_radius=8)
            bw = 3 if hovered else 1
            pygame.draw.rect(card_surf, (*c_col, 255), (0, 0, card_w, card_h), bw, border_radius=8)

            # Hover glow
            if hovered:
                glow_a = int(30 + 20 * math.sin(now * 0.006))
                glow = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                glow.fill((*c_col, glow_a))
                card_surf.blit(glow, (0, 0))

            # Type tag
            ctype = choice.get("type", "stat")
            if ctype == "weapon":
                tag, tag_col = "NEW WEAPON", (255, 200, 80)
            elif ctype == "weapon_upgrade":
                tier_lbl = {1: "I", 2: "II", 3: "III"}.get(choice.get("tier", 1), "I")
                tag, tag_col = f"UPGRADE  TIER {tier_lbl}", (100, 220, 255)
            else:
                tag, tag_col = "STAT BOOST", (120, 220, 120)
            tag_t = self.font_small.render(tag, True, tag_col)
            card_surf.blit(tag_t, (12, 10))

            # Icon circle
            pygame.draw.circle(card_surf, c_col, (36, 72), 24)
            icon_ch = self.font_icon.render(str(choice.get("icon", "?")), True, (255, 255, 255))
            card_surf.blit(icon_ch, (36 - icon_ch.get_width() // 2, 72 - icon_ch.get_height() // 2))

            # Name
            name_t = self.font.render(choice["name"], True, c_col if not hovered else (255, 255, 255))
            card_surf.blit(name_t, (72, 34))

            # Desc (wrap at ~38 chars)
            desc = str(choice.get("desc", ""))
            words = desc.split()
            lines, cur = [], ""
            for w in words:
                if len(cur) + len(w) + 1 <= 38:
                    cur = (cur + " " + w).strip()
                else:
                    if cur:
                        lines.append(cur)
                    cur = w
            if cur:
                lines.append(cur)
            for li, ln in enumerate(lines[:2]):
                lt = self.font_small.render(ln, True, (180, 180, 190))
                card_surf.blit(lt, (72, 60 + li * 16))

            # Number hint
            num_t = self.font_small.render(f"[{i + 1}]", True, (100, 100, 110))
            card_surf.blit(num_t, (card_w - num_t.get_width() - 8, card_h - num_t.get_height() - 8))

            surface.blit(card_surf, (cx2, card_y))

        # Reroll button
        cost = self._reroll_cost
        can_reroll = getattr(self._player_ref, "coins", 0) >= cost
        btn_y = card_y + card_h + 28
        btn_rect = pygame.Rect(cx - 140, btn_y, 280, 44)
        btn_col = (60, 200, 80) if (can_reroll and self._reroll_hover) else \
                  (40, 140, 60) if can_reroll else (80, 80, 80)
        pygame.draw.rect(surface, btn_col, btn_rect, border_radius=8)
        pygame.draw.rect(surface, (200, 220, 200), btn_rect, 1, border_radius=8)
        coin_sym = "\u25cf"
        btn_label = f"Reroll  {coin_sym}{cost}"
        if not can_reroll:
            btn_label += "  (need more coins)"
        bl = self.font.render(btn_label, True, (255, 255, 255) if can_reroll else (130, 130, 130))
        surface.blit(bl, (cx - bl.get_width() // 2, btn_y + 12))

        # Coins display
        coins = getattr(self._player_ref, "coins", 0)
        coin_t = self.font_small.render(f"Coins: {coin_sym}{coins}", True, (255, 210, 60))
        surface.blit(coin_t, (cx - coin_t.get_width() // 2, btn_y + 60))

        # Instructions
        hint = self.font_small.render("Click a card or press 1/2/3  |  ENTER to confirm selection", True, (120, 120, 130))
        surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 36))

    def _draw_rewards(self, surface, cx, cy, now):
        """Draw revealed reward cards."""
        num_rewards = len(self.rewards)
        shown = min(self._reveal_index, num_rewards)

        # Title with reward count
        color_title = (255, 255, 100) if num_rewards >= 4 else (255, 220, 50)
        title_text = "JACKPOT!" if self._jackpot else f"{num_rewards} REWARD{'S' if num_rewards > 1 else ''}!"
        title = self.font_big.render(title_text, True, color_title)
        surface.blit(title, (cx - title.get_width() // 2, 40))

        # Jackpot flash background — bright golden pulse
        if self._jackpot and self.phase == "revealed":
            flash = int(90 + 70 * math.sin(now * 0.007))
            fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fs.fill((255, 220, 50, flash))
            surface.blit(fs, (0, 0))
            # Screen-edge gold glow
            edge = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            edge_a = int(60 + 50 * math.sin(now * 0.009))
            for t in range(18):
                a = max(0, edge_a - t * 4)
                pygame.draw.rect(edge, (255, 200, 0, a), (t, t, SCREEN_WIDTH - t * 2, SCREEN_HEIGHT - t * 2), 2)
            surface.blit(edge, (0, 0))

        # Layout cards
        card_w, card_h = 360, 70
        total_h = num_rewards * (card_h + 12) - 12
        start_y = cy - total_h // 2

        for i in range(shown):
            reward = self.rewards[i]
            r_col = reward.get("color", (180, 180, 180))
            card_y = start_y + i * (card_h + 12)

            # Card entrance slide-in
            reveal_age = now - (self._reveal_time if self.phase == "revealed"
                                else self._reveal_time + i * self._reveal_interval)
            if self.phase == "revealing":
                reveal_age = now - (self._reveal_time + i * self._reveal_interval)
            slide = min(1.0, max(0.0, reveal_age / 200))
            card_x = int(cx - card_w // 2 - 60 * (1 - slide))
            alpha = int(255 * slide)

            # Card background
            card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            bg_color = (30, 30, 40, min(220, alpha))
            pygame.draw.rect(card, bg_color, (0, 0, card_w, card_h),
                             border_radius=6)
            border_col = (*r_col, min(255, alpha))
            pygame.draw.rect(card, border_col, (0, 0, card_w, card_h),
                             2, border_radius=6)

            # Icon circle
            icon_cx, icon_cy = 35, card_h // 2
            pygame.draw.circle(card, (*r_col, min(200, alpha)),
                               (icon_cx, icon_cy), 18)
            icon_t = self.font_icon.render(reward["icon"], True, (255, 255, 255))
            icon_t.set_alpha(alpha)
            card.blit(icon_t, (icon_cx - icon_t.get_width() // 2,
                               icon_cy - icon_t.get_height() // 2))

            # Name
            name_t = self.font.render(reward["name"], True, r_col)
            name_t.set_alpha(alpha)
            card.blit(name_t, (65, 12))

            # Effect tag
            if reward["effect"] == "weapon":
                tag = "WEAPON"
            elif reward["effect"] == "passive":
                tag = "PASSIVE"
            else:
                tag = "STAT BOOST"
            tag_t = self.font_small.render(tag, True, (150, 150, 160))
            tag_t.set_alpha(alpha)
            card.blit(tag_t, (65, 38))

            surface.blit(card, (card_x, card_y))

        # Instructions
        if self.phase == "revealing":
            hint = self.font_small.render("Press SPACE to skip...",
                                          True, (120, 120, 120))
        elif self.phase == "revealed":
            hint = self.font.render("Press SPACE to continue",
                                    True, (180, 180, 180))
        else:
            hint = self.font_small.render("...", True, (100, 100, 100))
        surface.blit(hint, (cx - hint.get_width() // 2, SCREEN_HEIGHT - 50))
