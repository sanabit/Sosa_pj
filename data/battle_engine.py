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

    def _calc_hp(self, base):
        # 본가 HP 계산 공식: ((Base*2 + IV + EV/4) * Level / 100) + Level + 10
        return int((base * 2 + 31) * self.level / 100 + self.level + 10)

    def _calc_stat(self, base):
        # 본가 일반 능력치 계산 공식: (((Base*2 + IV + EV/4) * Level / 100) + 5) * Nature
        return int((base * 2 + 31) * self.level / 100 + 5)

    def is_fainted(self):
        return self.hp <= 0
    #기절했니? 라는 뜻

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
        # 2/8, 2/7, 2/6, 2/5, 2/4, 2/3, 2/2, 3/2, 4/2, 5/2, 6/2, 7/2, 8/2
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
        
        # [방어자 특성] 타오르는 불꽃 (Flash Fire): 불꽃 타입 공격 무효화
        if defender.ability == "Flash Fire" and move["type"] == "Fire":
            return 0
            
        # [공격자 특성] 급류 (Torrent): HP가 1/3 이하일 때 물 타입 위력 1.5배
        current_power = power
        if attacker.ability == "Torrent" and move["type"] == "Water":
            if attacker.hp <= (attacker.max_hp / 3):
                current_power *= 1.5
        
        # [공격자 특성] 심록 (Overgrow): HP가 1/3 이하일 때 풀 타입 위력 1.5배
        if attacker.ability == "Overgrow" and move["type"] == "Grass":
            if attacker.hp <= (attacker.max_hp / 3):
                current_power *= 1.5
        
        # ----------------------------

        base_damage = (((2 * 50 / 5 + 2) * current_power * a_stat / d_stat) / 50) + 2
        
        # 2. 상성 배율 적용 (types.py 활용)
        type_mod = get_effectiveness(move["type"], defender.types)
        
        # 3. 자속 보정 (STAB: Same Type Attack Bonus, 1.5배)
        stab_mod = 1.5 if move["type"] in attacker.types else 1.0
        
        # 4. 난수 보정 (Random Roll: 0.85 ~ 1.0)
        random_mod = random.uniform(0.85, 1.0)
        
        # 모든 보정치를 곱하여 최종 데미지 정수형 반환
        final_damage = int(base_damage * type_mod * stab_mod * random_mod)
        
        return final_damage

    def execute_turn(self, action_list):
        """
        행동 리스트를 받아 우선도와 스피드 순서대로 턴을 처리함
        action_list 형식: [{'attacker': Pokemon 객체, 'defender': Pokemon 객체, 'move': '기술명'}, ...]
        """
        # 1. 모든 참여자 상태 리셋
        participants = set()
        for action in action_list:
            participants.add(action['attacker'])
            if action.get('defender'):
                participants.add(action['defender'])
        
        for p in participants:
            p.is_protecting = False
            p.is_wide_guarding = False

        # 2. 우선도 및 스피드 기준 정렬
        def sort_key(action):
            move_name = action['move']
            priority = MOVES[move_name].get('priority', 0)
            speed = action['attacker'].speed
            return (priority, speed)
            
        sorted_actions = sorted(action_list, key=sort_key, reverse=True)
        action_queue = deque(sorted_actions)
        results = []
        
        while action_queue:
            action = action_queue.popleft()
            attacker = action['attacker']
            move_name = action['move']
            
            if attacker.is_fainted():
                continue
                
            move = MOVES[move_name]
            
            # 기술 사용 선언 (로그의 첫 줄)
            results.append({
                "attacker": attacker.ko_name,
                "defender": "",
                "move": move["ko"],
                "damage": 0,
                "is_hit": True,
                "is_ko": False,
                "msg": f"{attacker.ko_name}의 {move['ko']}!"
            })
            
            # 타겟 수집
            targets = []
            if move["target"] == "all_opponents":
                for p in participants:
                    if p != attacker and not p.is_fainted():
                        if (attacker.name == "Reshiram" and p.name != "Reshiram") or \
                           (attacker.name != "Reshiram" and p.name == "Reshiram"):
                            targets.append(p)
                targets.sort(key=lambda x: x.speed, reverse=True)
            elif move["target"] == "self":
                targets = [attacker]
            elif move["target"] == "all":
                targets = list(participants)
                targets.sort(key=lambda x: x.speed, reverse=True)
            else: # single or others
                if action.get('defender'):
                    targets = [action['defender']]
                else:
                    targets = [attacker]

            # 각 타겟에 대해 효과 적용
            for defender in targets:
                if defender.is_fainted() and move["target"] != "all":
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
                        if move_name == "Protect":
                            attacker.is_protecting = True
                            msg = f"{attacker.ko_name}은(는) 방어 태세에 들어갔다!"
                        elif move_name == "Wide Guard":
                            for p in participants:
                                if (attacker.name == "Reshiram" and p.name == "Reshiram") or \
                                   (attacker.name != "Reshiram" and p.name != "Reshiram"):
                                    p.is_wide_guarding = True
                            msg = f"{attacker.ko_name} 측이 광역 공격으로부터 보호받는다!"
                        elif move_name == "Haze":
                            for p in participants:
                                for stat in p.stat_stages:
                                    p.stat_stages[stat] = 0
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
                        # 공격기
                        if defender.is_protecting:
                            msg = f"{defender.ko_name}은(는) 공격으로부터 몸을 지켰다!"
                        elif move["target"] == "all_opponents" and defender.is_wide_guarding:
                            msg = f"{defender.ko_name}이(가) 와이드가드로 광역 공격을 막아냈다!"
                        else:
                            damage = self.calculate_damage(attacker, defender, move_name)
                            defender.hp = max(0, defender.hp - damage)
                            is_ko = defender.is_fainted()
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
