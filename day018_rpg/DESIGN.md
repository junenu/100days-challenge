# Crystal Shards — Design Document

## Overview

Top-down action RPG. The hero must retrieve 3 Crystal Shards from three dungeons
(Forest, Cave, Dark Tower) to save the village from a dark wizard.

---

## Game States

```
TITLE ──► VILLAGE ──► DUNGEON_1 ──► DUNGEON_2 ──► DUNGEON_3 ──► VICTORY
             │                                                      ▲
             └──────────── (return after each shard) ──────────────┘
                    GAME_OVER (HP = 0, press R to restart)
```

State transitions:
- TITLE → VILLAGE on Enter
- VILLAGE → DUNGEON_N when player walks into a portal
- DUNGEON_N → VILLAGE when player picks up the Crystal Shard (boss drops it)
- Any state → GAME_OVER when player HP ≤ 0
- DUNGEON_3 → VICTORY after collecting all 3 shards

---

## Window & Tile Config

| Parameter       | Value          |
|----------------|----------------|
| Window size     | 960 × 640 px   |
| Tile size       | 40 × 40 px     |
| FPS target      | 60             |
| Map size        | 24 × 16 tiles  |
| Camera          | Centered on player, clamped to map bounds |

---

## Tile Types

| ID | Name    | Color (RGB)      | Walkable |
|----|---------|------------------|----------|
| 0  | WALL    | (60, 40, 30)     | No       |
| 1  | FLOOR   | (110, 90, 70)    | Yes      |
| 2  | GRASS   | (60, 100, 50)    | Yes      |
| 3  | WATER   | (40, 80, 160)    | No       |
| 4  | PORTAL  | (180, 100, 220)  | Yes (trigger) |
| 5  | STONE   | (100, 100, 110)  | Yes      |

---

## Map Layouts (24 × 16 tiles, 0=WALL, 1=FLOOR, etc.)

Each area is a 2D list. Design them with a border of WALLs and interior of walkable tiles.
Include:
- **VILLAGE**: 2×2 grass area, house outlines (walls), NPC at (12, 8),
  3 portals (bottom row) labelled Forest / Cave / Tower.
  Only Forest portal is active at start; Cave unlocks after shard 1; Tower after shard 2.
- **DUNGEON_1 (Forest)**: stone floor, obstacle walls, 6–8 Slimes + 2 Goblins,
  1 Forest Boss (Giant Slime) at map center. Boss drops Crystal Shard 1.
- **DUNGEON_2 (Cave)**: narrower corridors, 6 Goblins + 4 Skeletons,
  1 Cave Boss (Bone Knight) at center. Drops Crystal Shard 2.
- **DUNGEON_3 (Dark Tower)**: dense walls, 8 Skeletons + 4 Dark Orbs,
  Final Boss (Dark Wizard) at center. Drops Crystal Shard 3 → VICTORY.

Maps can be hard-coded as Python lists or procedurally generated — implementer's choice.

---

## Player

### Initial Stats
| Stat    | Value |
|---------|-------|
| HP      | 80    |
| Max HP  | 80    |
| MP      | 30    |
| Max MP  | 30    |
| ATK     | 12    |
| DEF     | 4     |
| SPD     | 180 px/s |
| Level   | 1     |
| XP      | 0     |
| XP Next | 30    |
| Gold    | 0     |
| Potions | 2     |

### Level Up (every xp_next XP, xp_next *= 1.6 each time)
- Max HP +10, HP fully restored
- Max MP +5
- ATK +3
- DEF +1

### Controls
| Key       | Action              |
|-----------|---------------------|
| WASD      | Move                |
| Space     | Melee attack (arc in front, range 55 px) |
| E         | Use potion          |
| Enter     | Confirm / interact  |
| Escape    | Pause / back to title |

### Visual
- Body: yellow circle, radius 16
- Direction indicator: small white triangle pointing in move direction
- Attack flash: white arc drawn for 12 frames when attacking

---

## Enemies

### Base class
Each enemy has: x, y, hp, max_hp, atk, def, spd, xp_value, gold_value, aggro_range, attack_range, attack_cooldown.

### Enemy Types
| Name        | Color         | HP | ATK | DEF | SPD  | XP | Gold | Aggro | Atk range | Cooldown |
|-------------|---------------|----|-----|-----|------|----|------|-------|-----------|----------|
| Slime       | (80,200,80)   | 18 |  6  |  0  |  80  |  6 |   3  | 160   |    40     |  1.2 s   |
| Goblin      | (180,80,40)   | 28 |  9  |  1  | 110  | 10 |   6  | 200   |    45     |  1.0 s   |
| Skeleton    | (220,220,200) | 40 | 13  |  2  |  90  | 16 |  10  | 220   |    48     |  0.9 s   |
| Dark Orb    | (100,30,180)  | 30 | 11  |  0  | 120  | 14 |   8  | 250   |   200     |  1.5 s   |

Dark Orb shoots a projectile toward the player (range 200, projectile spd 220 px/s).

### Bosses
| Name          | Color         | HP  | ATK | DEF | SPD | XP  | Gold | Notes                      |
|---------------|---------------|-----|-----|-----|-----|-----|------|----------------------------|
| Giant Slime   | (30,180,30)   | 120 | 14  |  2  |  70 |  60 |  40  | Splits into 2 Slimes at 50% HP |
| Bone Knight   | (240,240,210) | 200 | 20  |  6  |  85 | 100 |  70  | Charge attack every 4 s    |
| Dark Wizard   | (80,20,140)   | 280 | 18  |  4  |  75 | 160 | 120  | 3-phase: adds orbs at 66%/33% |

---

## Items

| Name           | Char | Color          | Effect                        | Drop rate |
|----------------|------|----------------|-------------------------------|-----------|
| Health Potion  | ●    | (220,60,60)    | +30 HP                        | 30% enemies |
| Gold Coin      | ◆    | (255,215,0)    | +random(3,12) gold            | 60% enemies |
| Crystal Shard  | ✦    | (150,200,255)  | Story item — triggers warp    | Boss only |

Player auto-picks up Gold Coins on overlap. Potions are picked up and stored (max 5).
Crystal Shards trigger area completion automatically.

---

## Combat Resolution

```
damage_dealt = max(1, attacker.atk + randint(-2, 3) - defender.def)
```

Melee attack hits all enemies within `attack_range` pixels in a 120° arc in front.
Hit enemies flash white for 8 frames and are knocked back 20 px.

---

## HUD Layout

Rendered at fixed screen coordinates (not affected by camera):

```
┌─────────────────────────────────────────────────────┐
│ [HP ████████░░] 72/80   [MP ██████░░░░] 18/30       │
│ Lv:3  XP:45/77  Gold:88  Potions:2  Shards: ●●○     │
└─────────────────────────────────────────────────────┘
```

Panel: semi-transparent black rect at top, height 56 px.
HP bar: red fill. MP bar: blue fill. Shard dots: filled=cyan, empty=dark gray.

---

## Dialogue System

Simple one-shot dialogue boxes (bottom of screen, semi-transparent):
- Triggered when player presses Enter near an NPC
- Shows NPC name + 1–3 lines of text
- Dismiss with Enter

NPC lines (VILLAGE):
> "The Crystal of Light has been shattered! Three shards fell into the Forest,
>  the Cave, and the Dark Tower. You are our only hope, hero!"

---

## Visual Style (pygame.draw only)

| Object       | Shape                                | Colors                          |
|--------------|--------------------------------------|---------------------------------|
| Player       | circle(r=16) + triangle for dir      | Yellow / White                  |
| Slime        | circle(r=14) with oval "eyes"        | Green                           |
| Goblin       | circle(r=14) + pointed "ears"        | Orange-red                      |
| Skeleton     | circle(r=14) + crossed "bones"       | Off-white                       |
| Dark Orb     | circle(r=12) pulsing + halo          | Purple                          |
| Giant Slime  | circle(r=26) + eyes                  | Bright green                    |
| Bone Knight  | rect body + circle head              | Off-white / gray                |
| Dark Wizard  | tall rect + triangle hat + circle    | Dark purple / magenta           |
| Projectile   | small circle(r=6)                    | Purple                          |
| Portals      | animated ring of circles             | Purple (unlit=gray)             |
| Crystal Shard| rotated rect, sparkling              | Cyan/white                      |
| NPC          | circle + rect body                   | Blue                            |

All entities cast a soft shadow: dark semi-transparent ellipse drawn under them.

---

## Audio

No audio required (pygame.mixer not needed). Optional: pygame.mixer.Sound with
generated beeps if implementer wishes.

---

## Code Architecture Notes

- **No external assets** — only stdlib + pygame.
- Use a `Camera` class with `apply(rect)` → offset rect for rendering.
- Use `pygame.sprite.Group` for enemies and items.
- `GameState` enum: TITLE, VILLAGE, DUNGEON_1/2/3, GAME_OVER, VICTORY.
- Delta-time movement: `pos += spd * dt` so frame rate doesn't affect speed.
- Enemy AI: if `dist(enemy, player) < aggro_range` → move toward player;
  if `dist < attack_range` and cooldown elapsed → attack.
- Keep each file under 300 lines; split logic cleanly per the file list.

---

## File Responsibilities

| File         | Responsibility                                              |
|--------------|-------------------------------------------------------------|
| main.py      | `pygame.init`, window, clock, state machine, main loop      |
| config.py    | All constants — sizes, colors, stats (no logic)             |
| world.py     | `TileMap` (render tiles), `Area` (holds map + spawn lists)  |
| entities.py  | `Entity`, `Player`, `Enemy` subclasses, `Item`, `Projectile`|
| camera.py    | `Camera` — offset, clamp, apply                             |
| ui.py        | `HUD`, `DialogueBox`, title/game-over/victory screens       |

---

## Acceptance Criteria (DoD)

- [ ] Title screen renders; Enter starts the game
- [ ] Player moves with WASD; camera follows
- [ ] Melee attack damages enemies in arc; enemies flash + knockback
- [ ] Enemies chase player and attack on cooldown
- [ ] HP bar updates correctly; GAME_OVER triggers at 0 HP
- [ ] Potions picked up and used with E
- [ ] Gold auto-collected; displayed in HUD
- [ ] 3 portals in VILLAGE; correct unlock progression
- [ ] Each dungeon has correct enemy composition
- [ ] Each boss has its special mechanic
- [ ] Crystal Shard collected → return to VILLAGE
- [ ] All 3 shards → VICTORY screen
- [ ] Level-up triggers with stat increase message
- [ ] No crashes on normal play-through
