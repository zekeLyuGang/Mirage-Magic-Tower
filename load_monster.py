from datetime import datetime

import gradio as gr
import json
import os


def save_monster(
        monster_type,
        weakness,
        immunity,
        start_level,
        end_level,
        attack1,
        attack2,
        attack3,
        attack4
):
    """保存怪物数据到JSON文件"""
    try:
        if not(1 <= start_level <= 100 and 1 <= end_level <= 100):
            return "楼层必须在1 - 100范围内"
        if start_level > end_level:
            return "起始楼层不能大于终止楼层"
        
        saved_fiels = []
        saved_levels=[]
        # 构建数据字典
        monster_template = {
            "type": monster_type.strip(),
            "weakness": weakness.strip(),
            "immunity": immunity.strip(),
            "attacks": [
                a.strip() for a in [attack1, attack2, attack3, attack4] if a.strip()
            ],
            "create_time": datetime.now().isoformat()
        }
        # 为没个楼层创建怪物文件
        for level in range(int(start_level),int(end_level)+1):
            #复制基础数据并添加楼层信息
            monster_data = monster_template.copy()
            monster_data["level"] = level
            # 创建保存目录
            save_dir = f"monsters/{level}"
            os.makedirs(save_dir, exist_ok=True)
            # 生成文件名（替换特殊字符）
            filename = f"monster_{monster_data['type'].lower().replace(' ', '_')}_level{level}.json"
            filepath = os.path.join(save_dir, filename)

            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(monster_data, f, indent=2, ensure_ascii=False)
            saved_fiels.append(filename)
            saved_levels.append(level)
            level_range = f"[{start_level}-{end_level}]" if start_level != end_level else f"{start_level}"
        return f"✅ 成功保存了{level_range}层的{len(saved_fiels)}个怪物文件"

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
            #楼层范围输入
            with gr.Row():
                start_level = gr.Number(
                    label = "起始楼层",
                    value = 1,
                    precision=0,
                    minimum=1,
                    maximum=100,
                    elem_id="start-level"
                )
                end_level = gr.Number(
                 label="终止楼层",
                    value=1,
                    precision=0,
                    minimum=1,
                    maximum=100,
                    elem_id="end-levle"

                )

        with gr.Column():
            attack1 = gr.Textbox(label="攻击方式 1", placeholder="例如：重击,【超100字自动截断】")
            attack2 = gr.Textbox(label="攻击方式 2", placeholder="例如：冲锋,【超100字自动截断】")
            attack3 = gr.Textbox(label="攻击方式 3", placeholder="例如：眩晕,【超100字自动截断】")
            attack4 = gr.Textbox(label="攻击方式 4", placeholder="例如：横扫,【超100字自动截断】")
    gr.Markdown("💡 提示：指定起始楼层和终止楼层会为范围内每一层创建一个独立的怪物")
    save_btn = gr.Button("💾 保存怪物数据", variant="primary")
    status = gr.Textbox(label="保存状态", interactive=False)

    # 事件绑定
    save_btn.click(
        save_monster,
        inputs=[monster_type, weakness, immunity, start_level,end_level, attack1, attack2, attack3, attack4],
        outputs=status
    )

    for component in [monster_type, weakness, immunity,attack1,attack2,attack3,attack4]:
        component.change(
            fn=lambda x: x[:100],
            inputs=component,
            outputs=component
        )
    def update_end_min(start_level):
        return gr.Number.update(minimum=start_level,Value=start_level)
    
    start_level.change(
        update_end_min,
        inputs=start_level,
        outputs=end_level
    )

if __name__ == "__main__":
    #创建monster目录（如果不存在）
    os.makedirs("monsters",exist_ok=True)
    app.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=8011,  # 指定端口号
    )
