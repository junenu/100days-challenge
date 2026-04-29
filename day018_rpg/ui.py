import pygame

import config as C


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(C.FONT_NAME, 24)
        self.small = pygame.font.Font(C.FONT_NAME, 20)

    def bar(self, surf, x, y, w, h, value, maximum, color, label):
        pygame.draw.rect(surf, (0, 0, 0, 150), (x, y, w, h))
        fill = int(w * max(0, value) / max(1, maximum))
        pygame.draw.rect(surf, color, (x + 2, y + 2, max(0, fill - 4), h - 4))
        surf.blit(self.small.render(label, True, C.WHITE), (x + 6, y - 2))

    def draw(self, surf, player, state_name, message=None):
        panel = pygame.Surface((C.WIDTH, C.HUD_H), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 165))
        surf.blit(panel, (0, 0))
        self.bar(surf, 16, 10, 210, 16, player.hp, player.max_hp, C.RED, f"HP {player.hp}/{player.max_hp}")
        self.bar(surf, 250, 10, 210, 16, player.mp, player.max_mp, C.BLUE, f"MP {player.mp}/{player.max_mp}")
        line = f"Lv:{player.level}  XP:{player.xp}/{player.xp_next}  Gold:{player.gold}  Potions:{player.potions}"
        surf.blit(self.small.render(line, True, C.WHITE), (18, 32))
        surf.blit(self.small.render(C.STATE_LABELS[state_name], True, C.CYAN), (640, 10))
        for i in range(3):
            col = C.CYAN if i < player.shards else C.DARK_GRAY
            pygame.draw.circle(surf, col, (820 + i * 26, 38), 8)
        surf.blit(self.small.render("Shards", True, C.WHITE), (740, 28))
        if message:
            surf.blit(self.small.render(message, True, C.YELLOW), (500, 32))


class DialogueBox:
    def __init__(self):
        self.font = pygame.font.Font(C.FONT_NAME, 24)
        self.small = pygame.font.Font(C.FONT_NAME, 20)

    def draw(self, surf, speaker, lines):
        box = pygame.Surface((C.WIDTH - 60, 130), pygame.SRCALPHA)
        box.fill((0, 0, 0, 190))
        rect = box.get_rect(midbottom=(C.WIDTH // 2, C.HEIGHT - 18))
        surf.blit(box, rect.topleft)
        surf.blit(self.font.render(speaker, True, C.CYAN), (rect.x + 20, rect.y + 12))
        for i, line in enumerate(lines):
            surf.blit(self.small.render(line, True, C.WHITE), (rect.x + 20, rect.y + 48 + i * 24))
        surf.blit(self.small.render("Enter", True, C.GRAY), (rect.right - 80, rect.bottom - 30))


def draw_screen(surf, title, subtitle, accent):
    surf.fill(C.BG)
    font_big = pygame.font.Font(C.FONT_NAME, 72)
    font_mid = pygame.font.Font(C.FONT_NAME, 30)
    font_small = pygame.font.Font(C.FONT_NAME, 22)
    pygame.draw.circle(surf, (*accent, 0), (180, 160), 110)
    pygame.draw.rect(surf, (25, 28, 36), (90, 150, C.WIDTH - 180, 280), border_radius=24)
    surf.blit(font_big.render(title, True, accent), (140, 210))
    surf.blit(font_mid.render(subtitle, True, C.WHITE), (145, 300))
    surf.blit(font_small.render("Enter: confirm   Esc: title   R: restart", True, C.GRAY), (145, 360))


def draw_title(surf):
    draw_screen(surf, "Crystal Shards", "Recover the three shards and save the village.", C.CYAN)


def draw_game_over(surf):
    draw_screen(surf, "Game Over", "Your light faded. Press R to try again.", C.RED)


def draw_victory(surf):
    draw_screen(surf, "Victory", "All three shards shine again. The village is saved.", C.GOLD)
