import gradio as gr
import numpy as np
import random
import json
import os

from midware import get_story

# 迷宫配置
GRID_SIZE = 8
COLORS = {
    "path": "#FFFFFF", "wall": "#000000",
    "start": "#00FF00", "end": "#FF0000",
    "player": "#0000FF",
    "item": "#FFD700"
}

# 初始化全局状态
initial_maze = None
player_pos = [GRID_SIZE - 1, GRID_SIZE - 1]
item_positions = {}
equipment_data = {
    "gift": "无",
    "equipment": "无",
    "weapon": "无",
    "skill1": "无",
    "skill2": "无",
    "skill3": "无",
    "skill4": "无"
}
floor_completed = False
gift_locked = False
is_dead = False
tower_level = 1


# ----------------- 迷宫生成逻辑 -----------------
def generate_guaranteed_maze():
    global item_positions
    maze = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    start = (GRID_SIZE - 1, GRID_SIZE - 1)
    end = (0, 0)
    maze[start] = 2
    maze[end] = 3

    # 生成保证路径
    path = []
    current = start
    while current != end:
        dx = -1 if current[0] > end[0] else 1 if current[0] < end[0] else 0
        dy = -1 if current[1] > end[1] else 1 if current[1] < end[1] else 0

        if random.random() < 0.8:
            next_cell = (current[0] + dx, current[1]) if dx != 0 else (current[0], current[1] + dy)
        else:
            next_cell = random.choice([
                (current[0] + 1, current[1]),
                (current[0] - 1, current[1]),
                (current[0], current[1] + 1),
                (current[0], current[1] - 1)
            ])

        if 0 <= next_cell[0] < GRID_SIZE and 0 <= next_cell[1] < GRID_SIZE:
            if maze[next_cell] in [0, 3]:
                path.append(next_cell)
                current = next_cell
                if maze[current] != 3:
                    maze[current] = 4

    # 添加障碍
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if maze[i, j] == 0 and random.random() < 0.3:
                maze[i, j] = 1

    # 生成随机物品
    item_positions = {}
    valid_cells = [cell for cell in path if cell not in (start, end)]

    # 装备（0-1）
    if random.random() < 0.5 and valid_cells:
        pos = random.choice(valid_cells)
        maze[pos] = 5
        item_positions[pos] = "equipment"
        valid_cells.remove(pos)

    # 武器（0-1）
    if random.random() < 0.5 and valid_cells:
        pos = random.choice(valid_cells)
        maze[pos] = 5
        item_positions[pos] = "weapon"
        valid_cells.remove(pos)

    # 技能（1-2）
    for _ in range(random.randint(1, 2)):
        if valid_cells:
            pos = random.choice(valid_cells)
            maze[pos] = 5
            item_positions[pos] = f"skill{random.randint(1, 4)}"
            valid_cells.remove(pos)

    return maze


# ----------------- 可视化函数 -----------------
def visualize_maze():
    html = ['<table style="margin: auto; border-collapse: collapse; background: white;">']
    html.append('<caption style="font-size: 1.2em; margin: 10px;"><b>迷宫地图</b></caption>')
    for i in range(GRID_SIZE):
        html.append('<tr>')
        for j in range(GRID_SIZE):
            cell = initial_maze[i, j]
            color = COLORS["path"]
            if (i, j) == tuple(player_pos):
                color = COLORS["player"]
            elif cell == 1:
                color = COLORS["wall"]
            elif cell == 2:
                color = COLORS["start"]
            elif cell == 3:
                color = COLORS["end"]
            elif cell == 5:
                color = COLORS["item"]
            html.append(f'<td style="width: 40px; height: 40px; background: {color}; border: 1px solid #666;"></td>')
        html.append('</tr>')
    html.append('</table>')
    return ''.join(html)


# ----------------- 游戏逻辑 -----------------

def move_player(direction):
    global player_pos, floor_completed, gift_locked, is_dead
    if is_dead:  # 如果已经死亡，阻止移动
        return visualize_maze(), "你已阵亡，请重新开始！", *[gr.update(interactive=False)] * 7, gr.update(
            interactive=False)

    old_i, old_j = player_pos
    new_i, new_j = old_i, old_j

    if direction == "forward":
        new_i -= 1
    elif direction == "back":
        new_i += 1
    elif direction == "left":
        new_j -= 1
    elif direction == "right":
        new_j += 1

    message = ""
    updates = {
        "gift": gr.update(interactive=not gift_locked),
        "equipment": gr.update(interactive=False),
        "weapon": gr.update(interactive=False),
        "skill1": gr.update(interactive=False),
        "skill2": gr.update(interactive=False),
        "skill3": gr.update(interactive=False),
        "skill4": gr.update(interactive=False),
    }
    newmap_btn_state = gr.update(interactive=False)

    # 新增死亡判断
    current_pos = (new_i, new_j)
    if current_pos not in [(GRID_SIZE - 1, GRID_SIZE - 1), (0, 0)]:
        dead, story = get_story(tower_level)
        if dead:
            is_dead = True
            message += f"\n💀 遭遇不幸:｛story｝"
            # 删除装备文件
            if os.path.exists("equipment.json"):
                os.remove("equipment.json")
            # 禁用所有按钮（除了重置按钮）
            return (
                visualize_maze(),
                message,
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False),
                gr.update(interactive=False)
            )
        else:
            message += f"\n⚔️ 遭遇战斗："
        message += f"{story}\n"
    if 0 <= new_i < GRID_SIZE and 0 <= new_j < GRID_SIZE:
        if initial_maze[new_i, new_j] != 1:
            player_pos[0], player_pos[1] = new_i, new_j
            current_pos = (new_i, new_j)

            # 检查物品收集
            if current_pos in item_positions:
                item_type = item_positions[current_pos]
                if item_type in updates:
                    updates[item_type] = gr.update(interactive=True)
                message += f"🎁 获得{item_type}！"

    # 检查终点
    if tuple(player_pos) == (0, 0):
        message = "🎉 成功抵达出口！"
        floor_completed = True
        newmap_btn_state = gr.update(interactive=True)

    return (
        visualize_maze(),
        message,
        updates["gift"],
        updates["equipment"],
        updates["weapon"],
        updates["skill1"],
        updates["skill2"],
        updates["skill3"],
        updates["skill4"],
        newmap_btn_state
    )


def reset_game():
    global player_pos, floor_completed, gift_locked, equipment_data, initial_maze, is_dead,tower_level
    # 在一楼复活
    is_dead = False
    tower_level = 1
    new_title = f"# 🏰 幻境魔塔第{tower_level}层"
    # 清空保存文件
    if os.path.exists("equipment.json"):
        os.remove("equipment.json")
    # 重置状态
    initial_maze = generate_guaranteed_maze()
    player_pos = [GRID_SIZE - 1, GRID_SIZE - 1]
    floor_completed = False
    gift_locked = False
    equipment_data = {k: "" for k in equipment_data}
    return (
        visualize_maze(),
        "",
        gr.update(value="", interactive=True),
        gr.update(value="", interactive=False),
        gr.update(value="", interactive=False),
        gr.update(value="", interactive=False),
        gr.update(value="", interactive=False),
        gr.update(value="", interactive=False),
        gr.update(value="", interactive=False),
        gr.update(interactive=False),
        new_title
    )


def new_map():
    global initial_maze, floor_completed, player_pos, tower_level
    player_pos = [GRID_SIZE - 1, GRID_SIZE - 1]
    initial_maze = generate_guaranteed_maze()
    floor_completed = False
    tower_level = min(tower_level + 1, 100)
    new_title = f"# 🏰 幻境魔塔第{tower_level}层"
    original_outputs = move_player("")
    return original_outputs + (new_title,)


# ----------------- 装备系统 -----------------
def save_equipment(gift, equipment, weapon, s1, s2, s3, s4):
    global gift_locked
    equipment_data.update({
        "gift": gift[:100],
        "equipment": equipment[:100],
        "weapon": weapon[:100],
        "skill1": s1[:100],
        "skill2": s2[:100],
        "skill3": s3[:100],
        "skill4": s4[:100]
    })
    with open("equipment.json", "w") as f:
        json.dump(equipment_data, f)
    gift_locked = True
    return "✅ 装备保存成功！", gr.update(interactive=False)


def load_equipment():
    try:
        with open("equipment.json") as f:
            data = json.load(f)
            return [
                data["gift"],
                data["equipment"],
                data["weapon"],
                data["skill1"],
                data["skill2"],
                data["skill3"],
                data["skill4"],
                gr.update(interactive=False),
                gr.update(interactive=False)
            ]
    except:
        return ["", "", "", "", "", "", "", gr.update(interactive=True), gr.update(interactive=False)]


# ----------------- 界面构建 -----------------
with gr.Blocks() as demo:
    title = gr.Markdown(f"# 🏰 幻境魔塔第{tower_level}层")

    with gr.Row():
        map_display = gr.HTML()
        status = gr.Textbox(label="游戏状态", interactive=False)

    with gr.Row():
        forward_btn = gr.Button("⬆️ 向前")
        back_btn = gr.Button("⬇️ 向后")
        left_btn = gr.Button("⬅️ 向左")
        right_btn = gr.Button("➡️ 向右")

    with gr.Row():
        reset_btn = gr.Button("🔄 再来一次")
        newmap_btn = gr.Button("下个地图", interactive=False)

    with gr.Row():
        with gr.Column():
            gift = gr.Textbox(label="天赋【超100字自动截断】", placeholder="无")
            equip = gr.Textbox(label="装备【超100字自动截断】", placeholder="无", interactive=False)
            weapon = gr.Textbox(label="武器【超100字自动截断】", placeholder="无", interactive=False)
        with gr.Column():
            s1 = gr.Textbox(label="技能1【超100字自动截断】", placeholder="无", interactive=False)
            s2 = gr.Textbox(label="技能2【超100字自动截断】", placeholder="无", interactive=False)
            s3 = gr.Textbox(label="技能3【超100字自动截断】", placeholder="无", interactive=False)
            s4 = gr.Textbox(label="技能4【超100字自动截断】", placeholder="无", interactive=False)

    save_btn = gr.Button("💾 保存装备")
    save_status = gr.Textbox(label="保存状态", interactive=False)

    # 事件绑定
    move_outputs = [
        map_display, status,
        gift, equip, weapon,
        s1, s2, s3, s4,
        newmap_btn
    ]

    # 方向按钮事件绑定
    for btn, direction in [(forward_btn, "forward"),
                           (back_btn, "back"),
                           (left_btn, "left"),
                           (right_btn, "right")]:
        btn.click(
            lambda d=direction: move_player(d),
            outputs=move_outputs
        )

    reset_btn.click(
        reset_game,
        outputs=move_outputs+ [title]
    )

    newmap_btn.click(
        new_map,
        outputs=move_outputs + [title]
    )

    save_btn.click(
        save_equipment,
        inputs=[gift, equip, weapon, s1, s2, s3, s4],
        outputs=[save_status, gift]
    )

    demo.load(
        lambda: [visualize_maze(), *load_equipment()],
        outputs=[map_display, gift, equip, weapon, s1, s2, s3, s4, newmap_btn, gift]
    )

if __name__ == "__main__":
    initial_maze = generate_guaranteed_maze()
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=8010,  # 指定端口号
    )
