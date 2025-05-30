import json
import os
import random
import glob

import requests

HW_REUQEST_URL = "http://9.118.27.189:8015/common_chat/"

system_prompt = """
你是在一个名字叫做幻境迷宫的游戏中主宰一切的最高意志，无所不能掌握一切生死的神，
请根据提供的怪物的属性和攻击方式，玩家的天赋、武器、装备、技能来决定当前这场战斗的输赢，并给出约200字左右的战斗经过描述，输赢要合乎逻辑。
请写的有趣一些，有奇幻色彩一些。
"""


def get_story():
    """模拟随机死亡事件，10%概率死亡"""
    # is_dead = random.random() < 0.1  # 10%死亡概率
    is_dead = False
    stories = [
        "你踩中了古老陷阱，地面突然塌陷！",
        "神秘的雾气突然笼罩，呼吸变得困难...",
        "黑暗中传来低吼，一双发亮的眼睛逐渐靠近...",
        "看似平静的水潭突然伸出触手将你拖入水中！"
    ]
    return is_dead, random.choice(stories)


def get_user_prompt(level: int):
    """随机抽取当前level下的所有怪物，逢5的倍数层只抽取当层怪物"""
    select_level = min(random.randint(1, level), 100)
    if level % 5 == 0:
        select_level = min(level, 100)
    monsters_lib_path = f"monsters{os.sep}{select_level}{os.sep}*"
    monsters_file = glob.glob(monsters_lib_path)
    select_monster = random.choice(monsters_file)
    with open(select_monster, 'r', encoding='utf-8') as f:
        select_monster_data = json.load(f)
    with open("equipment.json", "r", encoding='utf-8') as f:
        current_player_data = json.load(f)

    return f"""
    怪物的属性如下：
    怪物的类型是{select_monster_data['type']},
    怪物的弱点是{select_monster_data['weakness']},
    怪物的免疫属性是{select_monster_data['immunity']},
    怪物的攻击方式是\n{"/".join(select_monster_data['attacks'])}.
    玩家的属性如下：
    玩家的天赋是{current_player_data['gift']},
    玩家的装备是{current_player_data['equipment']},
    玩家的武器是{current_player_data['weapon']},
    玩家的技能1是{current_player_data['skill1']},
    玩家的技能2是{current_player_data['skill2']},
    玩家的技能3是{current_player_data['skill3']},
    玩家的技能4是{current_player_data['skill4']},
    """


def test():
    global system_prompt
    request_data = {
        "system_prompt": system_prompt,
        "query": get_user_prompt(1)
    }

    response = requests.post(
        HW_REUQEST_URL,
        json=request_data,
        timeout=30
    )
    print(response.json())


if __name__ == '__main__':
    test()
