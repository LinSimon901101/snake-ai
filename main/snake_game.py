import os
import sys
import random

import numpy as np

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # 隱藏Pygame的啟動提示訊息
import pygame
from pygame import mixer

class SnakeGame:
    def __init__(self, seed=0, board_size=12, silent_mode=True):
        self.board_size = board_size  # 棋盤大小
        self.grid_size = self.board_size ** 2  # 計算總格數
        self.cell_size = 40  # 每格的大小（像素）
        self.width = self.height = self.board_size * self.cell_size  # 計算畫面寬高

        self.border_size = 20  # 邊框大小
        self.display_width = self.width + 2 * self.border_size  # 計算顯示畫面寬度
        self.display_height = self.height + 2 * self.border_size + 40  # 計算顯示畫面高度

        self.silent_mode = silent_mode  # 是否靜音模式
        if not silent_mode:
            pygame.init()  # 初始化Pygame
            pygame.display.set_caption("Snake Game")  # 設置視窗標題
            self.screen = pygame.display.set_mode((self.display_width, self.display_height))  # 設置視窗大小
            self.font = pygame.font.Font(None, 36)  # 設置字體

            # 載入音效
            mixer.init()
            self.sound_eat = mixer.Sound("sound/eat.wav")  # 吃食物音效
            self.sound_game_over = mixer.Sound("sound/game_over.wav")  # 遊戲結束音效
            self.sound_victory = mixer.Sound("sound/victory.wav")  # 勝利音效
        else:
            self.screen = None
            self.font = None

        self.snake = None  # 蛇
        self.non_snake = None  # 非蛇格

        self.direction = None  # 蛇的方向
        self.score = 0  # 得分
        self.food = None  # 食物
        self.seed_value = seed  # 隨機種子

        random.seed(seed)  # 設定隨機種子
        
        self.reset()  # 初始化遊戲狀態

    def reset(self):
        # 初始化蛇，蛇身位置為中央三格
        self.snake = [(self.board_size // 2 + i, self.board_size // 2) for i in range(1, -2, -1)]
        # 初始化非蛇身格，將所有非蛇身格添加進集合中
        self.non_snake = set([(row, col) for row in range(self.board_size) for col in range(self.board_size) if (row, col) not in self.snake])
        self.direction = "DOWN"  # 蛇的初始方向是向下
        self.food = self._generate_food()  # 生成食物
        self.score = 0  # 重置分數

    def step(self, action):
        self._update_direction(action)  # 根據動作更新方向

        # 根據當前方向移動蛇
        row, col = self.snake[0]
        if self.direction == "UP":
            row -= 1
        elif self.direction == "DOWN":
            row += 1
        elif self.direction == "LEFT":
            col -= 1
        elif self.direction == "RIGHT":
            col += 1

        # 檢查蛇是否吃到食物
        if (row, col) == self.food:  # 如果蛇吃到食物，蛇不會移除尾巴，食物會被蛇佔據
            food_obtained = True
            self.score += 10  # 吃到食物後得分增加 10
            if not self.silent_mode:
                self.sound_eat.play()  # 播放吃食物音效
        else:
            food_obtained = False
            self.non_snake.add(self.snake.pop())  # 否則，去掉蛇尾，將尾巴格子加入非蛇格集合

        # 檢查蛇是否與自己或牆壁碰撞
        done = (
            (row, col) in self.snake  # 蛇是否撞到自己
            or row < 0  # 蛇是否超出上邊界
            or row >= self.board_size  # 蛇是否超出下邊界
            or col < 0  # 蛇是否超出左邊界
            or col >= self.board_size  # 蛇是否超出右邊界
        )

        if not done:
            self.snake.insert(0, (row, col))  # 若無碰撞，將蛇頭加到蛇身中
            self.non_snake.remove((row, col))  # 將新的蛇頭位置從非蛇格中刪除
        else:  # 若遊戲結束，播放遊戲結束音效
            if not self.silent_mode:
                if len(self.snake) < self.grid_size:
                    self.sound_game_over.play()  # 播放遊戲結束音效
                else:
                    self.sound_victory.play()  # 播放勝利音效

        # 當蛇吃到食物後生成新食物
        if food_obtained:
            self.food = self._generate_food()

        info = {
            "snake_size": len(self.snake),
            "snake_head_pos": np.array(self.snake[0]),
            "prev_snake_head_pos": np.array(self.snake[1]),
            "food_pos": np.array(self.food),
            "food_obtained": food_obtained
        }

        return done, info  # 返回遊戲是否結束和遊戲資訊

    # 更新蛇的移動方向
    def _update_direction(self, action):
        if action == 0:  # UP
            if self.direction != "DOWN":  # 防止蛇倒退
                self.direction = "UP"
        elif action == 1:  # LEFT
            if self.direction != "RIGHT":
                self.direction = "LEFT"
        elif action == 2:  # RIGHT
            if self.direction != "LEFT":
                self.direction = "RIGHT"
        elif action == 3:  # DOWN
            if self.direction != "UP":
                self.direction = "DOWN"
        # Python 3.10+ 支援 switch-case

    # 生成食物
    def _generate_food(self):
        if len(self.non_snake) > 0:
            food = random.sample(self.non_snake, 1)[0]  # 隨機選擇非蛇身的位置作為食物
        else:  # 若蛇已佔滿整個棋盤，則不生成食物，設為(0,0)
            food = (0, 0)
        return food
    
    # 顯示分數
    def draw_score(self):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (self.border_size, self.height + 2 * self.border_size))
    
    # 顯示歡迎畫面
    def draw_welcome_screen(self):
        title_text = self.font.render("SNAKE GAME", True, (255, 255, 255))
        start_button_text = "START"

        self.screen.fill((0, 0, 0))  # 清空畫面
        self.screen.blit(title_text, (self.display_width // 2 - title_text.get_width() // 2, self.display_height // 4))  # 顯示遊戲標題
        self.draw_button_text(start_button_text, (self.display_width // 2, self.display_height // 2))  # 顯示開始按鈕
        pygame.display.flip()  # 更新顯示

    # 顯示遊戲結束畫面
    def draw_game_over_screen(self):
        game_over_text = self.font.render("GAME OVER", True, (255, 255, 255))
        final_score_text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
        retry_button_text = "RETRY"

        self.screen.fill((0, 0, 0))  # 清空畫面
        self.screen.blit(game_over_text, (self.display_width // 2 - game_over_text.get_width() // 2, self.display_height // 4))  # 顯示遊戲結束文字
        self.screen.blit(final_score_text, (self.display_width // 2 - final_score_text.get_width() // 2, self.display_height // 4 + final_score_text.get_height() + 10))  # 顯示最終得分
        self.draw_button_text(retry_button_text, (self.display_width // 2, self.display_height // 2))  # 顯示重試按鈕
        pygame.display.flip()  # 更新顯示

    # 繪製按鈕文字
    def draw_button_text(self, button_text_str, pos, hover_color=(255, 255, 255), normal_color=(100, 100, 100)):
        mouse_pos = pygame.mouse.get_pos()  # 獲取滑鼠位置
        button_text = self.font.render(button_text_str, True, normal_color)  # 渲染按鈕文字
        text_rect = button_text.get_rect(center=pos)

        if text_rect.collidepoint(mouse_pos):  # 檢查滑鼠是否在按鈕上
            colored_text = self.font.render(button_text_str, True, hover_color)  # 如果滑鼠懸停，改變顏色
        else:
            colored_text = self.font.render(button_text_str, True, normal_color)

        self.screen.blit(colored_text, text_rect)  # 顯示按鈕文字
    
    # 顯示倒數計時
    def draw_countdown(self, number):
        countdown_text = self.font.render(str(number), True, (255, 255, 255))
        self.screen.blit(countdown_text, (self.display_width // 2 - countdown_text.get_width() // 2, self.display_height // 2 - countdown_text.get_height() // 2))
        pygame.display.flip()

    # 檢查滑鼠是否點擊在按鈕上
    def is_mouse_on_button(self, button_text):
        mouse_pos = pygame.mouse.get_pos()
        text_rect = button_text.get_rect(
            center=(
                self.display_width // 2,
                self.display_height // 2,
            )
        )
        return text_rect.collidepoint(mouse_pos)

    # 繪製遊戲畫面
    def render(self):
        self.screen.fill((0, 0, 0))  # 清空畫面

        # 繪製邊框
        pygame.draw.rect(self.screen, (255, 255, 255), (self.border_size - 2, self.border_size - 2, self.width + 4, self.height + 4), 2)

        # 繪製蛇
        self.draw_snake()
        
        # 繪製食物
        if len(self.snake) < self.grid_size:  # 如果蛇還未佔滿棋盤，繪製食物
            r, c = self.food
            pygame.draw.rect(self.screen, (255, 0, 0), (c * self.cell_size + self.border_size, r * self.cell_size + self.border_size, self.cell_size, self.cell_size))

        # 顯示分數
        self.draw_score()

        pygame.display.flip()  # 更新顯示

        for event in pygame.event.get():  # 處理事件
            if event.type == pygame.QUIT:
                pygame.quit()  # 關閉遊戲
                sys.exit()

    # 繪製蛇身
    def draw_snake(self):
        # 繪製蛇頭
        head_r, head_c = self.snake[0]
        head_x = head_c * self.cell_size + self.border_size
        head_y = head_r * self.cell_size + self.border_size

        # 繪製蛇頭（藍色）
        pygame.draw.polygon(self.screen, (100, 100, 255), [
            (head_x + self.cell_size // 2, head_y),
            (head_x + self.cell_size, head_y + self.cell_size // 2),
            (head_x + self.cell_size // 2, head_y + self.cell_size),
            (head_x, head_y + self.cell_size // 2)
        ])

        eye_size = 3
        eye_offset = self.cell_size // 4
        pygame.draw.circle(self.screen, (255, 255, 255), (head_x + eye_offset, head_y + eye_offset), eye_size)  # 左眼
        pygame.draw.circle(self.screen, (255, 255, 255), (head_x + self.cell_size - eye_offset, head_y + eye_offset), eye_size)  # 右眼

        # 繪製蛇身（顏色漸層）
        color_list = np.linspace(255, 100, len(self.snake), dtype=np.uint8)
        i = 1
        for r, c in self.snake[1:]:
            body_x = c * self.cell_size + self.border_size
            body_y = r * self.cell_size + self.border_size
            body_width = self.cell_size
            body_height = self.cell_size
            body_radius = 5
            pygame.draw.rect(self.screen, (0, color_list[i], 0),
                             (body_x, body_y, body_width, body_height), border_radius=body_radius)
            i += 1
        pygame.draw.rect(self.screen, (255, 100, 100),
                             (body_x, body_y, body_width, body_height), border_radius=body_radius)
if __name__ == "__main__":
    import time

    seed = random.randint(0, 1e9)
    game = SnakeGame(seed=seed, silent_mode=False)
    pygame.init()
    game.screen = pygame.display.set_mode((game.display_width, game.display_height))
    pygame.display.set_caption("Snake Game")
    game.font = pygame.font.Font(None, 36)
    

    game_state = "welcome"

    # Two hidden button for start and retry click detection
    start_button = game.font.render("START", True, (0, 0, 0))
    retry_button = game.font.render("RETRY", True, (0, 0, 0))

    update_interval = 0.15
    start_time = time.time()
    action = -1

    while True:
        
        for event in pygame.event.get():

            if game_state == "running":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        action = 0
                    elif event.key == pygame.K_DOWN:
                        action = 3
                    elif event.key == pygame.K_LEFT:
                        action = 1
                    elif event.key == pygame.K_RIGHT:
                        action = 2

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_state == "welcome" and event.type == pygame.MOUSEBUTTONDOWN:
                if game.is_mouse_on_button(start_button):
                    for i in range(3, 0, -1):
                        game.screen.fill((0, 0, 0))
                        game.draw_countdown(i)
                        game.sound_eat.play()
                        pygame.time.wait(1000)
                    action = -1  # Reset action variable when starting a new game
                    game_state = "running"

            if game_state == "game_over" and event.type == pygame.MOUSEBUTTONDOWN:
                if game.is_mouse_on_button(retry_button):
                    for i in range(3, 0, -1):
                        game.screen.fill((0, 0, 0))
                        game.draw_countdown(i)
                        game.sound_eat.play()
                        pygame.time.wait(1000)
                    game.reset()
                    action = -1  # Reset action variable when starting a new game
                    game_state = "running"
        
        if game_state == "welcome":
            game.draw_welcome_screen()

        if game_state == "game_over":
            game.draw_game_over_screen()

        if game_state == "running":
            if time.time() - start_time >= update_interval:
                done, _ = game.step(action)
                game.render()
                start_time = time.time()

                if done:
                    game_state = "game_over"
        
        pygame.time.wait(1)
