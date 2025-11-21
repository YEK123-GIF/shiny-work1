from shiny import App, reactive, render, ui
import pandas as pd
from sqlalchemy import create_engine
from root_ui import *
from judger_ui import *
from login_ui import *
import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "SimSun"]
matplotlib.rcParams["axes.unicode_minus"] = False

engine = create_engine('mysql+pymysql://root:Lzc3219870@localhost:3306/work1?charset=utf8')

DIMENSIONS = pd.read_sql_table('dimensions', engine)
judger_df = pd.read_sql_table('judger', engine)
root_df = pd.read_sql_table('root', engine)
history_df = pd.read_sql_table('history', engine)
grades_df = pd.read_sql_table('grades', engine)

def server(input, output, session):
    logged_in = reactive.Value(False)
    current_user = reactive.Value("")
    login_msg_text = reactive.Value("")
    login_role_store = reactive.Value("judge")

    dims_store = reactive.Value(DIMENSIONS.copy())
    judges_store = reactive.Value(judger_df.copy()) #让shiny自动追踪reactive值
    history_store = reactive.Value(history_df.copy())
    grades_store = reactive.Value(grades_df.copy())

    @output
    @render.text
    def login_msg():
        return login_msg_text()

    @reactive.Effect
    @reactive.event(input.login_btn)
    def do_login():
        role = input.login_role()
        u = (input.login_user() or "").strip()
        p = (input.login_pass() or "")

        if role == "judge":
            row = judger_df.loc[judger_df["name"] == u]
        else:
            row = root_df.loc[root_df["name"] == u]

        if row.empty:
            login_msg_text.set("用户名不存在")
            return

        real_pwd = str(row.iloc[0]["password"])
        if real_pwd != p:
            login_msg_text.set("密码错误")
            return

        logged_in.set(True)
        current_user.set(u)
        login_msg_text.set("")
        login_role_store.set(input.login_role())

        who = "评委" if role == "judge" else "管理员"
        ui.notification_show(f"欢迎，{u}（{who}）！", type="message")

    @reactive.Effect
    @reactive.event(input.logout_btn)
    def do_logout():
        logged_in.set(False)
        current_user.set("")
        ui.notification_show("已退出登录", type="message")
        login_role_store.set("judge")
    
    @reactive.Effect
    @reactive.event(input.submit_score)
    def do_submit():

        try:
            current_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") #时间
            current_sid = (input.student() or "").strip().split()[0] #学生编号

            s = (input.student() or "").strip().split()[1]
            student_name = s[1:-1] #学生姓名
            judger_name = str(current_user()) #评委姓名

            # 1. 获取评分维度列表（处理 dims 为 None 的情况）
            dims = list(DIMENSIONS.iloc[0]) if (not DIMENSIONS.empty and DIMENSIONS.iloc[0] is not None) else []
    
            # 2. 遍历维度读取分数，转为整数（存储为字典：维度名 -> 整数分数）
            scores = {}
            for dim in dims:
                # 读取滑块值（默认返回 float，如 5.0、8.5）
                score = input[f"score_{dim}"]()  
        
                # 处理空值/异常值
                if score is None:
                    score = 0.0  # 空值默认0分
        
                scores[dim] = score
            
            total_score = sum(scores.values())
        
            score_data = {
                "候选人": student_name,
                "评审人": judger_name,
                "评审时间": current_time,
                "总分": total_score,
                **scores
            }
        
            insert_df = pd.DataFrame([score_data])
            
            from sqlalchemy import text
            with engine.begin() as conn:
            # 删除同一评审人+候选人的旧记录
                conn.execute(
                    text("""
                    DELETE FROM history
                    WHERE 候选人 = :student_name
                      AND 评审人 = :judger_name
                """),
                    {"student_name": student_name, "judger_name": judger_name}
                )

            insert_df.to_sql(
                name="history",  
                con=engine,     
                if_exists="append",  
                index=False,    
                chunksize=1000
            )

            ui.notification_show("提交成功", type="message")
        except:
            ui.notification_show("提交失败", type="warning")

    @output
    @render.ui
    def root_panel():
        page = input.root_page() or "blank"

        if page == "blank":
            return ui.card("欢迎登录") #默认空白显示

        elif page == "show":
            return show_ui()

        elif page == "manage":
            return manage_ui()

        elif page == "history":
            return history_ui()

    @output
    @render.ui
    def judge_panel():
        page = input.judge_page() or "blank"

        if page == "blank":
            return ui.card("欢迎登录")  # 默认空白显示

        if page == "judge":
            return jud_ui()
        
        if page == "results":
            return res_ui()

    @output
    @render.ui
    def page():
        if not logged_in():
            return login_ui

        role = login_role_store()
        if role == "root":
            return root_ui
        else:
            return judger_ui

    @output
    @render.text
    def judger_name():
        return f"当前用户: {current_user()}"

    @output
    @render.ui
    def student_card():
        sid = (input.student() or "").strip().split()[0]
        if not sid:
            return ui.div("未选择学生")
        students_df = pd.read_sql("SELECT * FROM students", engine) #student_card() 是一个 reactive 输出（用了 @output + @render.ui） 它依赖的 输入 input.student() 发生变化 或者其他它使用的 reactive 内容变化（比如数据库数据 如果你每次都重新查询） 它就 会自动重新执行并刷新 UI。
        row = students_df.loc[students_df["id"] == sid]
        if row.empty:
            return ui.div("未找到该学生")
        r = row.iloc[0]
        return ui.card(
            ui.card_header(f"已选学生：{r['name']}"),
            ui.tags.ul(
                ui.tags.li(f"学号：{r['id']}"),
                ui.tags.li(f"专业：{r['major']}"),
                ui.tags.li(f"年级：{r['grade']}"),
            )
        )
    
    
    @output
    @render.data_frame
    def score_table():
        df = pd.read_sql(f"SELECT 候选人, 专业基础知识, 逻辑思维能力, 科研潜力, 沟通与表达能力, 综合素质, 总分 FROM history WHERE 评审人='{current_user()}'", engine)
        return df
    
    @output
    @render.data_frame
    def score_table_for_root():
        student = input.plot_student()
        df = pd.read_sql(f"SELECT 评审人, 候选人, 专业基础知识, 逻辑思维能力, 科研潜力, 沟通与表达能力, 综合素质, 总分 FROM history WHERE 候选人='{student}'", engine)
        return df
    

    @output
    @render.image
    def judeger_show_image():
        pass

    @render.download(filename="scores.csv")
    def download_csv():
        # 读取数据库里的评分记录
        df = pd.read_sql(f"SELECT 候选人, 专业基础知识, 逻辑思维能力, 科研潜力, 沟通与表达能力, 综合素质, 总分 FROM history WHERE 评审人='{current_user()}'", engine)

        # 返回文本（str），Shiny 会作为文件内容
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        yield csv_data
    
    @render.download(filename="scores.csv")
    def download_csv_root():
        student = input.plot_student()
        df = pd.read_sql(f"SELECT 评审人, 候选人, 专业基础知识, 逻辑思维能力, 科研潜力, 沟通与表达能力, 综合素质, 总分 FROM history WHERE 候选人='{student}'", engine)

        # 返回文本（str），Shiny 会作为文件内容
        csv_data = df.to_csv(index=False, encoding="utf-8-sig")
        yield csv_data

    @reactive.Effect
    @reactive.event(input.upload_file)
    def _load_students_from_upload():

        files = input.upload_file()

        if not files:
            return

        file_info = files[0]
        filepath = file_info["datapath"]  # 临时文件路径
        filename = file_info["name"].lower()

        if filename.endswith(".csv"):
            try:
                 students = pd.read_csv(filepath)
            except Exception as e:
                ui.notification_show(f"CSV 文件无法读取：{e}", type="error")
                return

        elif filename.endswith(".xlsx"):
            try:
                students = pd.read_excel(filepath)
            except Exception as e:
                ui.notification_show(f"Excel 文件无法读取：{e}", type="error")
                return

        else:
            ui.notification_show("❌ 仅支持上传 CSV 或 Excel 文件！", type="error")
            return

        students.to_sql("students", engine, if_exists="replace", index=False)
        ui.notification_show("✔ 学生名单上传成功！", type="message")

    @output
    @render.data_frame
    def history_table():
       return history_store()

    # --------- 评分维度表格 ----------
    @output
    @render.data_frame
    def dims_table():
        dims = pd.DataFrame({"评分维度": list(dims_store().iloc[0])})
        return dims

    # --------- 评委表格 ----------
    @output
    @render.data_frame
    def judges_table():
        return judges_store()

    # --------- 评分表格 ----------
    @output
    @render.data_frame
    def grades_table():
        return grades_store()

    # --------- 删除维度用的下拉框 ----------
    @output
    @render.ui
    def dim_delete_ui():
        dims = list(dims_store().iloc[0])
        if not dims:
            return ui.div("当前没有任何评分维度", class_="text-muted")

        return ui.layout_columns(
            ui.input_select(
                "del_dim_name",
                "选择要删除的维度",
                choices=dims,
                multiple=False,
            ),
            ui.input_action_button(
                "del_dim_btn",
                "删除选中维度",
                class_="btn btn-sm btn-danger mt-2"
            )
        )

    # --------- 删除评委用的下拉框 ----------
    @output
    @render.ui
    def judge_delete_ui():
        df = judges_store()
        if df.empty:
            return ui.div("当前没有任何评委账号", class_="text-muted")

        # 用用户名做选项
        choices = list(df["name"])
        return ui.layout_columns(
            ui.input_select(
                "del_judge_user",
                "选择要删除的评委",
                choices=choices,
                multiple=False,
            ),
            ui.input_action_button(
                "del_judge_btn",
                "删除选中评委",
                class_="btn btn-sm btn-danger mt-2"
            )
        )

    # ------- 添加评分维度 -------
    @reactive.Effect
    @reactive.event(input.add_dim_btn)
    def _add_dim():
        global DIMENSIONS
        name = (input.new_dim_name() or "").strip()
        if not name:
            ui.notification_show("请先输入维度名称", type="warning")
            return

        dims = list(DIMENSIONS.iloc[0])
        if name in dims:
            ui.notification_show("该维度已存在！", type="warning")
            return

        dims.append(name)
        DIMENSIONS[len(DIMENSIONS.columns)] = name
        DIMENSIONS.columns = list(range(DIMENSIONS.shape[1]))
        DIMENSIONS.to_sql(name="dimensions", con=engine, if_exists='replace', index=False)
        dims_store.set(DIMENSIONS.copy())
        ui.notification_show(f"已添加评分维度：{name}", type="message")

        # 清空输入框
        ui.update_text("new_dim_name", value="")

    # ------- 删除评分维度 -------
    @reactive.Effect
    @reactive.event(input.del_dim_btn)
    def _del_dim():
        global DIMENSIONS
        name = input.del_dim_name()
        if not name:
            ui.notification_show("请选择要删除的维度", type="warning")
            return

        # 找到该列编号
        col_index = DIMENSIONS.iloc[0].tolist().index(name)
        col_name = DIMENSIONS.columns[col_index]

        # 删除该列
        DIMENSIONS = DIMENSIONS.drop(columns=[col_name])
        DIMENSIONS.columns = list(range(DIMENSIONS.shape[1]))
        DIMENSIONS.to_sql(name="dimensions", con=engine, if_exists='replace', index=False)
        dims_store.set(DIMENSIONS.copy())

        ui.notification_show(f"已删除评分维度：{name}", type="message")

    # ------- 添加评委 -------
    @reactive.Effect
    @reactive.event(input.add_judge_btn)
    def _add_judge():
        global judger_df
        user = (input.new_judge_user() or "").strip()
        pwd = (input.new_judge_pwd() or "").strip()

        if not user or not pwd:
            ui.notification_show("请填写评委用户名和密码", type="warning")
            return

        df = judger_df
        if not df[df["name"] == user].empty:
            ui.notification_show("该评委用户名已存在！", type="warning")
            return

        new_row = pd.DataFrame([{
            "id": f"T{len(df) + 1:03d}",
            "name": user,
            "password": pwd,
        }])

        judger_df = pd.concat([df, new_row], ignore_index=True)
        judger_df.to_sql(name="judger", con=engine, if_exists='replace', index=False)
        judges_store.set(judger_df.copy())

        ui.notification_show(f"已添加评委：{user}", type="message")

        ui.update_text("new_judge_user", value="")
        ui.update_text("new_judge_pwd", value="")

    # ------- 删除评委 -------
    @reactive.Effect
    @reactive.event(input.del_judge_btn)
    def _del_judge():
        global judger_df
        user = input.del_judge_user()
        if not user:
            ui.notification_show("请选择要删除的评委", type="warning")
            return

        judger_df = judger_df[judger_df["name"] != user].reset_index(drop=True)
        judger_df.to_sql(name="judger", con=engine, if_exists='replace', index=False)
        judges_store.set(judger_df.copy())

        ui.notification_show(f"已删除评委：{user}", type="message")
    
    @reactive.Effect
    def _update_student_choices():
        # 让 effect 对 root_page 有依赖，这样每次切换功能菜单都会重新执行
        page = input.root_page()

        # 只有在“查看评分汇总分析”页面时才更新下拉框
        if page != "show":
            return

        df = pd.read_sql("SELECT DISTINCT 候选人 FROM history", engine)

        students = df["候选人"].tolist() if not df.empty else []

        ui.update_select(
            "plot_student",
            choices=students,
            selected=students[0] if students else None,
    )

    @render.plot
    def score_diff_plot():
        student = input.plot_student()
        if not student:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center")
            ax.axis("off")
            return fig

        # 只取该学生的评分记录
        df = pd.read_sql(
            "SELECT 候选人, 评审人, 总分 FROM history WHERE 候选人 = %s",
            con=engine,
            params=(student,)   # 注意这里是元组，不是 [student]
        )


        if df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "该学生暂无评分数据", ha="center", va="center")
            ax.axis("off")
            return fig
        
        df["总分"] = pd.to_numeric(df["总分"], errors="coerce")
        # 如果存在非法值被转成 NaN，可以顺手丢掉
        df = df.dropna(subset=["总分"])
        if df.empty:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "总分列无法转换为数值", ha="center", va="center")
            ax.axis("off")
            return fig
        
        median_score = df["总分"].median()
        df["差值"] = df["总分"] - median_score
        df_sorted = df.sort_values("差值")
         
        diffs = df_sorted["差值"].values
        judges = df_sorted["评审人"].tolist()

        # x 轴用排序后的序号（1,2,3,...）
        x = np.arange(1, len(diffs) + 1)

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.scatter(x, diffs)

        # 标注每个点对应的评委名字（可选）
        for xi, yi, name in zip(x, diffs, judges):
            ax.text(xi, yi, name, fontsize=8, ha="center", va="bottom")


        ax.set_xlabel("评委")
        ax.set_ylabel("差值")
        ax.set_title(f"{student}：各评委分值与中位数差值的分布")

        ax.set_xticks(x)
        ax.set_xticklabels(range(1, len(diffs) + 1))

        fig.tight_layout()
        return fig
    

    @render.download(filename=lambda: f"{input.plot_student() or 'score_diff'}.pdf")
    def download_pdf():
        student = input.plot_student()
        if not student:
            # 没有选择学生时给个空 PDF
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center")
            ax.axis("off")
        else:
            fig = make_score_diff_figure(student)

        buf = BytesIO()
        fig.savefig(buf, format="pdf", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        # 用 yield 返回二进制内容
        yield buf.getvalue()
    
    @render.download(filename=lambda: f"{input.plot_student() or 'score_diff'}.jpg")
    def download_jpg():
        student = input.plot_student()
        if not student:
            fig, ax = plt.subplots()
            ax.text(0.5, 0.5, "暂无数据", ha="center", va="center")
            ax.axis("off")
        else:
            fig = make_score_diff_figure(student)

        buf = BytesIO()
        fig.savefig(buf, format="jpg", dpi=300, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        yield buf.getvalue()




from io import BytesIO

def make_score_diff_figure(student: str):
    # 与上面 score_diff_plot 中的逻辑一致，只是返回 fig
    df = pd.read_sql(
            "SELECT 候选人, 评审人, 总分 FROM history WHERE 候选人 = %s",
            con=engine,
            params=(student,)   # 注意这里是元组，不是 [student]
        )

    fig, ax = plt.subplots(figsize=(6, 4))

    if df.empty:
        ax.text(0.5, 0.5, "该学生暂无评分数据", ha="center", va="center")
        ax.axis("off")
        return fig
    df["总分"] = pd.to_numeric(df["总分"], errors="coerce")
    # 如果存在非法值被转成 NaN，可以顺手丢掉
    df = df.dropna(subset=["总分"])
    if df.empty:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "总分列无法转换为数值", ha="center", va="center")
        ax.axis("off")
        return fig
    
    median_score = df["总分"].median()
    df["差值"] = df["总分"] - median_score
    df_sorted = df.sort_values("差值")

    diffs = df_sorted["差值"].values
    judges = df_sorted["评审人"].tolist()

    x = np.arange(1, len(diffs) + 1)
    ax.scatter(x, diffs)

    for xi, yi, name in zip(x, diffs, judges):
        ax.text(xi, yi, name, fontsize=8, ha="center", va="bottom")

    ax.set_xlabel("评委")
    ax.set_ylabel("差值")
    ax.set_title(f"{student}：各评委分值与中位数差值的分布")
    ax.set_xticks(x)
    ax.set_xticklabels(range(1, len(diffs) + 1))

    fig.tight_layout()
    return fig
