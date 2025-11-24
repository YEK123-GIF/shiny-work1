from shiny import App, reactive, render, ui

def show_ui():
    return ui.layout_columns(
        ui.card(
            ui.card_header("评分分布"),

            ui.input_select(
                "plot_student",
                "选择学生",
                choices=[],   
            ),

            ui.output_plot("score_diff_plot", height="400px"),

            ui.download_button(
                    "download_pdf",
                    "下载",
                    class_="btn btn-sm btn-outline-primary"
            )
            
        ),

        ui.card(
            ui.card_header("评分表"),
            ui.tags.hr(),
            ui.output_data_frame("score_table_for_root"),  
            ui.tags.hr(),
            ui.download_button(
                "download_csv_root",
                "下载",
             class_="btn btn-sm btn-outline-primary"
                )
            )  
    )

def manage_ui():
    return ui.layout_columns(
        ui.card(
            ui.card_header("评分维度管理"),

            ui.tags.p("当前系统中的评分维度: ", class_="text-muted"),
            ui.output_data_frame("dims_table"),  

            ui.tags.hr(),

            ui.h5("新增评分维度"),
            ui.input_text("new_dim_name", "维度名称"),
            ui.input_action_button(
                "add_dim_btn",
                "添加维度",
                class_="btn btn-sm btn-primary mt-2"
            ),

            ui.tags.hr(),

            ui.h5("删除评分维度"),
            ui.output_ui("dim_delete_ui"), 
        ),

        ui.card(
            ui.card_header("评委账号管理"),

            ui.tags.p("当前已注册评委: ", class_="text-muted"),
            ui.output_data_frame("judges_table"),  

            ui.tags.hr(),

            ui.h5("新增评委账号"),
            ui.input_text("new_judge_user", "评委用户名"),
            ui.input_password("new_judge_pwd", "初始密码"),
            ui.input_action_button(
                "add_judge_btn",
                "添加评委",
                class_="btn btn-sm btn-primary mt-2"
            ),

            ui.tags.hr(),

            ui.h5("删除评委账号"),
            ui.output_ui("judge_delete_ui"), 
        )
    )
def history_ui():
    return ui.output_data_frame("history_table")

root_ui = ui.page_fillable(
    ui.layout_sidebar(
        ui.sidebar(
            ui.div(
                "管理员操作界面",
                class_="fs-4 fw-bold mb-3"
            ),

            ui.input_radio_buttons(
                "root_page",
                "功能菜单",
                {
                    "show": "查看评分汇总分析",
                    "manage": "管理",
                    "history": "历史记录",
                },
                selected=None,
                inline=False
            ),

            ui.tags.hr(),

            ui.tags.small("学生名单管理", class_="text-muted"),
            ui.input_file(
                "upload_file",
                "上传学生名单(CSV / Excel)",
                accept=[".csv", ".xlsx"],
                multiple=False,
            ),

            ui.div(class_="mb-3"),  

            ui.tags.hr(),

            ui.input_action_button(
                "logout_btn",
                "退出登录",
                class_="btn btn-outline-danger w-100"
            ),

            width=260  
        ),

        ui.div(
            ui.card(
                ui.card_header("管理员工作台"),
                ui.output_ui("root_panel"),  
                class_="mt-3"
            ),
            class_="p-3"
        )
    )
)