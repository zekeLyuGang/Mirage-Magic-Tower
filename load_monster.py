from datetime import datetime
import gradio as gr
import json
import os


def save_monster(
        monster_type,
        description,
        weakness,
        immunity,
        start_level,
        end_level,
        skill1,
        skill2,
        skill3,
        skill4
):
    """保存怪物数据到JSON文件，成功后清空输入框"""
    try:
        # 确保楼层是整数
        start_level = int(start_level)
        end_level = int(end_level)

        # 楼层范围验证
        if not (1 <= start_level <= 100 and 1 <= end_level <= 100):
            return ["楼层必须在1-100范围内"] + [gr.update()] * 9
        if start_level > end_level:
            return ["起始楼层不能大于终止楼层"] + [gr.update()] * 9

        saved_files = []
        # 构建基础怪物数据
        monster_template = {
            "type": monster_type.strip()[:200],
            "description":description.strip()[:200],
            "weakness": weakness.strip()[:200],
            "immunity": immunity.strip()[:200],
            "skills": [
                a.strip()[:200] for a in [skill1, skill2, skill3, skill4] if a.strip()
            ],
            "create_time": datetime.now().isoformat()
        }

        # 为每个楼层创建怪物文件
        for level in range(start_level, end_level + 1):
            # 复制基础数据并添加楼层信息
            monster_data = monster_template.copy()
            monster_data["level"] = f"{start_level}-{end_level}"

            # 创建保存目录
            save_dir = f"monsters/{level}"
            os.makedirs(save_dir, exist_ok=True)

            # 生成文件名（避免特殊字符问题）
            filename = f"monster_{monster_data['type'].lower().replace(' ', '_').replace('/', '_')}_level{level}.json"
            filepath = os.path.join(save_dir, filename)

            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(monster_data, f, indent=2, ensure_ascii=False)
            saved_files.append(filename)

        # 生成成功消息
        level_range = f"{start_level}层" if start_level == end_level else f"{start_level}-{end_level}层"

        # 返回成功消息并清空输入框
        return [
            f"✅ 成功保存了{level_range}的{len(saved_files)}个怪物文件",  # status
            "",  # monster_type
            "",  # description
            "",  # weakness
            "",  # immunity
            start_level,  # start_level
            end_level,  # end_level
            "",  # skill1
            "",  # skill2
            "",  # skill3
            ""  # skill4
        ]

    except ValueError:  # 输入不是有效数值
        return ["❌ 请输入有效的楼层数值(整数)"] + [gr.update()] * 9
    except Exception as e:  # 其他错误
        return [f"❌ 保存失败：{str(e)}"] + [gr.update()] * 9


def update_end_level(start_level_input, current_end_level):
    """更新终止楼层值，确保大于等于起始楼层"""
    try:
        start_level = int(start_level_input)
        current_end_level = int(current_end_level)

        # 确保输入在有效范围内
        if start_level < 1:
            start_level = 1
        if start_level > 100:
            start_level = 100

        # 如果当前结束楼层小于新的起始楼层，则更新
        if current_end_level < start_level:
            return start_level

        return current_end_level
    except:
        return current_end_level


def ensure_integer_input(level_input):
    """确保输入的是整数"""
    try:
        return int(level_input)
    except (ValueError, TypeError):
        return 1


# 界面布局
with gr.Blocks(title="怪物编辑器") as app:
    gr.Markdown("## 🧌 怪物属性编辑器")

    with gr.Row():
        with gr.Column():
            monster_type = gr.Textbox(
                label="种类",
                placeholder="例如：哥布林, 不要超过200字",
                max_length=200
            )
            description = gr.Textbox(
                label="描述",
                placeholder="例如：一种绿皮生物, 不要超过200字",
                max_length=200
            )
            weakness = gr.Textbox(
                label="弱点属性",
                placeholder="例如：火属性, 不要超过200字",
                max_length=200
            )
            immunity = gr.Textbox(
                label="免疫属性",
                placeholder="例如：毒属性, 不要超过200字",
                max_length=200
            )

            # 楼层范围输入
            with gr.Row():
                with gr.Column(min_width=120):
                    start_level = gr.Number(
                        label="起始楼层",
                        value=1,
                        precision=0,
                        minimum=1,
                        maximum=100,
                        elem_id="level-input"
                    )
                with gr.Column(min_width=120):
                    end_level = gr.Number(
                        label="终止楼层",
                        value=1,
                        precision=0,
                        minimum=1,
                        maximum=100,
                        elem_id="level-input"
                    )

        with gr.Column():
            skill1 = gr.Textbox(
                label="技能 1",
                placeholder="例如：重击, 不要超过200字",
                max_length=200
            )
            skill2 = gr.Textbox(
                label="技能 2",
                placeholder="例如：冲锋, 不要超过200字",
                max_length=200
            )
            skill3 = gr.Textbox(
                label="技能 3",
                placeholder="例如：眩晕, 不要超过200字",
                max_length=200
            )
            skill4 = gr.Textbox(
                label="技能 4",
                placeholder="例如：横扫, 不要超过200字",
                max_length=200
            )

    gr.Markdown("💡 提示：指定起始楼层和终止楼层会为范围内每一层创建一个独立的怪物")

    save_btn = gr.Button("💾 保存怪物数据", variant="primary")
    status = gr.Textbox(label="保存状态", interactive=False)

    # 保存按钮事件绑定
    save_btn.click(
        save_monster,
        inputs=[monster_type, description,weakness, immunity, start_level, end_level, skill1, skill2, skill3, skill4],
        outputs=[status, monster_type,description, weakness, immunity, start_level, end_level, skill1, skill2, skill3, skill4]
    )

    # 添加一个清空按钮
    clear_btn = gr.Button("🧹 清空所有输入", variant="secondary")


    # 清空按钮事件绑定
    def clear_form():
        return [
            "输入已清空",  # status
            "",  # monster_type
            "",  # description
            "",  # weakness
            "",  # immunity
            1,  # start_level
            1,  # end_level
            "",  # skill1
            "",  # skill2
            "",  # skill3
            ""  # skill4
        ]


    clear_btn.click(
        clear_form,
        outputs=[status, monster_type,description, weakness, immunity, start_level, end_level, skill1, skill2, skill3, skill4]
    )

    # 楼层输入验证
    start_level.input(
        ensure_integer_input,  # 确保输入的是整数
        inputs=start_level,
        outputs=start_level
    )

    end_level.input(
        ensure_integer_input,  # 确保输入的是整数
        inputs=end_level,
        outputs=end_level
    )

    # 楼层关系更新 - 当起始楼层变化时，确保结束楼层不小于起始楼层
    start_level.input(
        update_end_level,
        inputs=[start_level, end_level],
        outputs=end_level
    )

if __name__ == "__main__":
    # 创建monsters目录（如果不存在）
    os.makedirs("monsters", exist_ok=True)

    # 启动应用
    app.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=8011,  # 指定端口号
        share=False  # 不创建公开链接
    )