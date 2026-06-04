import arcade
import random
from data.battle_engine import BattleEngine, Pokemon
from data.moves import MOVES

# --- 화면 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "폭주! 레시라무"

# --- 상태(State) 상수 ---
STATE_P1_SELECT = 1     # 1번 포켓몬 기술 선택 중
STATE_P2_SELECT = 2     # 2번 포켓몬 기술 선택 중
STATE_BATTLE_PHASE = 3  # 턴 연산 및 텍스트 출력 중
STATE_GAME_OVER = 4     # 전투 종료

class BattleGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        # --- 데이터 엔진 및 객체 초기화 ---
        self.engine = BattleEngine()
        
        # 포켓몬 객체 생성
        self.p1 = Pokemon("Primarina")
        self.p2 = Pokemon("Zekrom")
        self.boss = Pokemon("Reshiram")

        # 기술 목록 (한글 표시용)
        self.p1_moves_ko = [MOVES[m]["ko"] for m in self.p1.moves]
        self.p2_moves_ko = [MOVES[m]["ko"] for m in self.p2.moves]

        # --- 시스템 변수 초기화
        self.current_state = STATE_P1_SELECT
        self.cursor_index = 0
        self.p1_selected_move_idx = None
        self.p2_selected_move_idx = None
        
        # 화면 하단에 띄울 전투 로그 및 페이지 관리
        self.log_queue = [f"야생의 {self.boss.ko_name}이(가) 나타났다!", "어떤 기술을 사용할까?"]
        self.visible_logs = []  # 현재 화면에 보이는 최대 2줄
        self._update_visible_logs()

        # --- 성능 최적화를 위한 Text 객체 관리 ---
        self.boss_label = arcade.Text("", 400, 540, arcade.color.WHITE, 16, bold=True, anchor_x="center")
        self.p1_label = arcade.Text("", 200, 310, arcade.color.WHITE, 14, align="center", anchor_x="center", multiline=True, width=200)
        self.p2_label = arcade.Text("", 600, 310, arcade.color.WHITE, 14, align="center", anchor_x="center", multiline=True, width=200)
        self.log_texts = [arcade.Text("", 30, 110 - (i * 40), arcade.color.WHITE, 16) for i in range(2)]
        self.menu_title = arcade.Text("", 30, 120, arcade.color.YELLOW, 16, bold=True)
        self.undo_hint = arcade.Text("(B 키를 누르면 이전 포켓몬 취소)", 250, 120, arcade.color.GRAY, 12)
        self.move_texts = [arcade.Text("", 0, 0, arcade.color.WHITE, 16) for _ in range(4)]
        self.continue_text = arcade.Text("▶ 엔터를 눌러 다음...", 600, 30, arcade.color.YELLOW, 14)
        self.game_over_text = arcade.Text("▶ 전투 종료 (Esc를 눌러 종료)", 550, 30, arcade.color.RED, 14)

    def _update_visible_logs(self):
        """현재 로그 큐에서 최대 2줄을 가져와 visible_logs를 업데이트합니다."""
        self.visible_logs = []
        for _ in range(2):
            if self.log_queue:
                self.visible_logs.append(self.log_queue.pop(0))

    def on_draw(self):
        self.clear()

        # 1. 보스 (레시라무)
        arcade.draw_rect_filled(arcade.XYWH(400, 450, 150, 150), arcade.color.DARK_RED)
        self.boss_label.text = f"{self.boss.ko_name} HP: {self.boss.hp}/{self.boss.max_hp}"
        self.boss_label.draw()

        # 2. 플레이어 1
        p1_color = arcade.color.BLUE if not self.p1.is_fainted() else arcade.color.GRAY
        arcade.draw_rect_filled(arcade.XYWH(200, 250, 100, 100), p1_color)
        self.p1_label.text = f"1. {self.p1.ko_name}\nHP: {self.p1.hp}/{self.p1.max_hp}"
        self.p1_label.draw()

        # 3. 플레이어 2
        p2_color = arcade.color.PURPLE if not self.p2.is_fainted() else arcade.color.GRAY
        arcade.draw_rect_filled(arcade.XYWH(600, 250, 100, 100), p2_color)
        self.p2_label.text = f"2. {self.p2.ko_name}\nHP: {self.p2.hp}/{self.p2.max_hp}"
        self.p2_label.draw()

        # 4. 하단 UI 박스
        arcade.draw_rect_outline(arcade.XYWH(400, 80, 780, 140), arcade.color.WHITE, 2)

        # 5. 상태에 따른 UI 렌더링
        if self.current_state in [STATE_P1_SELECT, STATE_P2_SELECT]:
            self.draw_action_menu()
        else:
            self.draw_battle_logs()

    def draw_action_menu(self):
        if self.current_state == STATE_P1_SELECT:
            current_poke_name = self.p1.ko_name
            moves_ko = self.p1_moves_ko
        else:
            current_poke_name = self.p2.ko_name
            moves_ko = self.p2_moves_ko
        
        self.menu_title.text = f"[{current_poke_name}의 행동 선택]"
        self.menu_title.draw()
        
        if self.current_state == STATE_P2_SELECT:
            self.undo_hint.draw()

        positions = [(50, 70), (350, 70), (50, 30), (350, 30)]
        for i in range(4):
            t = self.move_texts[i]
            t.x, t.y = positions[i]
            t.color = arcade.color.GREEN if i == self.cursor_index else arcade.color.WHITE
            prefix = "▶ " if i == self.cursor_index else "  "
            t.text = f"{prefix}{moves_ko[i]}"
            t.draw()

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
        """키보드 입력을 처리하는 상태 머신 (뇌)"""
        # [강력 수정] 언제 어디서든 Esc를 누르면 즉시 창을 닫고 종료
        if key == arcade.key.ESCAPE:
            self.close()
            return

        if self.current_state == STATE_GAME_OVER:
            return

        if self.current_state in [STATE_P1_SELECT, STATE_P2_SELECT]:
            if key == arcade.key.UP and self.cursor_index >= 2:
                self.cursor_index -= 2
            elif key == arcade.key.DOWN and self.cursor_index <= 1:
                self.cursor_index += 2
            elif key == arcade.key.LEFT and self.cursor_index % 2 != 0:
                self.cursor_index -= 1
            elif key == arcade.key.RIGHT and self.cursor_index % 2 == 0:
                self.cursor_index += 1
            elif key == arcade.key.ENTER:
                if self.current_state == STATE_P1_SELECT:
                    self.p1_selected_move_idx = self.cursor_index
                    if self.p2.is_fainted():
                        self.p2_selected_move_idx = None
                        self.start_battle_phase()
                    else:
                        self.current_state = STATE_P2_SELECT
                        self.cursor_index = 0
                elif self.current_state == STATE_P2_SELECT:
                    self.p2_selected_move_idx = self.cursor_index
                    self.start_battle_phase()
            elif (key == arcade.key.B or key == arcade.key.BACKSPACE) and self.current_state == STATE_P2_SELECT:
                self.p1_selected_move_idx = None
                self.current_state = STATE_P1_SELECT
                self.cursor_index = 0

        elif self.current_state == STATE_BATTLE_PHASE:
            if key == arcade.key.ENTER:
                if self.log_queue:
                    self._update_visible_logs()
                else:
                    if self.boss.is_fainted() or (self.p1.is_fainted() and self.p2.is_fainted()):
                        self.current_state = STATE_GAME_OVER
                        msg = f"승리했습니다! {self.boss.ko_name}을(를) 물리쳤습니다." if self.boss.is_fainted() else "패배했습니다... 모든 포켓몬이 쓰러졌습니다."
                        self.visible_logs = [msg]
                    else:
                        if self.p1.is_fainted():
                            self.current_state = STATE_P2_SELECT
                        else:
                            self.current_state = STATE_P1_SELECT
                        self.cursor_index = 0
                        self.log_queue = ["어떤 기술을 사용할까?"]
                        self._update_visible_logs()

    def start_battle_phase(self):
        self.current_state = STATE_BATTLE_PHASE
        self.visible_logs = []
        self.log_queue = []
        action_list = []
        
        if not self.p1.is_fainted() and self.p1_selected_move_idx is not None:
            move_name = self.p1.moves[self.p1_selected_move_idx]
            action_list.append({"attacker": self.p1, "defender": self.boss, "move": move_name})
            
        if not self.p2.is_fainted() and self.p2_selected_move_idx is not None:
            move_name = self.p2.moves[self.p2_selected_move_idx]
            action_list.append({"attacker": self.p2, "defender": self.boss, "move": move_name})
            
        if not self.boss.is_fainted():
            targets = []
            if not self.p1.is_fainted(): targets.append(self.p1)
            if not self.p2.is_fainted(): targets.append(self.p2)
            if targets:
                target = random.choice(targets)
                boss_move = random.choice(self.boss.moves)
                action_list.append({"attacker": self.boss, "defender": target, "move": boss_move})
        
        results = self.engine.execute_turn(action_list)
        for res in results:
            self.log_queue.append(res['msg'])
            if res['is_ko']:
                self.log_queue.append(f"{res['defender']}은(는) 쓰러졌다!")
        self._update_visible_logs()

def main():
    game = BattleGame()
    arcade.run()

if __name__ == "__main__":
    main()
