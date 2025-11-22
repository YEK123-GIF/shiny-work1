from shiny import App, reactive, render, ui
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://root:Lzc3219870@localhost:3306/work1?charset=utf8')

def jud_ui():
    # 从DIMENSIONS表获取评分维度列表
    DIMENSIONS = pd.read_sql_table('dimensions', engine)
    dims = list(DIMENSIONS.iloc[0]) if not DIMENSIONS.empty else None
    
    # 生成每个维度的评分滑块（0-10分，步长0.5）
    score_inputs = []
    for i, dim in enumerate(dims):
        score_inputs.append(
            ui.div(
                ui.h5(dim),
                ui.input_slider(
                    id=f"score_{dim}",  # 每个维度的inputId唯一（比如score_技术能力）
                    label=None,
                    min=0,
                    max=10,
                    value=5,  # 默认5分
                    step=0.5,
                    width="100%"
                ),
                class_="mb-3"  # 间距
            )
        )
    
    return  (
            ui.tags.hr(), 
            ui.div(*score_inputs),  # 动态插入所有评分维度控件
            ui.tags.hr(),
        )
    

def res_ui():
    return (
        ui.tags.hr(),
        ui.h4("评分结果"),
        ui.output_data_frame("score_table"),  # 支持列排序
        ui.tags.hr(),
        ui.download_button(
            "download_csv",
            "下载评分表",
            class_="btn btn-success"
        ),
    )

def judger_ui():
    students_df = pd.read_sql("SELECT * FROM students", engine)
    student_choices = [f"{r['id']} （{r['name']})"for _, r in students_df.iterrows()]
    judger_ui = ui.page_fluid(
        ui.layout_sidebar(
            ui.sidebar(
                ui.h3("评分界面"),
                ui.h4(ui.output_text("judger_name")),
                ui.input_selectize(
                    "student", "选择学生",
                    choices=student_choices,
                    multiple=False,
                    options={
                        "placeholder": "输入姓名搜索…",
                        "maxItems": 1,
                        "create": False,  # 禁止用户自建选项
                    },
                ),
                ui.output_ui("student_card"),

                ui.tags.hr(),

                ui.input_radio_buttons(
                    "judge_page",
                    None,
                    {
                        "judge": "评分",
                        "results": "评分结果"
                    },
                    inline=False,
                    selected=None
                ),

                ui.tags.hr(),

                ui.input_action_button(
                    "submit_score",
                    "提交本次评分",
                    class_="btn btn-primary w-100"
                ),
                ui.input_action_button(
                    "logout_btn",
                    "退出登录",
                class_="btn btn-outline-danger w-100"
                )   
            ),
                ui.div(
                ui.card(
                    ui.card_header("评委界面"),
                    ui.output_ui("judge_panel"),  
                    class_="mt-3"
                ),
                class_="p-3"
            )
                 )
    )

    return judger_ui
