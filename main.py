import arcade
import random
from data.battle_engine import BattleEngine, Pokemon, ACHIEVEMENTS
from data.moves import MOVES

# --- 화면 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "폭주! 레시라무"

# --- 상태(State) 상수 ---
STATE_P1_ACTION = 1
STATE_P1_MOVE = 2
STATE_P1_PARTY = 3
STATE_P2_ACTION = 4
STATE_P2_MOVE = 5
STATE_P2_PARTY = 6
STATE_BATTLE_PHASE = 7
STATE_GAME_OVER = 8
STATE_FAINT_SWITCH = 9

class StoryView(arcade.View):
    def __init__(self):
        super().__init__()
        self.time_elapsed = 0.0
        self.phase = 0
        
        # 사운드 로드
        self.sound_earth = arcade.Sound("audio/Earth1.ogg")
        self.sound_reshiram = arcade.Sound("audio/RESHIRAM.ogg")
        self.sound_zekrom = arcade.Sound("audio/ZEKROM.ogg")
        
        self.played_earth1 = False
        self.played_earth2 = False
        self.played_reshiram = False
        self.played_zekrom = False
        
        # 텍스트 객체 초기화
        t1 = "플라스마단의 숨겨진 연구소... 그곳에서 최악의 사태가 발생했다.\n\n강제적인 실험의 부작용으로, 이성을 잃고 폭주하는 레시라무."
        self.story_text1 = arcade.Text(t1, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                       arcade.color.WHITE, font_size=18, anchor_x="center", anchor_y="center", align="center", multiline=True, width=700)
                                       
        t2 = "하나지방이 푸른 화염에 집어삼켜지려는 찰나.."
        self.story_text2 = arcade.Text(t2, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                       arcade.color.WHITE, font_size=18, anchor_x="center", anchor_y="center", align="center")
                                       
        t3 = "푸른 번개와 함께 제크로무가 나타나 \n\n당신에게 힘을 빌려달라 부탁한다.\n\n 폭주하는 레시라무를 잠재우고 하나지방을 구하라!"
        self.story_text3 = arcade.Text(t3, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                                       arcade.color.WHITE, font_size=18, anchor_x="center", anchor_y="center", align="center", multiline=True, width=700)
                                       
        self.skip_text = arcade.Text("S 키를 눌러 스킵", SCREEN_WIDTH - 20, SCREEN_HEIGHT - 30,
                                     arcade.color.GRAY, font_size=14, anchor_x="right")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_update(self, delta_time):
        self.time_elapsed += delta_time
        
        # 사운드 재생 제어
        if self.time_elapsed >= 3.0 and not self.played_earth1:
            self.sound_earth.play()
            self.played_earth1 = True
        
        if self.time_elapsed >= 4.0 and not self.played_earth2:
            self.sound_earth.play()
            self.played_earth2 = True
            
        if self.time_elapsed >= 5.0 and not self.played_reshiram:
            self.sound_reshiram.play()
            self.played_reshiram = True
            
        if self.time_elapsed >= 10.0 and not self.played_zekrom:
            self.sound_zekrom.play()
            self.played_zekrom = True
            
        # 페이즈 제어 및 자동 화면 전환 (페이즈 변수 대신 직접 시간으로 렌더링)
        if self.time_elapsed >= 15.0:
            self.window.show_view(TitleView())

    def on_draw(self):
        self.clear()
        
        # 1. 붉은 점멸 (5.0초 ~ 5.5초)
        if 5.0 <= self.time_elapsed <= 5.5:
            arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT), arcade.color.DARK_RED)
            
        # 2. 푸른 페이드인 (10.0초 이후 2초간 서서히)
        if self.time_elapsed >= 10.0:
            progress = min(1.0, (self.time_elapsed - 10.0) / 2.0)
            alpha = int(255 * progress)
            # 투명도를 지원하는 파란색 (R, G, B, A)
            blue_color = (0, 0, 139, alpha)
            arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, SCREEN_WIDTH, SCREEN_HEIGHT), blue_color)
        
        # 스토리 텍스트 렌더링
        if self.time_elapsed < 5.0:
            self.story_text1.draw()
        elif 5.5 < self.time_elapsed < 10.0: # 붉은 점멸이 끝난 직후부터 텍스트 표시
            self.story_text2.draw()
        elif self.time_elapsed >= 10.0:
            self.story_text3.draw()
            
        self.skip_text.draw()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.S:
            self.window.show_view(TitleView())

class TitleView(arcade.View):
    def __init__(self):
        super().__init__()
        # 타이틀 배경 이미지 로드
        self.background = arcade.load_texture("ui/title.png")
        # 게임 시작 시 재생할 사운드
        self.sound_start = arcade.Sound("audio/RESHIRAM.ogg")
        
        self.menu_index = 0
        self.menu_options = ["1. 게임 시작", "2. 업적", "3. 게임 종료"]
        self.option_texts = [arcade.Text("", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - (i * 60),
                                        arcade.color.WHITE, font_size=24, anchor_x="center")
                             for i in range(len(self.menu_options))]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        
        # 배경 이미지 렌더링 (800x680)
        # 상단을 화면에 맞추고 아래 80픽셀을 잘라내기 위해 중심 y를 260으로 설정
        # (중심 260 + 절반 높이 340 = 상단 600)
        arcade.draw_texture_rect(self.background, arcade.XYWH(SCREEN_WIDTH / 2, 260, 800, 680))
        
        for i, option in enumerate(self.menu_options):
            y_pos = SCREEN_HEIGHT / 2 - (i * 60)
            
            # 투명도가 적용된 회색 사각형 (RGBA: 60, 60, 60, 150)
            bg_color = (60, 60, 60, 150)
            arcade.draw_rect_filled(arcade.XYWH(SCREEN_WIDTH / 2, y_pos + 12, 250, 45), bg_color)
            
            # 선택된 메뉴는 테두리를 그려서 강조
            if i == self.menu_index:
                arcade.draw_rect_outline(arcade.XYWH(SCREEN_WIDTH / 2, y_pos + 12, 250, 45), arcade.color.YELLOW, 2)
            
            t = self.option_texts[i]
            t.color = arcade.color.YELLOW if i == self.menu_index else arcade.color.WHITE
            prefix = "▶ " if i == self.menu_index else "  "
            t.text = f"{prefix}{option}"
            t.draw()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.UP:
            self.menu_index = (self.menu_index - 1) % len(self.menu_options)
        elif key == arcade.key.DOWN:
            self.menu_index = (self.menu_index + 1) % len(self.menu_options)
        elif key == arcade.key.ENTER:
            if self.menu_index == 0:
                self.sound_start.play()
                self.window.show_view(BattleView())
            elif self.menu_index == 1:
                self.window.show_view(AchievementView())
            elif self.menu_index == 2:
                self.window.close()
        elif key == arcade.key.ESCAPE:
            self.window.close()

class AchievementView(arcade.View):
    def __init__(self):
        super().__init__()
        self.title_text = arcade.Text("업적 리스트", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100,
                                      arcade.color.WHITE, font_size=30, anchor_x="center", bold=True)
        self.achievement_info = [
            ("zekrom_finish", "제크로무로 마지막 일격 가하기"),
            ("wide_guard_block", "와이드가드로 광역 공격 막기"),
            ("haze_reset", "흑안개로 레시라무 능력치 초기화")
        ]
        self.achievement_texts = [arcade.Text("", 100, SCREEN_HEIGHT - 200 - (i * 80), 
                                              arcade.color.WHITE, font_size=20)
                                  for i in range(len(self.achievement_info))]
        self.back_text = arcade.Text("'B' 키를 눌러 타이틀로 돌아가기", SCREEN_WIDTH / 2, 100,
                                     arcade.color.GRAY, font_size=16, anchor_x="center")

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        self.title_text.draw()
        
        for i, (key, desc) in enumerate(self.achievement_info):
            status = "완료" if ACHIEVEMENTS[key] else "미완료"
            color = arcade.color.GREEN if ACHIEVEMENTS[key] else arcade.color.RED
            t = self.achievement_texts[i]
            t.text = f"{desc}: {status}"
            t.color = color
            t.draw()

        self.back_text.draw()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.B:
            self.window.show_view(TitleView())

class BattleView(arcade.View):
    def __init__(self):
        super().__init__()
        # --- 데이터 엔진 및 객체 초기화 ---
        self.engine = BattleEngine()
        
        # UI 이미지 로드
        self.tex_hp_enemy = arcade.load_texture("ui/hp_left.png")   # 적군용 프레임
        self.tex_hp_player = arcade.load_texture("ui/hp_right.png") # 아군용 프레임
        self.tex_layer = arcade.load_texture("ui/layer.png")       # HP 게이지용
        
        # 1. 파티 데이터 구조화
        self.player_party = [
            Pokemon("Zekrom"),
            Pokemon("Chandelure"),
            Pokemon("Venusaur"),
            Pokemon("Primarina")
        ]
        
        self.active_p1 = self.player_party[0]
        self.active_p2 = self.player_party[1]
        self.boss = Pokemon("Reshiram")
        
        self.boss.max_hp *= 2
        self.boss.hp = self.boss.max_hp
        for stat in self.boss.stat_stages:
            self.boss.stat_stages[stat] = 1

        self.current_state = STATE_BATTLE_PHASE
        self.turn_count = 1
        self.cursor_index = 0
        self.action_cursor_index = 0
        
        self.p1_action = None
        self.p2_action = None
        self.faint_switch_queue = []
        self.current_faint_slot = None

        self.log_queue = [
            f"레시라무가 등장했다!",
            "레시라무는 폭주하는 에너지로 모든 능력치가 1단계 증가했다!",
            "어떤 행동을 할까?"
        ]
        self.visible_logs = []
        self._update_visible_logs()

        # UI Text 객체 관리 (위치는 on_draw에서 매 프레임 업데이트됨)
        self.boss_label = arcade.Text("", 0, 0, arcade.color.BLACK, 14, bold=True)
        self.p1_label = arcade.Text("", 0, 0, arcade.color.BLACK, 14, bold=True)
        self.p2_label = arcade.Text("", 0, 0, arcade.color.BLACK, 14, bold=True)
        
        self.log_texts = [arcade.Text("", 30, 110 - (i * 40), arcade.color.WHITE, 16) for i in range(2)]
        self.menu_title = arcade.Text("", 30, 120, arcade.color.YELLOW, 16, bold=True)
        self.undo_hint = arcade.Text("(B 키를 누르면 이전 단계/포켓몬 취소)", 250, 120, arcade.color.GRAY, 12)
        self.move_texts = [arcade.Text("", 0, 0, arcade.color.WHITE, 16) for _ in range(4)]
        self.action_texts = [arcade.Text("", 0, 0, arcade.color.WHITE, 18, bold=True) for _ in range(2)]
        self.continue_text = arcade.Text("▶ 엔터를 눌러 다음...", 600, 30, arcade.color.YELLOW, 14)
        self.game_over_text = arcade.Text("▶ 전투 종료 (Enter를 눌러 타이틀로)", 550, 30, arcade.color.RED, 14)
        self.warning_text = arcade.Text("", 400, 300, arcade.color.RED, 20, bold=True, anchor_x="center")
        self.warning_timer = 0
        
        self.achievement_notified = False

    def _update_visible_logs(self):
        self.visible_logs = []
        for _ in range(2):
            if self.log_queue:
                self.visible_logs.append(self.log_queue.pop(0))

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def draw_hp_ui(self, x, y, poke, is_enemy=False):
        """본가 스타일의 HP UI 프레임과 게이지를 그립니다."""
        # 요청에 따라 적군(보스)과 아군의 프레임 이미지를 서로 바꿈
        # 이전에 보스는 hp_left, 아군은 hp_right를 썼으나 이제 반대로 적용
        texture = self.tex_hp_player if is_enemy else self.tex_hp_enemy
        
        # 화면 끝에 맞추기 위한 위치 보정 (중심 좌표 기준)
        render_width = texture.width * 1.2
        render_height = texture.height * 1.2
        
        arcade.draw_texture_rect(texture, arcade.XYWH(x, y, render_width, render_height))
        
        # 체력바 오프셋
        hp_ratio = max(0, min(poke.hp / poke.max_hp, 1))
        full_bar_width = 115
        bar_height = 8
        
        # 프레임이 바뀌었으므로 오프셋 로직도 서로 교차하여 적용
        if is_enemy:
            # 보스가 아군용 프레임(hp_right)의 오프셋을 사용하도록 수정
            bar_x = x + 43
            bar_y = y - 15
            label_x = x - 130
            label_y = y + 5
            current_label = self.boss_label
        else:
            # 아군이 적군용 프레임(hp_left)의 오프셋을 사용하도록 수정
            bar_x = x + 65
            bar_y = y - 15
            label_x = x - 110
            label_y = y +10
            current_label = self.p1_label if poke == self.active_p1 else self.p2_label
            
            # HP 수치 텍스트 (아군만 표시)
            hp_text = f"{poke.hp} / {poke.max_hp}"
            arcade.draw_text(hp_text, x - 35, y - 14, arcade.color.BLACK, 12, bold=True, anchor_x="right")

        # 게이지 배경 (회색)
        arcade.draw_rect_filled(arcade.XYWH(bar_x, bar_y, full_bar_width, bar_height), arcade.color.DARK_GRAY)
        
        # 게이지 색상 레이어
        if hp_ratio > 0.5: color = arcade.color.GREEN
        elif hp_ratio > 0.2: color = arcade.color.YELLOW
        else: color = arcade.color.RED
        
        current_bar_width = full_bar_width * hp_ratio
        if current_bar_width > 0:
            actual_bar_x = (bar_x - full_bar_width / 2) + (current_bar_width / 2)
            arcade.draw_rect_filled(arcade.XYWH(actual_bar_x, bar_y, current_bar_width, bar_height), color)

        # 이름 출력
        current_label.text = poke.ko_name
        current_label.x = label_x
        current_label.y = label_y
        current_label.draw()

    def on_draw(self):
        self.clear()

        # 1. 배경 및 스프라이트 배치 (대각선 구도)
        # 보스(레시라무): 우측 상단 (더 위로 올림)
        boss_sprite_x, boss_y = 650, 450
        arcade.draw_rect_filled(arcade.XYWH(boss_sprite_x, boss_y, 180, 180), arcade.color.DARK_RED)
        
        # 플레이어 1: 좌측 하단 (더 왼쪽으로)
        p1_sprite_x, p1_sprite_y = 120, 220
        p1_color = arcade.color.BLUE if not self.active_p1.is_fainted() else arcade.color.GRAY
        arcade.draw_rect_filled(arcade.XYWH(p1_sprite_x, p1_sprite_y, 120, 120), p1_color)
        
        # 플레이어 2: 좌측 하단 (더 왼쪽으로)
        p2_sprite_x, p2_sprite_y = 270, 220
        p2_color = arcade.color.PURPLE if not self.active_p2.is_fainted() else arcade.color.GRAY
        arcade.draw_rect_filled(arcade.XYWH(p2_sprite_x, p2_sprite_y, 120, 120), p2_color)

        # 2. UI 프레임 배치
        # 보스 UI: 좌측 상단, 왼쪽 끝에 밀착
        # 프레임 너비가 약 250px이므로 x=125 정도면 왼쪽 끝에 닿음
        boss_ui_x = (self.tex_hp_enemy.width * 1.2) / 2
        self.draw_hp_ui(boss_ui_x, 530, self.boss, is_enemy=True)
        
        # 플레이어 UI: 우측 하단, 오른쪽 끝에 밀착
        player_ui_x = SCREEN_WIDTH - (self.tex_hp_player.width * 1.2) / 2
        self.draw_hp_ui(player_ui_x, 300, self.active_p1, is_enemy=False)
        self.draw_hp_ui(player_ui_x, 200, self.active_p2, is_enemy=False)

        # 3. 하단 UI 박스 및 로그/메뉴
        arcade.draw_rect_outline(arcade.XYWH(400, 80, 780, 140), arcade.color.WHITE, 2)

        if self.current_state in [STATE_P1_ACTION, STATE_P2_ACTION]:
            self.draw_action_select()
        elif self.current_state in [STATE_P1_MOVE, STATE_P2_MOVE]:
            self.draw_move_menu()
        elif self.current_state in [STATE_P1_PARTY, STATE_P2_PARTY, STATE_FAINT_SWITCH]:
            self.draw_party_select()
        else:
            self.draw_battle_logs()
            
        if self.warning_timer > 0:
            self.warning_text.draw()
            self.warning_timer -= 1

    def draw_action_select(self):
        current_poke = self.active_p1 if self.current_state == STATE_P1_ACTION else self.active_p2
        self.menu_title.text = f"[{current_poke.ko_name}의 행동 선택]"
        self.menu_title.draw()
        if self.current_state == STATE_P2_ACTION:
            self.undo_hint.draw()

        options = ["싸운다", "포켓몬"]
        positions = [(100, 50), (400, 50)]
        for i in range(2):
            t = self.action_texts[i]
            t.x, t.y = positions[i]
            t.color = arcade.color.YELLOW if i == self.action_cursor_index else arcade.color.WHITE
            prefix = "▶ " if i == self.action_cursor_index else "  "
            t.text = f"{prefix}{options[i]}"
            t.draw()

    def draw_move_menu(self):
        current_poke = self.active_p1 if self.current_state == STATE_P1_MOVE else self.active_p2
        moves_ko = [MOVES[m]["ko"] for m in current_poke.moves]
        self.menu_title.text = f"[{current_poke.ko_name}의 기술 선택]"
        self.menu_title.draw()
        self.undo_hint.draw()

        positions = [(50, 70), (350, 70), (50, 30), (350, 30)]
        for i in range(4):
            t = self.move_texts[i]
            t.x, t.y = positions[i]
            t.color = arcade.color.GREEN if i == self.cursor_index else arcade.color.WHITE
            prefix = "▶ " if i == self.cursor_index else "  "
            t.text = f"{prefix}{moves_ko[i]}"
            t.draw()

    def draw_party_select(self):
        arcade.draw_rect_filled(arcade.XYWH(400, 300, 700, 500), arcade.color.DARK_BLUE_GRAY)
        arcade.draw_rect_outline(arcade.XYWH(400, 300, 700, 500), arcade.color.WHITE, 3)
        title = "교체할 포켓몬을 선택하세요"
        if self.current_state == STATE_FAINT_SWITCH:
            title = f"기절한 {self.player_party[self.current_faint_slot-1].ko_name} 대신 나올 포켓몬을 선택하세요"
        arcade.draw_text(title, 400, 520, arcade.color.WHITE, 20, bold=True, anchor_x="center")
        arcade.draw_text("(B 키를 누르면 취소)", 400, 80, arcade.color.GRAY, 14, anchor_x="center")

        grid_pos = [(250, 400), (550, 400), (250, 270), (550, 270)]
        for i in range(4):
            poke = self.player_party[i]
            x, y = grid_pos[i]
            is_active = (poke == self.active_p1 or poke == self.active_p2)
            is_fainted = poke.is_fainted()
            is_selectable = not is_active and not is_fainted
            bg_color = arcade.color.GRAY if not is_selectable else (arcade.color.YELLOW_ORANGE if i == self.cursor_index else arcade.color.INDIGO)
            arcade.draw_rect_filled(arcade.XYWH(x, y, 280, 110), bg_color)
            arcade.draw_rect_outline(arcade.XYWH(x, y, 280, 110), arcade.color.WHITE, 2)
            rect_color = arcade.color.BLUE if i == 0 else (arcade.color.PURPLE if i == 1 else (arcade.color.GREEN if i == 2 else arcade.color.GOLDENROD))
            if is_fainted: rect_color = arcade.color.BLACK
            arcade.draw_rect_filled(arcade.XYWH(x - 80, y, 60, 60), rect_color)
            arcade.draw_text(poke.ko_name, x, y + 20, arcade.color.WHITE, 16, bold=True)
            hp_color = arcade.color.GREEN if poke.hp / poke.max_hp > 0.5 else (arcade.color.YELLOW if poke.hp / poke.max_hp > 0.2 else arcade.color.RED)
            arcade.draw_text(f"HP: {poke.hp}/{poke.max_hp}", x, y - 10, hp_color, 14)
            if is_active:
                arcade.draw_text("전투 중", x + 80, y - 30, arcade.color.CYAN, 12, bold=True, anchor_x="right")
            elif is_fainted:
                arcade.draw_text("기절함", x + 80, y - 30, arcade.color.RED, 12, bold=True, anchor_x="right")

    def draw_battle_logs(self):
        for i, log in enumerate(self.visible_logs):
            if i < len(self.log_texts):
                t = self.log_texts[i]
                t.text = log
                t.draw()
        if self.current_state == STATE_BATTLE_PHASE:
            if self.log_queue or self.visible_logs:
                self.continue_text.draw()
        elif self.current_state == STATE_GAME_OVER:
            self.game_over_text.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(TitleView())
            return

        if self.current_state == STATE_GAME_OVER:
            if key == arcade.key.ENTER:
                self.window.show_view(TitleView())
            return

        if self.current_state in [STATE_P1_ACTION, STATE_P2_ACTION]:
            if key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.action_cursor_index = 1 - self.action_cursor_index
            elif key == arcade.key.ENTER:
                if self.action_cursor_index == 0:
                    self.current_state = STATE_P1_MOVE if self.current_state == STATE_P1_ACTION else STATE_P2_MOVE
                    self.cursor_index = 0
                else:
                    self.current_state = STATE_P1_PARTY if self.current_state == STATE_P1_ACTION else STATE_P2_PARTY
                    self.cursor_index = 0
            elif (key == arcade.key.B or key == arcade.key.BACKSPACE) and self.current_state == STATE_P2_ACTION:
                self.current_state = STATE_P1_ACTION
                self.action_cursor_index = 0

        elif self.current_state in [STATE_P1_MOVE, STATE_P2_MOVE]:
            if key == arcade.key.UP and self.cursor_index >= 2: self.cursor_index -= 2
            elif key == arcade.key.DOWN and self.cursor_index <= 1: self.cursor_index += 2
            elif key == arcade.key.LEFT and self.cursor_index % 2 != 0: self.cursor_index -= 1
            elif key == arcade.key.RIGHT and self.cursor_index % 2 == 0: self.cursor_index += 1
            elif key == arcade.key.ENTER:
                if self.current_state == STATE_P1_MOVE:
                    self.p1_action = {"type": "move", "attacker": self.active_p1, "index": self.cursor_index}
                    if self.active_p2.is_fainted():
                        self.p2_action = None
                        self.start_battle_phase()
                    else:
                        self.current_state = STATE_P2_ACTION
                        self.action_cursor_index = 0
                else:
                    self.p2_action = {"type": "move", "attacker": self.active_p2, "index": self.cursor_index}
                    self.start_battle_phase()
            elif key == arcade.key.B or key == arcade.key.BACKSPACE:
                self.current_state = STATE_P1_ACTION if self.current_state == STATE_P1_MOVE else STATE_P2_ACTION
                self.action_cursor_index = 0

        elif self.current_state in [STATE_P1_PARTY, STATE_P2_PARTY, STATE_FAINT_SWITCH]:
            if key == arcade.key.UP and self.cursor_index >= 2: self.cursor_index -= 2
            elif key == arcade.key.DOWN and self.cursor_index <= 1: self.cursor_index += 2
            elif key == arcade.key.LEFT and self.cursor_index % 2 != 0: self.cursor_index -= 1
            elif key == arcade.key.RIGHT and self.cursor_index % 2 == 0: self.cursor_index += 1
            elif key == arcade.key.ENTER:
                target_poke = self.player_party[self.cursor_index]
                if target_poke == self.active_p1 or target_poke == self.active_p2:
                    self.show_warning("이미 필드에 있는 포켓몬입니다!")
                    return
                if target_poke.is_fainted():
                    self.show_warning("기절한 포켓몬은 선택할 수 없습니다!")
                    return
                if self.current_state == STATE_P1_PARTY:
                    self.p1_action = {"type": "switch", "slot": 1, "target_poke": target_poke, "switched_out": self.active_p1}
                    if self.active_p2.is_fainted():
                        self.p2_action = None
                        self.start_battle_phase()
                    else:
                        self.current_state = STATE_P2_ACTION
                        self.action_cursor_index = 0
                elif self.current_state == STATE_P2_PARTY:
                    self.p2_action = {"type": "switch", "slot": 2, "target_poke": target_poke, "switched_out": self.active_p2}
                    self.start_battle_phase()
                elif self.current_state == STATE_FAINT_SWITCH:
                    if self.current_faint_slot == 1: self.active_p1 = target_poke
                    else: self.active_p2 = target_poke
                    self.log_queue.append(f"가라! {target_poke.ko_name}!")
                    self.process_faint_switch_queue()
            elif (key == arcade.key.B or key == arcade.key.BACKSPACE) and self.current_state != STATE_FAINT_SWITCH:
                self.current_state = STATE_P1_ACTION if self.current_state == STATE_P1_PARTY else STATE_P2_ACTION
                self.action_cursor_index = 1

        elif self.current_state == STATE_BATTLE_PHASE:
            if key == arcade.key.ENTER:
                if self.log_queue:
                    self._update_visible_logs()
                else:
                    self.check_fainted_and_continue()

    def show_warning(self, msg):
        self.warning_text.text = msg
        self.warning_timer = 90

    def check_fainted_and_continue(self):
        self.faint_switch_queue = []
        if self.active_p1.is_fainted(): self.faint_switch_queue.append(1)
        if self.active_p2.is_fainted(): self.faint_switch_queue.append(2)
        if self.faint_switch_queue:
            can_switch = any(not p.is_fainted() and p != self.active_p1 and p != self.active_p2 for p in self.player_party)
            if not can_switch:
                if all(p.is_fainted() for p in self.player_party):
                    self.current_state = STATE_GAME_OVER
                    self.visible_logs = ["모든 포켓몬이 쓰러졌습니다! 패배했습니다..."]
                    return
            self.process_faint_switch_queue()
        else:
            if self.boss.is_fainted():
                self.current_state = STATE_GAME_OVER
                msg = f"승리했습니다! {self.boss.ko_name}을(를) 물리쳤습니다."
                
                # 업적 달성 알림 추가
                notified_any = False
                if ACHIEVEMENTS["zekrom_finish"]:
                    msg += "\n[업적 달성!] 제크로무의 일격"
                    notified_any = True
                if ACHIEVEMENTS["wide_guard_block"]:
                    msg += "\n[업적 달성!] 와이드가드 방어"
                    notified_any = True
                if ACHIEVEMENTS["haze_reset"]:
                    msg += "\n[업적 달성!] 흑안개 초기화"
                    notified_any = True
                
                self.visible_logs = msg.split("\n")
            else:
                self.current_state = STATE_P1_ACTION
                self.action_cursor_index = 0
                self.log_queue = ["어떤 행동을 할까?"]
                self._update_visible_logs()

    def process_faint_switch_queue(self):
        if self.faint_switch_queue:
            self.current_faint_slot = self.faint_switch_queue.pop(0)
            self.current_state = STATE_FAINT_SWITCH
            self.cursor_index = 0
        else:
            if self.boss.is_fainted():
                self.current_state = STATE_GAME_OVER
                self.visible_logs = [f"승리했습니다! {self.boss.ko_name}을(를) 물리쳤습니다."]
            else:
                self.current_state = STATE_P1_ACTION
                self.action_cursor_index = 0
                self.log_queue = ["어떤 행동을 할까?"]
                self._update_visible_logs()

    def start_battle_phase(self):
        self.current_state = STATE_BATTLE_PHASE
        self.visible_logs = []
        self.log_queue = []
        action_list = []
        for action in [self.p1_action, self.p2_action]:
            if action:
                if action["type"] == "move":
                    move_name = action["attacker"].moves[action["index"]]
                    action_list.append({"type": "move", "attacker": action["attacker"], "defender": self.boss, "move": move_name})
                elif action["type"] == "switch":
                    action_list.append(action)
        if not self.boss.is_fainted():
            boss_action = self.engine.get_boss_ai_action(self.boss, [self.active_p1, self.active_p2], self.turn_count)
            if boss_action:
                boss_action["type"] = "move"
                action_list.append(boss_action)
        results = self.engine.execute_turn(action_list)
        for res in results:
            if res.get("type") == "switch":
                if res["slot"] == 1: self.active_p1 = res["target_poke"]
                else: self.active_p2 = res["target_poke"]
                self.log_queue.append(res["msg"])
                continue
            for line in res['msg'].split('\n'):
                if line: self.log_queue.append(line)
            if res['is_ko']: self.log_queue.append(f"{res['defender']}은(는) 쓰러졌다!")
        self.turn_count += 1
        self._update_visible_logs()
        self.p1_action = None
        self.p2_action = None

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.show_view(StoryView())
    arcade.run()

if __name__ == "__main__":
    main()
