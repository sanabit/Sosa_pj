
import random
from collections import deque
from pokemon_types import get_effectiveness
from moves import MOVES
from pokemon import POKEMON

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
        
        # 변화 기술(Status)은 데미지 계산 제외
        if move["category"] == "Status":
            return 0
            
        power = move["power"]
        
        # 공격/방어 유형에 따른 스탯 선택 (Physical vs Special)
        if move["category"] == "Physical":
            a_stat = attacker.attack
            d_stat = defender.defense
        else: # Special
            a_stat = attacker.sp_atk
            d_stat = defender.sp_def
            
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
        행동 리스트를 받아 스피드 순서대로 턴을 처리함
        action_list 형식: [{'attacker': Pokemon 객체, 'defender': Pokemon 객체, 'move': '기술명'}, ...]
        """
        # 1. 스피드 스탯 기준 내림차순 정렬
        sorted_actions = sorted(action_list, key=lambda x: x['attacker'].speed, reverse=True)
        
        # 2. 순서대로 처리하기 위한 큐(Queue) 생성
        action_queue = deque(sorted_actions)
        
        results = []
        
        while action_queue:
            action = action_queue.popleft()
            attacker = action['attacker']
            defender = action['defender']
            move_name = action['move']
            
            # 공격자가 이미 쓰러진 상태라면 행동 스킵
            if attacker.is_fainted():
                continue
            
            # 1. 명중률 계산
            accuracy = MOVES[move_name]["accuracy"]
            is_hit = random.randint(1, 100) <= accuracy
            
            if is_hit:
                # 데미지 계산 및 반영
                damage = self.calculate_damage(attacker, defender, move_name)
                defender.hp = max(0, defender.hp - damage)
            else:
                damage = 0
                hit_text = f"{defender.ko_name}에게는 맞지 않았다 !"
            
            # 결과 저장 (이후 GUI 피드백용)
            turn_info = {
                "attacker": attacker.ko_name,
                "defender": defender.ko_name,
                "move": MOVES[move_name]["ko"],
                "damage": damage,
                "is_hit": is_hit,
                "is_ko": defender.is_fainted()
            }
            results.append(turn_info)
            
            # 테스트를 위한 로그 출력 (추후 Arcade 연동 시 제거 가능)
            print(f"[전투] {attacker.ko_name}의 {MOVES[move_name]['ko']}!")
            print(hit_text)
                
            if is_hit and damage == 0 and MOVES[move_name]["category"] != "Status":
                print(f" -> 효과가 없는 것 같다...")
                
            if defender.is_fainted():
                print(f" -> {defender.ko_name}은(는) 쓰러졌다!")
        
        return results

# 샘플 실행 테스트 코드
if __name__ == "__main__":
    # 데이터 로드 확인 및 객체 생성
    p1 = Pokemon("Primarina")
    p2 = Pokemon("Venusaur")
    boss = Pokemon("Zekrom")
    
    engine = BattleEngine()
    
    # 턴 행동 정의
    sample_actions = [
        {"attacker": p1, "defender": boss, "move": "Moonblast"},
        {"attacker": p2, "defender": boss, "move": "Sludge Bomb"},
        {"attacker": boss, "defender": p1, "move": "Fusion Bolt"}
    ]
    
    print("배틀 시뮬레이션 시작!")
    engine.execute_turn(sample_actions)
