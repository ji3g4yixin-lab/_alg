def needleman_wunsch(seq1: str, seq2: str, match_score=1, mismatch_penalty=-1, gap_penalty=-2):
    """
    使用 Needleman-Wunsch 動態規劃演算法比對兩條 DNA 序列。
    
    :param seq1: 第一條 DNA 序列
    :param seq2: 第二條 DNA 序列
    :param match_score: 鹼基配對相同時的得分（預設 +1）
    :param mismatch_penalty: 鹼基錯配時的懲罰得分（預設 -1）
    :param gap_penalty: 引入空格/缺失時的懲罰得分（預設 -2）
    """
    m, n = len(seq1), len(seq2)
    
    # 1. 建立 DP 分數矩陣與方向矩陣（用於回溯）
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    trace = [[None] * (n + 1) for _ in range(m + 1)]
    
    # 2. 初始化邊界條件（首行首列對應全部與空格 gap 比對）
    for i in range(1, m + 1):
        dp[i][0] = dp[i - 1][0] + gap_penalty
        trace[i][0] = 'UP'
    for j in range(1, n + 1):
        dp[0][j] = dp[0][j - 1] + gap_penalty
        trace[0][j] = 'LEFT'
        
    # 3. 填表計算最佳分數
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # 判斷當前鹼基是否相同
            score_diag = match_score if seq1[i - 1] == seq2[j - 1] else mismatch_penalty
            
            # 三種可能轉移來源
            from_diag = dp[i - 1][j - 1] + score_diag  # 對角線：配對或錯配
            from_up = dp[i - 1][j] + gap_penalty       # 上方：seq2 插入 gap
            from_left = dp[i][j - 1] + gap_penalty     # 左方：seq1 插入 gap
            
            # 取最大得分
            best_score = max(from_diag, from_up, from_left)
            dp[i][j] = best_score
            
            # 記錄回溯方向
            if best_score == from_diag:
                trace[i][j] = 'DIAG'
            elif best_score == from_up:
                trace[i][j] = 'UP'
            else:
                trace[i][j] = 'LEFT'
                
    # 4. 回溯路徑（從右下角 dp[m][n] 走回左上角 dp[0][0]）
    aligned_seq1 = []
    aligned_seq2 = []
    i, j = m, n
    
    while i > 0 or j > 0:
        direction = trace[i][j]
        if direction == 'DIAG':
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif direction == 'UP':
            aligned_seq1.append(seq1[i - 1])
            aligned_seq2.append('-')
            i -= 1
        elif direction == 'LEFT':
            aligned_seq1.append('-')
            aligned_seq2.append(seq2[j - 1])
            j -= 1

    # 反轉字串還原正向順序
    aligned_1 = "".join(reversed(aligned_seq1))
    aligned_2 = "".join(reversed(aligned_seq2))
    
    # 產生比對標示符號 (| 表示 match, * 表示 mismatch, 空格表示 gap)
    comparison = []
    for a, b in zip(aligned_1, aligned_2):
        if a == b:
            comparison.append("|")
        elif a == '-' or b == '-':
            comparison.append(" ")
        else:
            comparison.append("*")
    comp_line = "".join(comparison)
    
    return dp[m][n], aligned_1, comp_line, aligned_2


# === 測試範例 ===
if __name__ == "__main__":
    dna_a = "AGCACACA"
    dna_b = "ACACACTA"
    
    final_score, align1, comp, align2 = needleman_wunsch(dna_a, dna_b)
    
    print(f"DNA 序列 1: {dna_a}")
    print(f"DNA 序列 2: {dna_b}")
    print(f"最佳相似度比對分數: {final_score}\n")
    print("最佳比對結果 (Alignment):")
    print(f"Seq 1: {align1}")
    print(f"       {comp}")
    print(f"Seq 2: {align2}")