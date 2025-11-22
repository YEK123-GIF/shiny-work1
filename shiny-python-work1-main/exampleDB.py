import pandas as pd
from sqlalchemy import create_engine

"""用提供的示例来初始化数据库"""

engine = create_engine('mysql+pymysql://root:Lzc3219870@localhost:3306/work1?charset=utf8')

history_df = pd.read_csv("example/history.csv")
students_df = pd.read_csv("example/students.csv")
judger_df = pd.read_csv("example/judger.csv")
DIMENSIONS_df = pd.read_csv("example/dimensions.csv")
root_df = pd.read_csv("example/root.csv")

history_df.to_sql(name="history", con=engine, if_exists='replace', index=False)
students_df.to_sql(name="students", con=engine, if_exists='replace', index=False)
judger_df.to_sql(name="judger", con=engine, if_exists='replace', index=False)
DIMENSIONS_df.to_sql(name="dimensions", con=engine, if_exists='replace', index=False)
root_df.to_sql(name="root", con=engine, if_exists='replace', index=False)
