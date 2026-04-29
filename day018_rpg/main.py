from enum import Enum, auto

import pygame

import config as C
from camera import Camera
from entities import Enemy, Item, Player
from ui import HUD, DialogueBox, draw_game_over, draw_title, draw_victory
from world import TileMap, make_area


class GameState(Enum):
    TITLE = auto()
    VILLAGE = auto()
    DUNGEON_1 = auto()
    DUNGEON_2 = auto()
    DUNGEON_3 = auto()
    GAME_OVER = auto()
    VICTORY = auto()


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(C.TITLE)
        self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.dialogue_box = DialogueBox()
        self.camera = Camera()
        self.state = GameState.TITLE
        self.tick = 0
        self.notice = ""
        self.notice_timer = 0
        self.dialogue = None
        self.reset_run()

    def reset_run(self):
        self.player = Player()
        self.enemies = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.area = None
        self.tilemap = None

    def enter_area(self, state):
        self.state = state
        self.dialogue = None
        self.enemies.empty()
        self.items.empty()
        self.projectiles.empty()
        area = make_area(state.name, self.player.shards)
        self.area = area
        self.tilemap = TileMap(area.tiles)
        self.player.reset_pos(area.spawn_point)
        for tx, ty, kind in area.spawns:
            self.enemies.add(Enemy(kind, (tx + 0.5) * C.TILE, (ty + 0.5) * C.TILE))
        if area.boss:
            boss = Enemy(area.boss["kind"], *area.boss["pos"], boss=True)
            boss.shard_id = area.boss["shard"]
            self.enemies.add(boss)
        self.camera.update(self.player)
        self.notice_text(C.STATE_LABELS[state.name])

    def notice_text(self, text, duration=2.0):
        self.notice = text
        self.notice_timer = duration

    def restart_to_title(self):
        self.reset_run()
        self.state = GameState.TITLE
        self.notice = ""
        self.notice_timer = 0
        self.dialogue = None

    def try_portal(self):
        for portal in self.area.portals:
            if portal["rect"].colliderect(self.player.rect):
                if portal["active"]:
                    self.enter_area(GameState[portal["target"]])
                return

    def handle_pickups(self):
        for item in list(self.items):
            if self.player.pos.distance_to(item.pos) > self.player.radius + item.radius + 6:
                continue
            if item.kind == "gold":
                self.player.gold += item.value
                item.kill()
            elif item.kind == "potion" and self.player.potions < C.MAX_POTIONS:
                self.player.potions += 1
                self.notice_text("Potion +1", 1.0)
                item.kill()
            elif item.kind == "shard":
                self.player.shards = max(self.player.shards, item.value)
                item.kill()
                if item.value >= 3:
                    self.state = GameState.VICTORY
                else:
                    self.enter_area(GameState.VILLAGE)
                    self.notice_text(f"Crystal Shard {self.player.shards}/3", 2.5)
                return

    def enemy_death(self, enemy):
        if hasattr(enemy, "shard_id"):
            enemy.drop(self.items, enemy.shard_id)
        else:
            enemy.drop(self.items)
        leveled = self.player.reward(enemy.xp_value, enemy.gold_value)
        if leveled:
            self.notice_text(f"Level Up! Lv {self.player.level}", 2.5)

    def update_play(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys, self.tilemap)
        for enemy in list(self.enemies):
            if enemy.dead:
                self.enemy_death(enemy)
                enemy.kill()
                continue
            result = enemy.update(dt, self.player, self.tilemap)
            for kind, x, y in result["spawns"]:
                self.enemies.add(Enemy(kind, x, y))
            for shot in result["shots"]:
                self.projectiles.add(shot)
            if enemy.dead:
                self.enemy_death(enemy)
                enemy.kill()
        for item in list(self.items):
            item.update(dt)
        for proj in list(self.projectiles):
            proj.update(dt, self.tilemap, self.player)
            if proj.dead:
                proj.kill()
        self.handle_pickups()
        if self.state == GameState.VILLAGE:
            self.try_portal()
        self.camera.update(self.player)
        if self.notice_timer > 0:
            self.notice_timer = max(0, self.notice_timer - dt)
            if self.notice_timer == 0:
                self.notice = ""
        if self.player.hp <= 0:
            self.state = GameState.GAME_OVER

    def draw_npc(self):
        if not self.area.npc_pos:
            return
        p = self.camera.to_screen(pygame.Vector2(self.area.npc_pos))
        shade = pygame.Surface((34, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(shade, (0, 0, 0, 70), shade.get_rect())
        self.screen.blit(shade, (p.x - 17, p.y + 8))
        pygame.draw.rect(self.screen, (60, 110, 210), (p.x - 10, p.y - 4, 20, 24))
        pygame.draw.circle(self.screen, (120, 170, 255), (int(p.x), int(p.y - 10)), 12)

    def draw_labels(self):
        font = pygame.font.Font(C.FONT_NAME, 18)
        for portal in self.area.portals:
            col = C.CYAN if portal["active"] else C.GRAY
            pos = self.camera.apply(portal["rect"]).midtop
            label = font.render(portal["label"], True, col)
            self.screen.blit(label, label.get_rect(midbottom=(pos[0], pos[1] - 4)))
        if self.area.npc_pos and self.player.pos.distance_to(pygame.Vector2(self.area.npc_pos)) < 60:
            tip = font.render("Enter: Talk", True, C.WHITE)
            p = self.camera.to_screen(pygame.Vector2(self.area.npc_pos))
            self.screen.blit(tip, tip.get_rect(midbottom=(p.x, p.y - 26)))

    def render_play(self):
        self.screen.fill(C.BG)
        self.tilemap.render(self.screen, self.camera, self.tick)
        self.draw_npc()
        for item in self.items:
            item.draw(self.screen, self.camera)
        for proj in self.projectiles:
            proj.draw(self.screen, self.camera)
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera, self.tick)
        self.player.draw(self.screen, self.camera)
        self.draw_labels()
        self.hud.draw(self.screen, self.player, self.state.name, self.notice)
        if self.dialogue:
            self.dialogue_box.draw(self.screen, self.dialogue[0], self.dialogue[1])

    def handle_keydown(self, key):
        if self.state == GameState.TITLE:
            if key == pygame.K_RETURN:
                self.enter_area(GameState.VILLAGE)
            return
        if key == pygame.K_ESCAPE:
            self.state = GameState.TITLE
            return
        if self.state in {GameState.GAME_OVER, GameState.VICTORY}:
            if key in (pygame.K_r, pygame.K_RETURN):
                self.restart_to_title()
            return
        if self.dialogue:
            if key == pygame.K_RETURN:
                self.dialogue = None
            return
        if key == pygame.K_SPACE:
            self.player.melee_attack(self.enemies)
        elif key == pygame.K_e:
            if self.player.use_potion():
                self.notice_text("Potion used", 1.0)
        elif key == pygame.K_RETURN:
            if self.state == GameState.VILLAGE and self.area.npc_pos and self.player.pos.distance_to(pygame.Vector2(self.area.npc_pos)) < 70:
                self.dialogue = ("Village Elder", C.NPC_TEXT)
            else:
                self.try_portal()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(C.FPS) / 1000.0
            self.tick += dt
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)
            if self.state in {GameState.VILLAGE, GameState.DUNGEON_1, GameState.DUNGEON_2, GameState.DUNGEON_3} and not self.dialogue:
                self.update_play(dt)
            if self.state == GameState.TITLE:
                draw_title(self.screen)
            elif self.state == GameState.GAME_OVER:
                draw_game_over(self.screen)
            elif self.state == GameState.VICTORY:
                draw_victory(self.screen)
            else:
                self.render_play()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
