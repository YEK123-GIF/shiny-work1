from shiny import App, reactive, render, ui

login_ui = ui.page_fillable(
    ui.div(
        ui.card(
            ui.div("🎓 专家评分系统", class_="text-center fs-3 fw-bold mb-3"),

            ui.tags.hr(),

            ui.input_radio_buttons(
                "login_role",
                "登录身份",
                {"judge": "评委登录", "root": "管理员登录"},
                selected="judge",
                inline=True
            ),

            ui.input_text("login_user", "👤 用户名", placeholder="请输入用户名"),
            ui.input_password("login_pass", "🔑 密码", placeholder="请输入密码"),

            ui.input_action_button(
                "login_btn",
                "登录",
                class_="btn btn-success w-100 mt-3"
            ),

            ui.output_text("login_msg"),

            style="padding:30px; border-radius:14px;"
        ),
        style="width:420px; margin:auto; margin-top:70px;"
    )
)