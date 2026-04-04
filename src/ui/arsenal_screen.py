import pygame
import math
from src.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.systems.weapons import WEAPONS
from src.font_cache import get_font


class ArsenalScreen:
    """Pause-menu weapon picker — shows all collected weapons and lets the player equip one."""

    def __init__(self):
        self.active = False
        self.arsenal: list[str] = []
        self.current_key: str = ""
        self.selected: int = 0

    def activate(self, arsenal: list[str], current_key: str):
        self.arsenal = list(arsenal)
        self.current_key = current_key
        self.selected = arsenal.index(current_key) if current_key in arsenal else 0
        self.active = True

    def handle_event(self, event: pygame.event.Event) -> dict | None:
        """Returns {'action': 'equip', 'weapon': key}, {'action': 'close'}, or None."""
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.selected = (self.selected - 1) % max(1, len(self.arsenal))
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.selected = (self.selected + 1) % max(1, len(self.arsenal))
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                key = self.arsenal[self.selected] if self.arsenal else self.current_key
                self.active = False
                if key != self.current_key:
                    return {"action": "equip", "weapon": key}
                return {"action": "close"}
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                return {"action": "close"}

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, rect in enumerate(self._card_rects()):
                if rect.collidepoint(mx, my):
                    if i == self.selected:
                        key = self.arsenal[i]
                        self.active = False
                        if key != self.current_key:
                            return {"action": "equip", "weapon": key}
                        return {"action": "close"}
                    self.selected = i
        return None

    def _card_rects(self) -> list[pygame.Rect]:
        n = max(1, len(self.arsenal))
        card_w, card_h = 200, 200
        gap = 16
        total_w = n * card_w + (n - 1) * gap
        # clamp so it never overflows the screen (scroll not needed — max ~14 weapons)
        start_x = max(10, SCREEN_WIDTH // 2 - total_w // 2)
        card_y = SCREEN_HEIGHT // 2 - card_h // 2 + 10
        return [pygame.Rect(start_x + i * (card_w + gap), card_y, card_w, card_h)
                for i in range(len(self.arsenal))]

    # ------------------------------------------------------------------ draw
    def draw(self, surface: pygame.Surface):
        if not self.active:
            return

        now = pygame.time.get_ticks()

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))

        font_big = get_font("consolas", 34, True)
        font = get_font("consolas", 16, True)
        font_sm = get_font("consolas", 13)

        title = font_big.render("WEAPON ARSENAL", True, (255, 220, 50))
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 40))

        if len(self.arsenal) <= 1:
            sub = font_sm.render("Collect more weapons from level-up rewards to unlock switching.", True, (130, 130, 150))
            surface.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 90))

        hint = font_sm.render("← → to browse  •  Enter / E to equip  •  ESC to close", True, (100, 100, 120))
        surface.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 38))

        cards = self._card_rects()
        for i, (key, rect) in enumerate(zip(self.arsenal, cards)):
            wpn = WEAPONS.get(key, {})
            is_selected = (i == self.selected)
            is_equipped = (key == self.current_key)
            color = wpn.get("blade_color", (180, 180, 200))

            # Pulsing border for selected card
            pulse = 0.5 + 0.5 * math.sin(now * 0.006)
            border_alpha = int(180 + 75 * pulse) if is_selected else 180

            bg = (55, 50, 20) if is_selected else (22, 22, 34)
            pygame.draw.rect(surface, bg, rect, border_radius=10)

            if is_selected:
                border_col = (255, 220, 50)
                bw = 3
            elif is_equipped:
                border_col = (60, 220, 100)
                bw = 2
            else:
                border_col = (70, 70, 90)
                bw = 1
            pygame.draw.rect(surface, border_col, rect, bw, border_radius=10)

            inner_y = rect.y + 12
            cx = rect.centerx

            # EQUIPPED badge
            if is_equipped:
                badge = font_sm.render("● EQUIPPED", True, (60, 220, 90))
                surface.blit(badge, (cx - badge.get_width() // 2, inner_y))
            inner_y += 20

            # Weapon name
            name_surf = font.render(wpn.get("name", key), True, color)
            surface.blit(name_surf, (cx - name_surf.get_width() // 2, inner_y))
            inner_y += 22

            # Simple visual icon — a coloured shape representing the weapon
            icon_rect = pygame.Rect(cx - 30, inner_y, 60, 60)
            _draw_weapon_icon(surface, key, wpn, cx, inner_y + 30, color, now)
            inner_y += 68

            # Stats
            stats = [
                f"Dmg: x{wpn.get('damage_mult', 1.0):.1f}",
                f"Range: {wpn.get('range', '?')} px",
                f"CD: {wpn.get('cooldown', '?')} ms",
            ]
            for line in stats:
                s = font_sm.render(line, True, (170, 170, 190))
                surface.blit(s, (rect.x + 10, inner_y))
                inner_y += 16

            # Desc snippet
            desc = wpn.get("desc", "")
            if desc:
                # Wrap at 22 chars
                words = desc.split()
                lines, cur = [], ""
                for w in words:
                    if len(cur) + len(w) + 1 > 22:
                        lines.append(cur.strip())
                        cur = w
                    else:
                        cur += " " + w
                if cur:
                    lines.append(cur.strip())
                for line in lines[:2]:
                    ds = font_sm.render(line, True, (120, 120, 140))
                    surface.blit(ds, (rect.x + 6, inner_y))
                    inner_y += 14


def _draw_weapon_icon(surface: pygame.Surface, key: str, wpn: dict,
                      cx: int, cy: int, color: tuple, now: int):
    """Draw a tiny procedural silhouette for a weapon preview."""
    bob = math.sin(now * 0.004) * 2
    cy = int(cy + bob)
    is_proj = wpn.get("projectile", False)
    is_orb = wpn.get("orbiter", False)

    if is_orb:
        # Orbiting blades — circle of dots
        for a in range(3):
            ang = now * 0.003 + a * 2.094
            px = cx + int(math.cos(ang) * 22)
            py = cy + int(math.sin(ang) * 22)
            pygame.draw.circle(surface, color, (px, py), 5)
    elif is_proj:
        # Arrow / bolt pointing right
        pygame.draw.line(surface, color, (cx - 22, cy), (cx + 22, cy), 3)
        pygame.draw.polygon(surface, color,
                            [(cx + 22, cy), (cx + 12, cy - 6), (cx + 12, cy + 6)])
    else:
        # Melee — simple blade shape
        sword_len = max(20, min(30, wpn.get("range", 60) // 2))
        sweep = wpn.get("sweep_deg", 90)
        # Draw a thick diagonal line as blade
        angle = math.radians(-45)
        ex = cx + int(math.cos(angle) * sword_len)
        ey = cy + int(math.sin(angle) * sword_len)
        pygame.draw.line(surface, color, (cx, cy), (ex, ey), 4)
        # Guard
        perp = math.radians(-45 + 90)
        g = 8
        gx1 = cx + int(math.cos(perp) * g)
        gy1 = cy + int(math.sin(perp) * g)
        gx2 = cx - int(math.cos(perp) * g)
        gy2 = cy - int(math.sin(perp) * g)
        pygame.draw.line(surface, (200, 200, 200), (gx1, gy1), (gx2, gy2), 2)
