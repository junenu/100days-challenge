import random
from dataclasses import dataclass, field


class Entity:
    def __init__(self, x: int, y: int, char: str, name: str,
                 hp: int, attack: int, defense: int, xp_value: int = 0):
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.hp = hp
        self.max_hp = hp
        self.attack = attack
        self.defense = defense
        self.xp_value = xp_value

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, dmg: int) -> int:
        actual = max(1, dmg - self.defense)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before


class Player(Entity):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '@', 'Hero', 30, 5, 2)
        self.level = 1
        self.xp = 0
        self.xp_next = 20
        self.potions = 3
        self.gold = 0
        self.floor = 1
        self.kills = 0

    def gain_xp(self, amount: int) -> bool:
        self.xp += amount
        if self.xp >= self.xp_next:
            self._level_up()
            return True
        return False

    def _level_up(self):
        self.level += 1
        self.xp -= self.xp_next
        self.xp_next = int(self.xp_next * 1.6)
        self.max_hp += 8
        self.hp = self.max_hp
        self.attack += 2
        self.defense += 1


class Monster(Entity):
    pass


_MONSTER_TYPES = [
    ('g', 'Goblin',  6,  3, 0,  4),
    ('o', 'Orc',    14,  5, 1,  9),
    ('t', 'Troll',  22,  8, 2, 16),
    ('D', 'Dragon', 40, 12, 4, 32),
]


def spawn_monsters(rooms, floor: int) -> list[Monster]:
    monsters: list[Monster] = []
    n_types = min(floor, len(_MONSTER_TYPES))
    available = _MONSTER_TYPES[:n_types]
    weights = list(range(n_types, 0, -1))

    for room in rooms[1:]:
        count = random.randint(0, 2 + floor // 2)
        for _ in range(count):
            x, y = room.random_point()
            if any(m.x == x and m.y == y for m in monsters):
                continue
            char, name, hp, atk, dfn, xp = random.choices(available, weights=weights)[0]
            scale = 1.0 + (floor - 1) * 0.25
            monsters.append(Monster(
                x, y, char, name,
                int(hp * scale), int(atk * scale), dfn, int(xp * scale)
            ))

    return monsters


class Item:
    def __init__(self, x: int, y: int, char: str, name: str):
        self.x = x
        self.y = y
        self.char = char
        self.name = name

    def pick_up(self, player: Player) -> str:
        raise NotImplementedError


class Potion(Item):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, '!', 'Health Potion')

    def pick_up(self, player: Player) -> str:
        player.potions += 1
        return f"You pick up a {self.name}. ({player.potions} total)"


class Gold(Item):
    def __init__(self, x: int, y: int):
        self._amount = random.randint(5, 30)
        super().__init__(x, y, '$', f'Gold ({self._amount})')

    def pick_up(self, player: Player) -> str:
        player.gold += self._amount
        return f"You pick up {self._amount} gold! (total: {player.gold})"


def spawn_items(rooms, floor: int) -> list[Item]:
    items: list[Item] = []
    for room in rooms:
        if random.random() < 0.55:
            x, y = room.random_point()
            if random.random() < 0.55:
                items.append(Potion(x, y))
            else:
                items.append(Gold(x, y))
    return items
