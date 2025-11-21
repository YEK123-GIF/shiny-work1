import pandas as pd
from sqlalchemy import create_engine

"""用提供的实例来初始化数据库"""

engine = create_engine('mysql+pymysql://root:Lzc3219870@localhost:3306/work1?charset=utf8')

history_df = pd.read_sql("SELECT * FROM history", engine)
print(history_df)

students_df = pd.read_sql("SELECT * FROM students", engine)
print(students_df)

root_df = pd.read_sql("SELECT * FROM root", engine)
print(root_df)

dims_df = pd.read_sql("SELECT * FROM dimensions", engine)
print(dims_df)

judger_df = pd.read_sql("SELECT * FROM judger", engine)
print(judger_df)