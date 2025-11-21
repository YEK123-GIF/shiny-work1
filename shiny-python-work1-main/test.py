# 1. 获取评分维度列表（处理 dims 为 None 的情况）
dims = list(DIMENSIONS.iloc[0]) if (not DIMENSIONS.empty and DIMENSIONS.iloc[0] is not None) else []
    
# 2. 遍历维度读取分数，转为整数（存储为字典：维度名 -> 整数分数）
scores = {}
for dim in dims:
    # 读取滑块值（默认返回 float，如 5.0、8.5）
    score = input[f"score_{dim}"]()  
        
    # 处理空值/异常值
    if score is None:
        score_float = 0.0  # 空值默认0分
        
    scores[dim] = score