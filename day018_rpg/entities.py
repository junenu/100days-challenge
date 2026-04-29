import math
import random

import pygame

import config as C


def damage_roll(attacker_atk, defender_def):
    return max(1, attacker_atk + random.randint(-2, 3) - defender_def)


def shadow(surf, camera, pos, radius):
    p = camera.to_screen(pos)
    rect = pygame.Rect(0, 0, radius * 2, radius)
    rect.center = (int(p.x), int(p.y + radius * 0.8))
    layer = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.ellipse(layer, (0, 0, 0, 70), layer.get_rect())
    surf.blit(layer, rect.topleft)


class Entity:
    def __init__(self, x, y, radius, color, hp, atk, defense, spd):
        self.pos = pygame.Vector2(x, y)
        self.radius = radius
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.atk = atk
        self.defense = defense
        self.spd = spd
        self.flash = 0
        self.dead = False

    @property
    def rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    def move(self, dx, dy, tilemap):
        if dx:
            nx = self.pos.x + dx
            if tilemap.walkable(nx, self.pos.y, self.radius - 3):
                self.pos.x = nx
        if dy:
            ny = self.pos.y + dy
            if tilemap.walkable(self.pos.x, ny, self.radius - 3):
                self.pos.y = ny

    def take_hit(self, atk, source=None):
        dmg = damage_roll(atk, self.defense)
        self.hp -= dmg
        self.flash = 0.13
        if source:
            v = self.pos - source
            if v.length_squared() > 0:
                self.pos += v.normalize() * C.KNOCKBACK
        if self.hp <= 0:
            self.dead = True
        return dmg


class Player(Entity):
    def __init__(self):
        super().__init__(*C.PLAYER_START, C.PLAYER_RADIUS, C.YELLOW, C.PLAYER_BASE["hp"], C.PLAYER_BASE["atk"], C.PLAYER_BASE["def"], C.PLAYER_BASE["spd"])
        self.max_hp = C.PLAYER_BASE["max_hp"]
        self.mp = C.PLAYER_BASE["mp"]
        self.max_mp = C.PLAYER_BASE["max_mp"]
        self.level = C.PLAYER_BASE["level"]
        self.xp = C.PLAYER_BASE["xp"]
        self.xp_next = C.PLAYER_BASE["xp_next"]
        self.gold = C.PLAYER_BASE["gold"]
        self.potions = C.PLAYER_BASE["potions"]
        self.shards = 0
        self.attack_cd = 0
        self.attack_flash = 0
        self.invuln = 0
        self.facing = pygame.Vector2(0, 1)

    def reset_pos(self, pos):
        self.pos.update(pos)

    def update(self, dt, keys, tilemap):
        move = pygame.Vector2(keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_s] - keys[pygame.K_w])
        if move.length_squared() > 0:
            self.facing = move.normalize()
            move = self.facing * self.spd * dt
            self.move(move.x, 0, tilemap)
            self.move(0, move.y, tilemap)
        self.flash = max(0, self.flash - dt)
        self.attack_cd = max(0, self.attack_cd - dt)
        self.attack_flash = max(0, self.attack_flash - dt)
        self.invuln = max(0, self.invuln - dt)

    def melee_attack(self, enemies):
        if self.attack_cd > 0:
            return []
        self.attack_cd = C.ATTACK_COOLDOWN
        self.attack_flash = C.ATTACK_FLASH
        hits = []
        for enemy in enemies:
            if enemy.dead:
                continue
            v = enemy.pos - self.pos
            if v.length() <= C.ATTACK_RANGE + enemy.radius:
                ang = abs(self.facing.angle_to(v)) if v.length_squared() else 0
                if ang <= 60:
                    hits.append((enemy, enemy.take_hit(self.atk, self.pos)))
        return hits

    def take_enemy_hit(self, enemy):
        if self.invuln > 0:
            return 0
        self.invuln = C.INVULN_TIME
        return self.take_hit(enemy.atk, enemy.pos)

    def use_potion(self):
        if self.potions < 1 or self.hp >= self.max_hp:
            return False
        self.potions -= 1
        self.hp = min(self.max_hp, self.hp + C.POTION_HEAL)
        return True

    def reward(self, xp, gold):
        self.xp += xp
        self.gold += gold
        return self.level_up()

    def level_up(self):
        if self.xp < self.xp_next:
            return False
        while self.xp >= self.xp_next:
            self.xp -= self.xp_next
            self.level += 1
            self.xp_next = int(self.xp_next * 1.6)
            self.max_hp += 10
            self.hp = self.max_hp
            self.max_mp += 5
            self.mp = self.max_mp
            self.atk += 3
            self.defense += 1
        return True

    def draw(self, surf, camera):
        shadow(surf, camera, self.pos, self.radius)
        p = camera.to_screen(self.pos)
        color = C.WHITE if self.flash > 0 else self.color
        pygame.draw.circle(surf, color, (int(p.x), int(p.y)), self.radius)
        tip = p + self.facing * 18
        left = p + self.facing.rotate(135) * 8
        right = p + self.facing.rotate(-135) * 8
        pygame.draw.polygon(surf, C.WHITE, [(tip.x, tip.y), (left.x, left.y), (right.x, right.y)])
        if self.attack_flash > 0:
            rect = pygame.Rect(0, 0, C.ATTACK_RANGE * 2, C.ATTACK_RANGE * 2)
            rect.center = (int(p.x + self.facing.x * 28), int(p.y + self.facing.y * 28))
            start = math.radians(-60 - self.facing.angle_to(pygame.Vector2(1, 0)))
            pygame.draw.arc(surf, C.WHITE, rect, start, start + C.ATTACK_ARC, 4)


class Enemy(pygame.sprite.Sprite, Entity):
    def __init__(self, kind, x, y, boss=False):
        pygame.sprite.Sprite.__init__(self)
        s = C.ENEMY_STATS[kind]
        Entity.__init__(self, x, y, s["radius"], s["color"], s["hp"], s["atk"], s["def"], s["spd"])
        self.kind = kind
        self.boss = boss
        self.xp_value = s["xp"]
        self.gold_value = s["gold"]
        self.aggro = s["aggro"]
        self.attack_range = s["range"]
        self.cooldown = s["cd"]
        self.attack_timer = random.random()
        self.special_timer = 4.0
        self.phase_marks = set()
        self.split_done = False

    def update(self, dt, player, tilemap):
        self.flash = max(0, self.flash - dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.special_timer = max(0, self.special_timer - dt)
        result = {"spawns": [], "shots": [], "damage": 0}
        to_player = player.pos - self.pos
        dist = to_player.length() if to_player.length_squared() else 0
        if self.kind == "giant_slime" and not self.split_done and self.hp <= self.max_hp / 2:
            self.split_done = True
            result["spawns"] = [("slime", self.pos.x - 28, self.pos.y), ("slime", self.pos.x + 28, self.pos.y)]
        if self.kind == "dark_wizard":
            for threshold in (0.66, 0.33):
                if self.hp <= self.max_hp * threshold and threshold not in self.phase_marks:
                    self.phase_marks.add(threshold)
                    result["spawns"] += [("dark_orb", self.pos.x - 60, self.pos.y + 40), ("dark_orb", self.pos.x + 60, self.pos.y + 40)]
        if dist and dist < self.aggro:
            direction = to_player.normalize()
            speed = self.spd
            if self.kind == "bone_knight" and self.special_timer <= 0:
                self.special_timer = 4.0
                speed *= 2.4
            if dist > self.attack_range * 0.85 or self.kind in {"dark_wizard", "dark_orb"}:
                step = direction * speed * dt
                self.move(step.x, 0, tilemap)
                self.move(0, step.y, tilemap)
            if self.attack_timer <= 0 and dist <= self.attack_range + player.radius:
                self.attack_timer = self.cooldown
                if self.kind in {"dark_orb", "dark_wizard"}:
                    result["shots"].append(Projectile(self.pos, direction, self.atk, hostile=True))
                else:
                    result["damage"] = player.take_enemy_hit(self)
        return result

    def drop(self, items, shard=None):
        if shard:
            items.add(Item(self.pos.x, self.pos.y, "shard", shard))
            return
        if random.random() < C.DROP_GOLD_RATE:
            items.add(Item(self.pos.x, self.pos.y, "gold", random.randint(3, 12)))
        if random.random() < C.DROP_POTION_RATE:
            items.add(Item(self.pos.x + 10, self.pos.y - 8, "potion", 1))

    def draw(self, surf, camera, tick):
        shadow(surf, camera, self.pos, self.radius)
        p = camera.to_screen(self.pos)
        color = C.WHITE if self.flash > 0 else self.color
        if self.kind in {"slime", "giant_slime"}:
            pygame.draw.circle(surf, color, (int(p.x), int(p.y)), self.radius)
            for ex in (-6, 6):
                pygame.draw.ellipse(surf, C.BLACK, (p.x + ex - 3, p.y - 4, 6, 10))
        elif self.kind == "goblin":
            pygame.draw.circle(surf, color, (int(p.x), int(p.y)), self.radius)
            pygame.draw.polygon(surf, color, [(p.x - 10, p.y - 6), (p.x - 18, p.y - 12), (p.x - 8, p.y - 14)])
            pygame.draw.polygon(surf, color, [(p.x + 10, p.y - 6), (p.x + 18, p.y - 12), (p.x + 8, p.y - 14)])
        elif self.kind == "skeleton":
            pygame.draw.circle(surf, color, (int(p.x), int(p.y - 6)), 10)
            pygame.draw.line(surf, color, (p.x - 10, p.y + 10), (p.x + 10, p.y - 10), 3)
            pygame.draw.line(surf, color, (p.x - 10, p.y - 10), (p.x + 10, p.y + 10), 3)
        elif self.kind == "bone_knight":
            pygame.draw.rect(surf, color, (p.x - 16, p.y - 8, 32, 28))
            pygame.draw.circle(surf, color, (int(p.x), int(p.y - 14)), 12)
        elif self.kind == "dark_wizard":
            pygame.draw.rect(surf, color, (p.x - 14, p.y - 4, 28, 30))
            pygame.draw.circle(surf, (180, 80, 210), (int(p.x), int(p.y - 12)), 10)
            pygame.draw.polygon(surf, color, [(p.x, p.y - 34), (p.x - 16, p.y - 8), (p.x + 16, p.y - 8)])
        else:
            pulse = self.radius + int(2 * math.sin(tick * 6))
            pygame.draw.circle(surf, (80, 40, 150), (int(p.x), int(p.y)), pulse, 2)
            pygame.draw.circle(surf, color, (int(p.x), int(p.y)), self.radius)
        if self.boss:
            bar = pygame.Rect(p.x - 26, p.y - self.radius - 14, 52, 6)
            pygame.draw.rect(surf, C.DARK_GRAY, bar)
            pygame.draw.rect(surf, C.RED, (bar.x, bar.y, int(bar.w * max(0, self.hp) / self.max_hp), bar.h))


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, kind, value):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.kind = kind
        self.value = value
        self.radius = 12 if kind == "shard" else 10
        self.bob = random.random() * math.pi

    def update(self, dt):
        self.bob += dt * 4

    def draw(self, surf, camera):
        shadow(surf, camera, self.pos, self.radius)
        p = camera.to_screen(self.pos + pygame.Vector2(0, math.sin(self.bob) * 3))
        if self.kind == "gold":
            pygame.draw.polygon(surf, C.GOLD, [(p.x, p.y - 8), (p.x + 8, p.y), (p.x, p.y + 8), (p.x - 8, p.y)])
        elif self.kind == "potion":
            pygame.draw.circle(surf, C.RED, (int(p.x), int(p.y)), 8)
            pygame.draw.rect(surf, C.WHITE, (p.x - 3, p.y - 12, 6, 5))
        else:
            pts = [(0, -12), (8, 0), (0, 12), (-8, 0)]
            pts = [(p.x + x, p.y + y) for x, y in pts]
            pygame.draw.polygon(surf, C.CYAN, pts)
            pygame.draw.polygon(surf, C.WHITE, pts, 2)


class Projectile(pygame.sprite.Sprite):
    def __init__(self, pos, direction, atk, hostile=False):
        super().__init__()
        self.pos = pygame.Vector2(pos)
        self.vel = pygame.Vector2(direction) * C.PROJECTILE_SPEED
        self.atk = atk
        self.hostile = hostile
        self.radius = C.PROJECTILE_RADIUS
        self.life = 2.0
        self.dead = False

    def update(self, dt, tilemap, player):
        self.life -= dt
        self.pos += self.vel * dt
        if self.life <= 0 or not tilemap.walkable(self.pos.x, self.pos.y, self.radius):
            self.dead = True
        if self.hostile and self.pos.distance_to(player.pos) <= self.radius + player.radius and player.invuln <= 0:
            player.take_enemy_hit(type("Attack", (), {"atk": self.atk, "pos": self.pos})())
            self.dead = True

    def draw(self, surf, camera):
        p = camera.to_screen(self.pos)
        pygame.draw.circle(surf, (180, 80, 240), (int(p.x), int(p.y)), self.radius + 2)
        pygame.draw.circle(surf, C.WHITE, (int(p.x), int(p.y)), self.radius)
