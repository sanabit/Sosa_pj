import arcade
import random
from data.battle_engine import BattleEngine, Pokemon
from data.moves import MOVES

# --- 화면 설정 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "폭주! 레시라무"

# --- 상태(State) 상수 ---
STATE_P1_ACTION = 1      # 1번 포켓몬 행동 선택 ([싸운다], [포켓몬])
STATE_P1_MOVE = 2        # 1번 포켓몬 기술 선택
STATE_P1_PARTY = 3       # 1번 포켓몬 교체 선택
STATE_P2_ACTION = 4      # 2번 포켓몬 행동 선택
STATE_P2_MOVE = 5        # 2번 포켓몬 기술 선택
STATE_P2_PARTY = 6       # 2번 포켓몬 교체 선택
STATE_BATTLE_PHASE = 7   # 턴 연산 및 텍스트 출력 중
STATE_GAME_OVER = 8      # 전투 종료
STATE_FAINT_SWITCH = 9   # 기절 시 강제 교체

class BattleGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)

        # --- 데이터 엔진 및 객체 초기화 ---
        self.engine = BattleEngine()
        
        # 1. 파티 데이터 구조화
        self.player_party = [
            Pokemon("Zekrom"),
            Pokemon("Chandelure"),
            Pokemon("Venusaur"),
            Pokemon("Primarina")
        ]
        
        # 필드에 나와 있는 포켓몬 (슬롯 1, 슬롯 2)
        self.active_p1 = self.player_party[0]
        self.active_p2 = self.player_party[1]
        
        self.boss = Pokemon("Reshiram")
        
        # 보스 체력 2배 강화
        self.boss.max_hp *= 2
        self.boss.hp = self.boss.max_hp
        
        # 보스 초기 능력치 1단계 상승 (폭주 에너지)
        for stat in self.boss.stat_stages:
            self.boss.stat_stages[stat] = 1

        # --- 시스템 변수 초기화
        self.current_state = STATE_BATTLE_PHASE
        self.turn_count = 1
        self.cursor_index = 0
        self.action_cursor_index = 0 # [싸운다], [포켓몬] 선택용
        
        self.p1_action = None  # {"type": "move", "index": 0} or {"type": "switch", "target_idx": 2}
        self.p2_action = None
        
        # 기절 교체 관리
        self.faint_switch_queue = [] # 기절해서 교체가 필요한 슬롯 번호 (1 또는 2)
        self.current_faint_slot = None

        # 화면 하단에 띄울 전투 로그 및 페이지 관리
        self.log_queue = [
            f"레시라무가 등장했다!",
            "레시라무는 폭주하는 에너지로 모든 능력치가 1단계 증가했다!",
            "어떤 행동을 할까?"
        ]
        self.visible_logs = []
        self._update_visible_logs()

        # --- 성능 최적화를 위한 Text 객체 관리 ---
        self.boss_label = arcade.Text("", 400, 540, arcade.color.WHITE, 16, bold=True, anchor_x="center")
        self.p1_label = arcade.Text("", 200, 310, arcade.color.WHITE, 14, align="center", anchor_x="center", multiline=True, width=200)
        self.p2_label = arcade.Text("", 600, 310, arcade.color.WHITE, 14, align="center", anchor_x="center", multiline=True, width=200)
        self.log_texts = [arcade.Text("", 30, 110 - (i * 40), arcade.color.WHITE, 16) for i in range(2)]
        self.menu_title = arcade.Text("", 30, 120, arcade.color.YELLOW, 16, bold=True)
        self.undo_hint = arcade.Text("(B 키를 누르면 이전 단계/포켓몬 취소)", 250, 120, arcade.color.GRAY, 12)
        self.move_texts = [arcade.Text("", 0, 0, arcade.color.WHITE, 16) for _ in range(4)]
        self.action_texts = [arcade.Text("", 0, 0, arcade.color.WHITE, 18, bold=True) for _ in range(2)]
        self.continue_text = arcade.Text("▶ 엔터를 눌러 다음...", 600, 30, arcade.color.YELLOW, 14)
        self.game_over_text = arcade.Text("▶ 전투 종료 (Esc를 눌러 종료)", 550, 30, arcade.color.RED, 14)
        self.warning_text = arcade.Text("", 400, 300, arcade.color.RED, 20, bold=True, anchor_x="center")
        self.warning_timer = 0

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
        p1_color = arcade.color.BLUE if not self.active_p1.is_fainted() else arcade.color.GRAY
        arcade.draw_rect_filled(arcade.XYWH(200, 250, 100, 100), p1_color)
        self.p1_label.text = f"1. {self.active_p1.ko_name}\nHP: {self.active_p1.hp}/{self.active_p1.max_hp}"
        self.p1_label.draw()

        # 3. 플레이어 2
        p2_color = arcade.color.PURPLE if not self.active_p2.is_fainted() else arcade.color.GRAY
        arcade.draw_rect_filled(arcade.XYWH(600, 250, 100, 100), p2_color)
        self.p2_label.text = f"2. {self.active_p2.ko_name}\nHP: {self.active_p2.hp}/{self.active_p2.max_hp}"
        self.p2_label.draw()

        # 4. 하단 UI 박스
        arcade.draw_rect_outline(arcade.XYWH(400, 80, 780, 140), arcade.color.WHITE, 2)

        # 5. 상태에 따른 UI 렌더링
        if self.current_state in [STATE_P1_ACTION, STATE_P2_ACTION]:
            self.draw_action_select()
        elif self.current_state in [STATE_P1_MOVE, STATE_P2_MOVE]:
            self.draw_move_menu()
        elif self.current_state in [STATE_P1_PARTY, STATE_P2_PARTY, STATE_FAINT_SWITCH]:
            self.draw_party_select()
        else:
            self.draw_battle_logs()
            
        # 경고 메시지 출력
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
        # 파티 창 렌더링 (6등분 격자 중 4칸 사용)
        arcade.draw_rect_filled(arcade.XYWH(400, 300, 700, 500), arcade.color.DARK_BLUE_GRAY)
        arcade.draw_rect_outline(arcade.XYWH(400, 300, 700, 500), arcade.color.WHITE, 3)
        
        title = "교체할 포켓몬을 선택하세요"
        if self.current_state == STATE_FAINT_SWITCH:
            title = f"기절한 {self.player_party[self.current_faint_slot-1].ko_name} 대신 나올 포켓몬을 선택하세요"
        arcade.draw_text(title, 400, 520, arcade.color.WHITE, 20, bold=True, anchor_x="center")
        arcade.draw_text("(B 키를 누르면 취소)", 400, 80, arcade.color.GRAY, 14, anchor_x="center")

        # 2열 x 3행 격자
        # 상: (250, 400), (550, 400)
        # 중: (250, 270), (550, 270)
        # 하: (250, 140), (550, 140)
        grid_pos = [(250, 400), (550, 400), (250, 270), (550, 270)]
        
        for i in range(4):
            poke = self.player_party[i]
            x, y = grid_pos[i]
            
            # 선택 가능 여부 확인
            is_active = (poke == self.active_p1 or poke == self.active_p2)
            is_fainted = poke.is_fainted()
            is_selectable = not is_active and not is_fainted
            
            # 박스 색상
            bg_color = arcade.color.GRAY if not is_selectable else (arcade.color.YELLOW_ORANGE if i == self.cursor_index else arcade.color.INDIGO)
            arcade.draw_rect_filled(arcade.XYWH(x, y, 280, 110), bg_color)
            arcade.draw_rect_outline(arcade.XYWH(x, y, 280, 110), arcade.color.WHITE, 2)
            
            # 포켓몬 그래픽 (색상 사각형으로 대체)
            rect_color = arcade.color.BLUE if i == 0 else (arcade.color.PURPLE if i == 1 else (arcade.color.GREEN if i == 2 else arcade.color.GOLDENROD))
            if is_fainted: rect_color = arcade.color.BLACK
            arcade.draw_rect_filled(arcade.XYWH(x - 80, y, 60, 60), rect_color)
            
            # 이름 및 HP
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
        """키보드 입력을 처리하는 상태 머신 (뇌)"""
        if key == arcade.key.ESCAPE:
            self.close()
            return

        if self.current_state == STATE_GAME_OVER:
            return

        # 1. 행동 선택 상태 ([싸운다], [포켓몬])
        if self.current_state in [STATE_P1_ACTION, STATE_P2_ACTION]:
            if key == arcade.key.LEFT or key == arcade.key.RIGHT:
                self.action_cursor_index = 1 - self.action_cursor_index
            elif key == arcade.key.ENTER:
                if self.action_cursor_index == 0: # 싸운다
                    self.current_state = STATE_P1_MOVE if self.current_state == STATE_P1_ACTION else STATE_P2_MOVE
                    self.cursor_index = 0
                else: # 포켓몬
                    self.current_state = STATE_P1_PARTY if self.current_state == STATE_P1_ACTION else STATE_P2_PARTY
                    self.cursor_index = 0
            elif (key == arcade.key.B or key == arcade.key.BACKSPACE) and self.current_state == STATE_P2_ACTION:
                self.current_state = STATE_P1_ACTION
                self.action_cursor_index = 0

        # 2. 기술 선택 상태
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

        # 3. 파티 교체 선택 상태 (일반 교체 및 강제 교체)
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
                    # 강제 교체 처리
                    if self.current_faint_slot == 1:
                        self.active_p1 = target_poke
                    else:
                        self.active_p2 = target_poke
                    
                    self.log_queue.append(f"가라! {target_poke.ko_name}!")
                    self.process_faint_switch_queue()
                    
            elif (key == arcade.key.B or key == arcade.key.BACKSPACE) and self.current_state != STATE_FAINT_SWITCH:
                self.current_state = STATE_P1_ACTION if self.current_state == STATE_P1_PARTY else STATE_P2_ACTION
                self.action_cursor_index = 1 # [포켓몬]으로 돌아감

        # 4. 배틀 로그 상태
        elif self.current_state == STATE_BATTLE_PHASE:
            if key == arcade.key.ENTER:
                if self.log_queue:
                    self._update_visible_logs()
                else:
                    self.check_fainted_and_continue()

    def show_warning(self, msg):
        self.warning_text.text = msg
        self.warning_timer = 90 # 약 1.5초

    def check_fainted_and_continue(self):
        """턴 종료 후 기절 여부 체크 및 다음 상태 결정"""
        self.faint_switch_queue = []
        if self.active_p1.is_fainted():
            self.faint_switch_queue.append(1)
        if self.active_p2.is_fainted():
            self.faint_switch_queue.append(2)
            
        if self.faint_switch_queue:
            # 살아있는 대기 포켓몬이 있는지 확인
            can_switch = any(not p.is_fainted() and p != self.active_p1 and p != self.active_p2 for p in self.player_party)
            if not can_switch:
                # 더 이상 교체할 포켓몬이 없으면 게임 오버 체크
                if all(p.is_fainted() for p in self.player_party):
                    self.current_state = STATE_GAME_OVER
                    self.visible_logs = ["모든 포켓몬이 쓰러졌습니다! 패배했습니다..."]
                    return
            
            # 교체 창으로 이동
            self.process_faint_switch_queue()
        else:
            if self.boss.is_fainted():
                self.current_state = STATE_GAME_OVER
                self.visible_logs = [f"승리했습니다! {self.boss.ko_name}을(를) 물리쳤습니다."]
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
            # 모든 강제 교체 완료 후 다시 체크 (보스 승리 등)
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
        
        # 플레이어 액션 추가
        for action in [self.p1_action, self.p2_action]:
            if action:
                if action["type"] == "move":
                    move_name = action["attacker"].moves[action["index"]]
                    action_list.append({
                        "type": "move",
                        "attacker": action["attacker"],
                        "defender": self.boss,
                        "move": move_name
                    })
                elif action["type"] == "switch":
                    action_list.append(action)
            
        # 보스 AI 로직 적용
        if not self.boss.is_fainted():
            boss_action = self.engine.get_boss_ai_action(self.boss, [self.active_p1, self.active_p2], self.turn_count)
            if boss_action:
                boss_action["type"] = "move"
                action_list.append(boss_action)
        
        # 엔진 실행
        results = self.engine.execute_turn(action_list)
        
        # 결과 처리
        for res in results:
            if res.get("type") == "switch":
                # 실제 교체 적용 (엔진에서 처리한 뒤 결과를 받아와서 UI 업데이트)
                if res["slot"] == 1:
                    self.active_p1 = res["target_poke"]
                else:
                    self.active_p2 = res["target_poke"]
                self.log_queue.append(res["msg"])
                continue

            # 일반 기술 메시지 처리
            for line in res['msg'].split('\n'):
                if line:
                    self.log_queue.append(line)
            if res['is_ko']:
                self.log_queue.append(f"{res['defender']}은(는) 쓰러졌다!")
        
        self.turn_count += 1
        self._update_visible_logs()
        
        # 액션 초기화
        self.p1_action = None
        self.p2_action = None

def main():
    game = BattleGame()
    arcade.run()

if __name__ == "__main__":
    main()
