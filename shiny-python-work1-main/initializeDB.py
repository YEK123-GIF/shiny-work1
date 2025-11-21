import pandas as pd
from sqlalchemy import create_engine

"""用于初始化数据库"""

history_df = pd.DataFrame(
        columns=[
            "评审时间", "评审人", "候选人",
            "专业基础知识", "逻辑思维能力", "科研潜力", "沟通与表达能力", "综合素质",
            "总分"
        ]
)

students_df = pd.DataFrame(
    columns=[
        'id', 'name'
    ]
)

DIMENSIONS = [
    "专业基础知识",
    "逻辑思维能力",
    "科研潜力",
    "沟通与表达能力",
    "综合素质",
]
DIMENSIONS_df = pd.DataFrame([DIMENSIONS])

root_df = pd.DataFrame(
    columns=[
        'id',
        'name',
        'password'
    ]
)
root_df = pd.concat([
    root_df,
    pd.DataFrame([{"id": "R001", "name": "key", "password": "123456"}])
], ignore_index=True)

judger_df = pd.DataFrame(
    columns=[
        'id',
        'name',
        'password'
    ]
)

grades_df = pd.DataFrame(
    columns=[
    "专业基础知识",
    "逻辑思维能力",
    "科研潜力",
    "沟通与表达能力",
    "综合素质"
    ]
)

engine = create_engine('mysql+pymysql://root:Lzc3219870@localhost:3306/work1?charset=utf8')

history_df.to_sql(name="history", con=engine, if_exists='replace', index=False)
students_df.to_sql(name="students", con=engine, if_exists='replace', index=False)
judger_df.to_sql(name="judger", con=engine, if_exists='replace', index=False)
DIMENSIONS_df.to_sql(name="dimensions", con=engine, if_exists='replace', index=False)
root_df.to_sql(name="root", con=engine, if_exists='replace', index=False)

