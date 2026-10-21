from collections import defaultdict

def build_kmer_index(target: str, k: int) -> dict:
    """建立目標序列的 k-mer 雜湊索引表"""
    index = defaultdict(list)
    for i in range(len(target) - k + 1):
        kmer = target[i:i + k]
        index[kmer].append(i)
    return index

def extend_hit(query: str, target: str, q_pos: int, t_pos: int, k: int, 
               match_score=1, mismatch_penalty=-1, max_drop=2):
    """
    從種子命中點向左與向右雙向無空隙延伸（Ungapped Extension），
    當累計分數相較於最高分衰減超過 max_drop 時觸發 X-drop 提早終止。
    """
    # 種子本體的分數
    current_score = k * match_score
    max_score = current_score
    
    # 記錄延伸邊界
    best_q_left, best_t_left = q_pos, t_pos
    best_q_right, best_t_right = q_pos + k, t_pos + k
    
    # 1. 向左延伸
    score = 0
    max_left_score = 0
    q_l, t_l = q_pos - 1, t_pos - 1
    
    while q_l >= 0 and t_l >= 0:
        score += match_score if query[q_l] == target[t_l] else mismatch_penalty
        if score > max_left_score:
            max_left_score = score
            best_q_left = q_l
            best_t_left = t_l
        elif max_left_score - score >= max_drop:
            # X-drop 停止延伸
            break
        q_l -= 1
        t_l -= 1
        
    # 2. 向右延伸
    score = 0
    max_right_score = 0
    q_r, t_r = q_pos + k, t_pos + k
    
    while q_r < len(query) and t_r < len(target):
        score += match_score if query[q_r] == target[t_r] else mismatch_penalty
        if score > max_right_score:
            max_right_score = score
            best_q_right = q_r + 1
            best_t_right = t_r + 1
        elif max_right_score - score >= max_drop:
            # X-drop 停止延伸
            break
        q_r += 1
        t_r += 1
        
    total_score = current_score + max_left_score + max_right_score
    return total_score, (best_q_left, best_q_right), (best_t_left, best_t_right)

def seed_and_extend_search(query: str, target: str, k=4, min_score_threshold=5):
    """
    主函式：在 target 中檢索與 query 高度相似的局部比對片段
    """
    index = build_kmer_index(target, k)
    hits_evaluated = set()
    results = []
    
    # 遍歷 query 中的每一個 k-mer
    for q_idx in range(len(query) - k + 1):
        kmer = query[q_idx:q_idx + k]
        
        # 尋找種子命中
        if kmer in index:
            for t_idx in index[kmer]:
                # 依對角線編號去重（避免鄰近種子重複延伸同一比對區間）
                diag = q_idx - t_idx
                if diag in hits_evaluated:
                    continue
                
                score, (q_start, q_end), (t_start, t_end) = extend_hit(
                    query, target, q_idx, t_idx, k
                )
                
                if score >= min_score_threshold:
                    hits_evaluated.add(diag)
                    results.append({
                        "score": score,
                        "query_range": (q_start, q_end),
                        "target_range": (t_start, t_end),
                        "query_sub": query[q_start:q_end],
                        "target_sub": target[t_start:t_end]
                    })
                    
    # 依分數由高至低排序
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# === 測試範例 ===
if __name__ == "__main__":
    # 目標資料庫長序列與查詢序列
    target_dna = "TTTTGATCGATCGATCGCCCGGGATTTTT"
    query_dna  = "AAAGATCGATCGATCAAAAA"
    
    matches = seed_and_extend_search(query_dna, target_dna, k=4, min_score_threshold=6)
    
    print(f"Target: {target_dna}")
    print(f"Query : {query_dna}\n")
    print(f"找到 {len(matches)} 個符合門檻的高分比對區域 (HSP):\n")
    
    for i, m in enumerate(matches, 1):
        q_s, q_e = m["query_range"]
        t_s, t_e = m["target_range"]
        print(f"[Result {i}] 分數: {m['score']}")
        print(f"Query  [{q_s:2d}:{q_e:2d}]: {m['query_sub']}")
        
        # 對齊標示符號 (| 表示 match, * 表示 mismatch)
        match_line = "".join("|" if a == b else "*" for a, b in zip(m["query_sub"], m["target_sub"]))
        print(f"              {match_line}")
        print(f"Target [{t_s:2d}:{t_e:2d}]: {m['target_sub']}\n")