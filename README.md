# Hack 'n Slash

A 2D top-down hack and slash game built with Python + Pygame. No external assets — all graphics are drawn with code, all sounds are procedurally generated.

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrow Keys | Move |
| Space / J / Left Click | Attack |
| Shift / K | Dash (i-frames) |
| Mouse | Aim direction |
| 1-3 / 1-5 | Select upgrades |
| R | Restart (on death) |
| ESC | Quit |

## Features

- **3 Character Classes** — Knight (heavy melee), Archer (fast ranged), Jester (chaotic fun)
- **16+ Weapons** — Swords, axes, throwing daggers, banana boomerangs, confetti grenades, and more
- **Wave-based combat** with escalating difficulty (+12% HP, +8% damage, +3% speed per wave)
- **Boss waves** every 3rd/5th wave with dedicated HP bars and arena-cleared encounters
- **Parry system** — Melee attacks deflect enemy projectiles
- **Orbiting projectiles** — Bananas and blades orbit the player after returning
- **Passive abilities** — Lifesteal, crits, evasion, armor, chain lightning, vampiric strike, thorns, second wind, explosive kills
- **Roguelite persistence** — Legacy Points and 6 permanent upgrades that carry between runs
- **Dynamic lighting** — Darkness grows away from the campfire, scaling enemy stats and XP rewards
- **Procedural audio** — Two-layer 8-bit chiptune (calm/combat crossfade) and generated SFX
- **AVP-style radar** — Motion tracker with sweep-line and proximity beeps
- **Status effects** — Fire, bleed, poison, slow with visual particles
- **Boss chests** — Powerful upgrades from defeated bosses
- **Campfire healing** between waves
- **Fruit trees** you can hit for apples
- **Floating damage numbers** with scale-pop and outlines
- **Red danger vignette** when HP is critically low

## Project Structure

```
hacknslash/
├── main.py                  # Entry point
├── requirements.txt
└── src/
    ├── settings.py          # All tunable constants
    ├── game.py              # Main game loop & state orchestrator
    ├── entities/
    │   ├── player.py        # Player: 3 classes, movement, attacks, leveling
    │   └── enemy.py         # Enemy AI: Dalek, Wraith, Mini-Boss, Big Boss
    ├── systems/
    │   ├── combat.py        # Hit detection, damage, XP rewards
    │   ├── spawner.py       # Wave spawning, patterns, boss waves, scaling
    │   ├── projectiles.py   # Bullets, daggers, orbiters, grenades
    │   ├── weapons.py       # Weapon definitions and drawing
    │   ├── pickups.py       # Item drops and collection
    │   ├── boss_chest.py    # Boss chest rewards
    │   ├── game_actions.py  # Death processing & projectile firing helpers
    │   ├── legacy.py        # Roguelite persistence (JSON save)
    │   ├── environment.py   # Trees, rocks, fruit trees
    │   ├── campfire.py      # Between-wave healing
    │   ├── lighting.py      # Dynamic darkness system
    │   ├── animations.py    # Particles, screen shake, death effects
    │   ├── sounds.py        # Procedural SFX + 8-bit music generation
    │   ├── status_effects.py # DOT effects and debuffs
    │   ├── camera.py        # Smooth-follow camera
    │   └── game_map.py      # Tile-based world
    └── ui/
        ├── hud.py           # HP/XP bars, boss HP, wave info, low-HP vignette
        ├── radar.py         # Motion tracker
        ├── levelup.py       # Level-up upgrade selection
        ├── charselect.py    # Character class picker
        └── legacy_screen.py # Post-death permanent upgrade shop
```

## Gameplay Guide

See [GAMEPLAY.md](GAMEPLAY.md) for a full guide covering classes, weapons, parry, enemies, boss chests, and tips.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions and how to make your first contribution.
