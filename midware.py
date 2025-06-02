import json
import os
import random
import glob
from setting import DEEPSEEK_KEY
from setting import HW_REUQEST_URL
from openai import OpenAI

client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
beaten_monsters = {}
system_prompt = """
你是在一个名字叫做幻境迷宫的游戏中主宰一切的最高意志，无所不能掌握一切生死的神，
请根据提供的怪物的属性和攻击方式，玩家的天赋、武器、装备、技能来决定当前这场战斗的输赢，并给出约200字左右的战斗经过描述，输赢要合乎逻辑，
请写的有趣一些，有奇幻色彩一些,多使用一些图标，把最后表述中的玩家替换为“你”字以便故事更有带入感，请记得你不是玩家，
如果有提供历史战斗信息，请关注，已经损坏或者丢失的物品无法再次使用，主角之前战斗受到的伤害会让当前战斗更加艰难。
"""


# def get_story(current_level):
#     """模拟随机死亡事件，10%概率死亡"""
#     # is_dead = random.random() < 0.1  # 10%死亡概率
#     is_dead = False
#     stories = [
#         "你踩中了古老陷阱，地面突然塌陷！",
#         "神秘的雾气突然笼罩，呼吸变得困难...",
#         "黑暗中传来低吼，一双发亮的眼睛逐渐靠近...",
#         "看似平静的水潭突然伸出触手将你拖入水中！"
#     ]
#     return is_dead, random.choice(stories)


def get_story(current_level):
    is_dead = False
    current_story = ""
    try:
        is_dead, current_story = get_story_description(current_level)
        print(current_story)
        print(f"isdead：{is_dead}")
    except Exception as e:
        print(f"❌连接deepseek失败：{str(e)}")
    finally:
        return is_dead, current_story


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
    fight_history = ""
    for beaten_monster in beaten_monsters.keys():
        fight_history += f"玩家已经经历过的历史战斗：\n"
        fight_history += f"对战怪物：{beaten_monster}\n"
        fight_history += f"对战经过：{beaten_monsters[beaten_monster][1]}\n"

    return select_monster_data['type'], current_player_data, f"""
    怪物的属性如下：\n
    怪物的类型是:{select_monster_data['type']},\n
    怪物的弱点是:{select_monster_data['weakness']},\n
    怪物的免疫属性是:{select_monster_data['immunity']},\n
    怪物的攻击方式是:{"/".join(select_monster_data['attacks'])}.\n
    玩家的属性如下：\n
    玩家的天赋是:{current_player_data['gift']},\n
    玩家的装备是:{current_player_data['equipment']},\n
    玩家的武器是:{current_player_data['weapon']},\n
    玩家的技能1是:{current_player_data['skill1']},\n
    玩家的技能2是:{current_player_data['skill2']},\n
    玩家的技能3是:{current_player_data['skill3']},\n
    玩家的技能4是:{current_player_data['skill4']},\n
    {fight_history}
    """


def get_story_description(current_level):
    global client, system_prompt, beaten_monsters
    current_story = ""
    is_dead = False
    current_monster, current_player_data, user_prompt = get_user_prompt(current_level)
    if current_monster in beaten_monsters.keys():
        if beaten_monsters[current_monster][0] == current_player_data:
            return False, f"🕊️此格没有怪物🕊️\n" \
                          f"  🌈 请享受🌈  "

    print(f"玩家和怪物的信息如下：\n{user_prompt}")
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": f"{system_prompt}"},
                {"role": "user", "content": f"{user_prompt}"},
            ],
            stream=False
        )

        current_story = response.choices[0].message.content
        print(f"✅连接deepseek，成功获取故事")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system",
                 "content": f"你是在一个名字叫做幻境迷宫的游戏中主宰一切的最高意志，无所不能掌握一切生死的神，请你根据描述客观的判断玩家是否死亡，仅用1个字（是或者否）来回答问题"},
                {"role": "user", "content": f"{current_story}"},
            ],
            stream=False
        )
        death_result = response.choices[0].message.content
        print(f"✅连接deepseek，答复:{death_result}")

        if "是" in death_result:
            is_dead = True
        print(f"✅连接deepseek，成功判断玩家是否死亡")
    except Exception as e:
        print(f"❌连接deepseek失败：{str(e)}")
    finally:
        beaten_monsters[current_monster] = [current_player_data, current_story]
        return is_dead, current_story


if __name__ == '__main__':
    get_story(1)
