import random
from collections import deque
from data.pokemon_types import get_effectiveness
from data.moves import MOVES
from data.pokemon import POKEMON

class Pokemon:
    """
    전투 필드에 참여하는 개별 포켓몬의 상태와 능력치를 관리하는 클래스
    """
    def __init__(self, name):
        if name not in POKEMON:
            raise ValueError(f"Pokemon {name} not found in data.")
            
        data = POKEMON[name] #포켓몬 파일에서 데이터 호출
        self.name = name
        self.ko_name = data["ko"]
        self.types = data["types"]
        self.ability = data["ability"]
        self.moves = data["moves"]
        
        # 종족값 (Base Stats)
        self.base_stats = data["base_stats"]
        
        # 레벨 50 기준 능력치 계산 (개체값 31, 노력치 0 가정)
        self.level = 50
        self.hp = self._calc_hp(self.base_stats["hp"])
        self.max_hp = self.hp
        self.attack = self._calc_stat(self.base_stats["attack"])    
        self.defense = self._calc_stat(self.base_stats["defense"])
        self.sp_atk = self._calc_stat(self.base_stats["sp_atk"])
        self.sp_def = self._calc_stat(self.base_stats["sp_def"])
        self.speed = self._calc_stat(self.base_stats["speed"])

        # 상태 변수 (전투 중 관리)
        self.is_protecting = False  # 방어 상태
        self.is_wide_guarding = False  # 와이드가드 상태
        self.stat_stages = {
            "attack": 0, 
            "defense": 0, 
            "sp_atk": 0, 
            "sp_def": 0, 
            "speed": 0
        }  # 랭크업 상태
        self.is_phase_2 = False # 보스 2페이즈 진입 여부

    def _calc_hp(self, base):
        # 본가 HP 계산 공식: ((Base*2 + IV + EV/4) * Level / 100) + Level + 10
        return int((base * 2 + 31) * self.level / 100 + self.level + 10)

    def _calc_stat(self, base):
        # 본가 일반 능력치 계산 공식: (((Base*2 + IV + EV/4) * Level / 100) + 5) * Nature
        return int((base * 2 + 31) * self.level / 100 + 5)

    def is_fainted(self):
        return self.hp <= 0
    #기절했니? 라는 뜻

# 업적 데이터 (전역 관리)
ACHIEVEMENTS = {
    "zekrom_finish": False,
    "wide_guard_block": False,
    "haze_reset": False
}

class BattleEngine:
    """
    데미지 계산 및 턴 순서 처리를 담당하는 핵심 전투 엔진
    """
    
    def calculate_damage(self, attacker, defender, move_name):
        """
        포켓몬 본가 데미지 공식을 기반으로 최종 데미지 산출
        """
        if move_name not in MOVES:
            return 0
            
        move = MOVES[move_name]
        
        if move["category"] == "Status":
            return 0
            
        power = move["power"]
        
        # 랭크 보정치 테이블 (랭크 -6 ~ +6)
        rank_mult = {
            -6: 2/8, -5: 2/7, -4: 2/6, -3: 2/5, -2: 2/4, -1: 2/3,
             0: 1.0,
             1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0, 5: 3.5, 6: 4.0
        }
        
        if move["category"] == "Physical":
            a_stat = attacker.attack * rank_mult.get(attacker.stat_stages["attack"], 1.0)
            d_stat = defender.defense * rank_mult.get(defender.stat_stages["defense"], 1.0)
        else: # Special
            a_stat = attacker.sp_atk * rank_mult.get(attacker.stat_stages["sp_atk"], 1.0)
            d_stat = defender.sp_def * rank_mult.get(defender.stat_stages["sp_def"], 1.0)
            
        # 1. 기초 데미지 공식 (Level 50 고정)
        # Damage = (((2 * Level / 5 + 2) * Power * A/D) / 50 + 2)
        
        # --- 특성(Ability) 로직 추가 ---
        if defender.ability == "Flash Fire" and move["type"] == "Fire":
            return 0
            
        current_power = power
        if attacker.ability == "Torrent" and move["type"] == "Water":
            if attacker.hp <= (attacker.max_hp / 3):
                current_power *= 1.5
        
        if attacker.ability == "Overgrow" and move["type"] == "Grass":
            if attacker.hp <= (attacker.max_hp / 3):
                current_power *= 1.5
        
        base_damage = (((2 * 50 / 5 + 2) * current_power * a_stat / d_stat) / 50) + 2
        
        # 2. 상성 배율 적용
        type_mod = get_effectiveness(move["type"], defender.types)
        
        # 3. 자속 보정 (STAB: 1.5배)
        stab_mod = 1.5 if move["type"] in attacker.types else 1.0
        
        # 4. 난수 보정 (0.85 ~ 1.0)
        random_mod = random.uniform(0.85, 1.0)
        
        final_damage = int(base_damage * type_mod * stab_mod * random_mod)
        
        return final_damage

    def get_boss_ai_action(self, boss, opponents, turn_count):
        alive_opponents = [p for p in opponents if not p.is_fainted()]
        if not alive_opponents or boss.is_fainted():
            return None
            
        if turn_count == 1:
            return {"attacker": boss, "defender": alive_opponents[0], "move": "Hyper Voice"}
            
        best_moves = [] 
        aoe_moves = []  
        
        for move_name in boss.moves:
            move = MOVES[move_name]
            if move["target"] == "all_opponents":
                aoe_moves.append(move_name)
                
            for target in alive_opponents:
                if target.ability == "Flash Fire" and move["type"] == "Fire":
                    continue
                effectiveness = get_effectiveness(move["type"], target.types)
                if effectiveness >= 2.0:
                    best_moves.append((move_name, target))
                    
        if best_moves:
            chosen_move, chosen_target = random.choice(best_moves)
            return {"attacker": boss, "defender": chosen_target, "move": chosen_move}
            
        valid_aoe = []
        for move_name in aoe_moves:
            can_hit_anyone = False
            move = MOVES[move_name]
            for target in alive_opponents:
                eff = get_effectiveness(move["type"], target.types)
                if target.ability == "Flash Fire" and move["type"] == "Fire":
                    eff = 0
                if eff > 0:
                    can_hit_anyone = True
                    break
            if can_hit_anyone:
                valid_aoe.append(move_name)
                
        if valid_aoe:
            chosen_move = random.choice(valid_aoe)
            return {"attacker": boss, "defender": alive_opponents[0], "move": chosen_move}
            
        chosen_move = random.choice(boss.moves)
        return {"attacker": boss, "defender": alive_opponents[0], "move": chosen_move}

    def execute_turn(self, action_list):
        """
        교체(switch) 액션은 무조건 선제 실행하며,
        그 뒤 기술(move) 액션들을 우선도와 스피드에 따라 정렬하여 실행합니다.
        """
        results = []
        
        # 1. 액션 분류
        switch_actions = [a for a in action_list if a["type"] == "switch"]
        move_actions = [a for a in action_list if a["type"] == "move"]

        # 2. [절대 우선도] 교체 액션 먼저 실행 및 타겟 동적 업데이트
        for s_action in switch_actions:
            slot = s_action["slot"]
            switched_out = s_action.get("switched_out")
            switched_in = s_action["target_poke"]
            
            results.append({
                "type": "switch",
                "slot": slot,
                "target_poke": switched_in,
                "msg": f"{switched_out.ko_name}(이)가 들어가고 {switched_in.ko_name}(이)가 나왔다!"
            })
            
            # [버그 해결 핵심]: 아직 실행되지 않은 대기열 내의 타겟을 업데이트
            for m_action in move_actions:
                # 타겟(defender)이 나간 포켓몬이라면 새로운 포켓몬으로 교체
                if m_action.get("defender") == switched_out:
                    m_action["defender"] = switched_in
                
                # 공격자(attacker)가 나간 포켓몬이라면 해당 턴의 공격 취소 (몬스터볼로 돌아감)
                if m_action.get("attacker") == switched_out:
                    m_action["cancelled"] = True

        # 3. 참여자 상태 초기화 (방어 등)
        # 모든 공격 액션(취소되지 않은)의 공격자와 방어자 상태 초기화
        for m_action in move_actions:
            if not m_action.get("cancelled"):
                m_action["attacker"].is_protecting = False
                m_action["attacker"].is_wide_guarding = False
                if m_action.get("defender"):
                    m_action["defender"].is_protecting = False
                    m_action["defender"].is_wide_guarding = False

        # 4. 공격 액션 정렬 (우선도 -> 스피드)
        def sort_key(action):
            move_name = action['move']
            priority = MOVES[move_name].get('priority', 0)
            speed = action['attacker'].speed
            return (priority, speed)
            
        sorted_moves = sorted(move_actions, key=sort_key, reverse=True)
        action_queue = deque(sorted_moves)
        
        # 5. 공격 액션 실행
        while action_queue:
            action = action_queue.popleft()
            attacker = action['attacker']
            move_name = action['move']
            
            # 취소된 행동(교체되어 들어간 포켓몬)은 건너뜀
            if action.get("cancelled") or attacker.is_fainted():
                continue
                
            move = MOVES[move_name]
            
            # 기술 사용 메시지
            results.append({
                "attacker": attacker.ko_name,
                "defender": "",
                "move": move["ko"],
                "damage": 0,
                "is_hit": True,
                "is_ko": False,
                "msg": f"{attacker.ko_name}의 {move['ko']}!"
            })
            
            # 대상 결정
            targets = []
            if move["target"] == "all_opponents":
                # 현재 살아있는 모든 적군을 대상으로 설정
                potential_targets = []
                for m_act in move_actions:
                    p = m_act["attacker"]
                    # 상대 팀 판별 로직 (보스 vs 플레이어)
                    if not p.is_fainted():
                        if (attacker.name == "Reshiram" and p.name != "Reshiram") or \
                           (attacker.name != "Reshiram" and p.name == "Reshiram"):
                            if p not in potential_targets: potential_targets.append(p)
                targets = sorted(potential_targets, key=lambda x: x.speed, reverse=True)
            elif move["target"] == "self":
                targets = [attacker]
            else: 
                # 단일 타겟 (이미 switch 단계에서 최신화됨)
                if action.get('defender'):
                    targets = [action['defender']]
                else:
                    targets = [attacker]

            for defender in targets:
                # 타겟이 기절했는지 다시 한번 확인
                if defender.is_fainted():
                    continue

                accuracy = move["accuracy"]
                is_hit = random.randint(1, 100) <= accuracy
                damage = 0
                msg = ""
                is_ko = False

                if not is_hit:
                    msg = f"{defender.ko_name}에게는 맞지 않았다!"
                else:
                    if move["category"] == "Status":
                        # (기존 변화기 로직 유지)
                        if move_name == "Protect":
                            attacker.is_protecting = True
                            msg = f"{attacker.ko_name}의 방어! {attacker.ko_name}은(는) 방어 태세에 들어갔다!"
                        elif move_name == "Wide Guard":
                            # 같은 팀 광역 보호 (여기서는 플레이어 파티 vs 보스)
                            # 간소화: 공격자와 같은 진영의 모든 포켓몬 보호
                            # 실제로는 action_list를 통해 같은 편을 찾아야 함
                            for a_p in action_list:
                                if a_p["type"] == "move":
                                    p = a_p["attacker"]
                                    if (attacker.name == "Reshiram" and p.name == "Reshiram") or \
                                       (attacker.name != "Reshiram" and p.name != "Reshiram"):
                                        p.is_wide_guarding = True
                            msg = f"{attacker.ko_name} 측이 광역 공격으로부터 보호받는다!"
                        elif move_name == "Haze":
                            # 초기화 감지 업적
                            boss_reshiram = None
                            for m_act in move_actions:
                                if m_act["attacker"].name == "Reshiram":
                                    boss_reshiram = m_act["attacker"]
                                    break
                            
                            if boss_reshiram:
                                has_stats = any(v > 0 for v in boss_reshiram.stat_stages.values())
                                if has_stats:
                                    ACHIEVEMENTS["haze_reset"] = True
                            
                            msg = "필드의 모든 랭크 변화가 초기화되었다!"
                        elif move_name == "Calm Mind":
                            attacker.stat_stages["sp_atk"] = min(6, attacker.stat_stages["sp_atk"] + 1)
                            attacker.stat_stages["sp_def"] = min(6, attacker.stat_stages["sp_def"] + 1)
                            msg = f"{attacker.ko_name}의 특공과 특방이 올랐다!"
                        elif move_name == "Synthesis":
                            heal_amt = int(attacker.max_hp * 0.5)
                            attacker.hp = min(attacker.max_hp, attacker.hp + heal_amt)
                            msg = f"{attacker.ko_name}은(는) 체력을 회복했다!"
                    else:
                        if defender.is_protecting:
                            msg = f"{defender.ko_name}은(는) 공격으로부터 몸을 지켰다!"
                        elif move["target"] == "all_opponents" and defender.is_wide_guarding:
                            # 방어 감지 업적
                            ACHIEVEMENTS["wide_guard_block"] = True
                            msg = f"{defender.ko_name}이(가) 와이드가드로 광역 공격을 막아냈다!"
                        else:
                            damage = self.calculate_damage(attacker, defender, move_name)
                            if damage == 0:
                                msg = f"{defender.ko_name}에게는 효과가 없는 것 같다.."
                            else:
                                defender.hp = max(0, defender.hp - damage)
                                # 보스 기믹 처리
                                if defender.hp == 0 and defender.name == "Reshiram" and not defender.is_phase_2:
                                    defender.is_phase_2 = True
                                    defender.hp = defender.max_hp
                                    defender.stat_stages["speed"] = 2
                                    is_ko = False
                                    msg = f"{defender.ko_name}에게 {damage}의 데미지!\n레시라무가 에너지를 방출하고 있다!\n레시라무의 모든 상처가 치유되고 스피드가 2단계 올랐다!"
                                else:
                                    is_ko = defender.is_fainted()
                                    # 막타 감지 업적
                                    if is_ko and defender.name == "Reshiram" and attacker.name == "Zekrom":
                                        ACHIEVEMENTS["zekrom_finish"] = True
                                    msg = f"{defender.ko_name}에게 {damage}의 데미지!"

                results.append({
                    "attacker": attacker.ko_name,
                    "defender": defender.ko_name,
                    "move": move["ko"],
                    "damage": damage,
                    "is_hit": is_hit,
                    "is_ko": is_ko,
                    "msg": msg
                })
        
        return results
