from datetime import datetime

import gradio as gr
import json
import os


def save_monster(
        monster_type,
        weakness,
        immunity,
        level,
        attack1,
        attack2,
        attack3,
        attack4
):
    """保存怪物数据到JSON文件"""
    try:
        # 构建数据字典
        monster_data = {
            "type": monster_type.strip(),
            "weakness": weakness.strip(),
            "immunity": immunity.strip(),
            "level": level,
            "attacks": [
                a.strip() for a in [attack1, attack2, attack3, attack4] if a.strip()
            ],
            "create_time": datetime.now().isoformat()
        }
        # 创建保存目录
        save_dir = f"monsters/{level}"
        os.makedirs(save_dir, exist_ok=True)
        # 生成文件名（替换特殊字符）
        filename = f"monster_{monster_data['type'].lower().replace(' ', '_')}.json"
        filepath = os.path.join(save_dir, filename)

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(monster_data, f, indent=2, ensure_ascii=False)

        return f"✅ 保存成功：{filename}"

    except Exception as e:
        return f"❌ 保存失败：{str(e)}"


# 界面布局
with gr.Blocks(title="怪物编辑器") as app:
    gr.Markdown("## 🧌 怪物属性编辑器")

    with gr.Row():
        with gr.Column():
            monster_type = gr.Textbox(label="种类", placeholder="例如：哥布林,【超100字自动截断】")
            weakness = gr.Textbox(label="弱点", placeholder="例如：火属性,【超100字自动截断】")
            immunity = gr.Textbox(label="免疫", placeholder="例如：毒属性,【超100字自动截断】")
            level = gr.Number(label="投放楼层", precision=0, minimum=1, maximum=100)

        with gr.Column():
            attack1 = gr.Textbox(label="攻击方式 1", placeholder="例如：重击,【超100字自动截断】")
            attack2 = gr.Textbox(label="攻击方式 2", placeholder="例如：冲锋,【超100字自动截断】")
            attack3 = gr.Textbox(label="攻击方式 3", placeholder="例如：眩晕,【超100字自动截断】")
            attack4 = gr.Textbox(label="攻击方式 4", placeholder="例如：横扫,【超100字自动截断】")

    save_btn = gr.Button("💾 保存怪物数据", variant="primary")
    status = gr.Textbox(label="保存状态", interactive=False)

    # 事件绑定
    save_btn.click(
        save_monster,
        inputs=[monster_type, weakness, immunity, level, attack1, attack2, attack3, attack4],
        outputs=status
    )

    for component in [monster_type, weakness, immunity,attack1,attack2,attack3,attack4]:
        component.change(
            fn=lambda x: x[:100],
            inputs=component,
            outputs=component
        )

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=8011,  # 指定端口号
    )
