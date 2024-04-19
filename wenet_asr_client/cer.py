def cer(s1, s2):
    """
    计算中文语音识别结果字错率（CER）
    
    参数：
    s1: 语音识别结果字符串
    s2: 人工标注的标准答案字符串
    
    返回值：
    字错率数值
    """
    # 将字符串转换为字符列表
    s1_chars = list(s1)
    s2_chars = list(s2)
    
    # 初始化二维数组，用于存储Levenshtein距离
    dp = [[0] * (len(s2_chars) + 1) for _ in range(len(s1_chars) + 1)]
    
    # 初始化第一行和第一列
    for i in range(len(s1_chars) + 1):
        dp[i][0] = i
    for j in range(len(s2_chars) + 1):
        dp[0][j] = j
        
    # 动态规划计算Levenshtein距离
    correct = 0  # 记录正确的字数
    for i in range(1, len(s1_chars) + 1):
        for j in range(1, len(s2_chars) + 1):
            cost = 0 if s1_chars[i - 1] == s2_chars[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1,         # 删除操作
                           dp[i][j - 1] + 1,         # 插入操作
                           dp[i - 1][j - 1] + cost) # 替换操作
            if cost == 0:
                correct += 1
    
    # 计算字错率
    cer = dp[len(s1_chars)][len(s2_chars)] / len(s2_chars)

    # 返回字错率和正确字数数值
    return cer, correct
