# Copilot Instructions for Hacknslash

## Project Overview
Python + Pygame hack-and-slash survival game. ~5500 LOC, procedural graphics and audio (zero external assets).

## Architecture
- Entry: `main.py` → `src/game.py` Game class
- Game loop: `_handle_events()` → `_update(dt, now)` → `_draw()`
- `dt` = milliseconds from `clock.tick(60)`, `now` = `pygame.time.get_ticks()`

## Key File Roles
| File | What it does |
|------|-------------|
| `src/game.py` | Main orchestrator (~500 lines) — wires all systems, processes kills, applies passives |
| `src/settings.py` | All game constants (display, player, enemy, spawning, XP, lighting) |
| `src/entities/player.py` | Player state, 3 class draw methods, damage/evasion/shield logic |
| `src/entities/enemy.py` | 4 enemy types (dalek/wraith/mini_boss/big_boss), AI, draw |
| `src/systems/weapons.py` | Weapon stat dicts + procedural draw functions per weapon |
| `src/systems/combat.py` | Melee hit resolution, passives (vampiric/chain/thorns) |
| `src/systems/game_actions.py` | Enemy death processing + player projectile firing helpers |
| `src/systems/projectiles.py` | ThrownDagger, OrbitingProjectile, ConfettiGrenade + collision |
| `src/systems/spawner.py` | Wave patterns, boss wave triggers, difficulty scaling |
| `src/systems/boss_chest.py` | Chest upgrade pool + reward selection screen |
| `src/systems/pickups.py` | Item drops + magnetic field passive |
| `src/systems/status_effects.py` | Fire/bleed/poison/slow with tick damage |
| `src/systems/legacy.py` | Roguelite persistence (JSON save, 6 permanent upgrades) |
| `src/systems/sounds.py` | All procedural SFX + 2-layer chiptune music |
| `src/ui/hud.py` | In-game HUD (HP/XP bars, boss HP, wave info, vignette) |
| `src/ui/charselect.py` | 3-class picker |
| `src/ui/levelup.py` | Level-up upgrade choices |
| `src/ui/radar.py` | Motion tracker |
| `src/ui/legacy_screen.py` | Post-death permanent upgrade shop |

## Conventions
- All graphics are drawn with `pygame.draw.*` — no image files
- All audio is generated with `pygame.sndarray` — no sound files  
- Weapon definitions are dicts in `weapons.py` with keys: `name`, `damage_mult`, `range`, `cooldown`, `duration`, `sweep_deg`, `projectile` (bool), `type` (melee/ranged/orbiter/grenade)
- Passives are tracked in `player.passives` list of strings. Check with `"name" in self.player.passives`
- Enemy types are defined in `enemy.py` ENEMY_TYPES dict at the top
- When adding a passive: define in upgrade pool (boss_chest.py or levelup.py), then implement the check in game.py _update() or player.py or combat.py

## Testing
- Quick compile check: `python -c "from src.game import Game; print('OK')"`
- Run game: `python main.py`
- No test framework — verify by running the game
