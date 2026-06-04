
# data/moves.py

MOVES = {
    "Sparkling Aria": {
        "ko": "물거품아리아",
        "type": "Water",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "pp": 10,
        "target": "single",
        "description": "The user bursts into song, emitting many bubbles."
    },
    "Protect": {
        "ko": "방어",
        "type": "Normal",
        "category": "Status",
        "power": 0,
        "accuracy": 100,
        "pp": 10,
        "target": "self",
        "priority": 4,
        "description": "Enables the user to evade all attacks. Its chance of failing rises if it is used in succession."
    },
    "Calm Mind": {
        "ko": "명상",
        "type": "Psychic",
        "category": "Status",
        "power": 0,
        "accuracy": 100,
        "pp": 20,
        "target": "self",
        "description": "The user quietly focuses its mind and calms its spirit to raise its Sp. Atk and Sp. Def stats."
    },
    "Moonblast": {
        "ko": "문포스",
        "type": "Fairy",
        "category": "Special",
        "power": 95,
        "accuracy": 100,
        "pp": 15,
        "target": "single",
        "description": "Borrowing the power of the moon, the user attacks the target. This may also lower the target's Sp. Atk stat."
    },
    "Fusion Bolt": {
        "ko": "크로스썬더",
        "type": "Electric",
        "category": "Physical",
        "power": 100,
        "accuracy": 100,
        "pp": 5,
        "target": "single",
        "description": "The user throws down a giant thunderbolt. This move's power is increased if it is used after Fusion Flare."
    },
    "Light Screen": {
        "ko": "빛의 장막",
        "type": "Psychic",
        "category": "Status",
        "power": 0,
        "accuracy": 100,
        "pp": 30,
        "target": "all_allies",
        "description": "A wondrous wall of light is put up to reduce damage from special attacks for five turns."
    },
    "Dragon Claw": {
        "ko": "드래곤클로",
        "type": "Dragon",
        "category": "Physical",
        "power": 80,
        "accuracy": 100,
        "pp": 15,
        "target": "single",
        "description": "The user slashes the target with huge, sharp claws."
    },
    "Haze": {
        "ko": "흑안개",
        "type": "Ice",
        "category": "Status",
        "power": 0,
        "accuracy": 100,
        "pp": 30,
        "target": "all",
        "description": "The user creates a haze that eliminates every stat change among all the Pokémon engaged in battle."
    },
    "Shadow Ball": {
        "ko": "섀도볼",
        "type": "Ghost",
        "category": "Special",
        "power": 80,
        "accuracy": 100,
        "pp": 15,
        "target": "single",
        "description": "The user hurls a shadowy blob at the target. This may also lower the target's Sp. Def stat."
    },
    "Wide Guard": {
        "ko": "와이드 가드",
        "type": "Rock",
        "category": "Status",
        "power": 0,
        "accuracy": 100,
        "pp": 10,
        "target": "all_allies",
        "priority": 3,
        "description": "The user and its allies are protected from wide-ranging attacks for one turn."
    },
    "Flamethrower": {
        "ko": "화염방사",
        "type": "Fire",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "pp": 15,
        "target": "single",
        "description": "The target is scorched with an intense blast of fire. This may also leave the target with a burn."
    },
    "Synthesis": {
        "ko": "광합성",
        "type": "Grass",
        "category": "Status",
        "power": 0,
        "accuracy": 100,
        "pp": 5,
        "target": "self",
        "description": "The user restores its own HP. The amount of HP regained varies with the weather."
    },
    "Sludge Bomb": {
        "ko": "오물폭탄",
        "type": "Poison",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "pp": 10,
        "target": "single",
        "description": "Unsanitary sludge is hurled at the target. This may also poison the target."
    },
    "Energy Ball": {
        "ko": "에너지볼",
        "type": "Grass",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "pp": 10,
        "target": "single",
        "description": "The user draws power from nature and fires it at the target. This may also lower the target's Sp. Def stat."
    },
    "Pollen Puff": {
        "ko": "꽃가루경단",
        "type": "Bug",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "pp": 15,
        "target": "single",
        "description": "The user attacks the enemy with a pollen puff that explodes. If the target is an ally, it gives the ally a pollen puff that restores its HP instead."
    },
    "Blue Flare": {
        "ko": "푸른불꽃",
        "type": "Fire",
        "category": "Special",
        "power": 130,
        "accuracy": 85,
        "pp": 5,
        "target": "single",
        "description": "The user engulfs the target in an intense, yet beautiful, blue flame. This may also leave the target with a burn."
    },
    "Fusion Flare": {
        "ko": "크로스플레임",
        "type": "Fire",
        "category": "Special",
        "power": 100,
        "accuracy": 100,
        "pp": 5,
        "target": "single",
        "description": "The user crashes a giant fireball into the target. This move's power is increased if it is used after Fusion Bolt."
    },
    "Dragon Pulse": {
        "ko": "용의파동",
        "type": "Dragon",
        "category": "Special",
        "power": 85,
        "accuracy": 100,
        "pp": 10,
        "target": "single",
        "description": "The target is attacked with a shock wave generated by the user's gaping mouth."
    },
    "Extrasensory": {
        "ko": "신통력",
        "type": "Psychic",
        "category": "Special",
        "power": 80,
        "accuracy": 100,
        "pp": 20,
        "target": "single",
        "description": "The user attacks with an odd, unseeable power. This may also make the target flinch."
    },
    "Hyper Voice": {
        "ko": "하이퍼보이스",
        "type": "Normal",
        "category": "Special",
        "power": 90,
        "accuracy": 100,
        "pp": 10,
        "target": "all_opponents",
        "description": "The user lets loose a horribly echoing shout with the power to inflict damage."
    },
    "Heat Wave": {
        "ko": "열풍",
        "type": "Fire",
        "category": "Special",
        "power": 95,
        "accuracy": 90,
        "pp": 10,
        "target": "all_opponents",
        "description": "The user attacks by exhaling hot breath on opposing Pokémon. This may also leave those Pokémon with a burn."
    }
}
