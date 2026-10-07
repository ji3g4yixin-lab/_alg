def hanoi(n, source, auxiliary, target):
    """
    使用遞迴解河內塔問題
    :param n: 圓盤數量
    :param source: 來源柱
    :param auxiliary: 輔助柱
    :param target: 目標柱
    """
    # 基本情況：只剩 1 個圓盤時直接移動
    if n == 1:
        print(f"盤子 1：從 {source} 移動到 {target}")
        return

    # 步驟 1：將上面的 n-1 個盤子從 source 移到 auxiliary（藉助 target）
    hanoi(n - 1, source, target, auxiliary)

    # 步驟 2：將第 n 個（最底層）盤子從 source 移到 target
    print(f"盤子 {n}：從 {source} 移動到 {target}")

    # 步驟 3：將 auxiliary 上的 n-1 個盤子移到 target（藉助 source）
    hanoi(n - 1, auxiliary, source, target)


# 執行示範（以 3 個盤子為例，A 為起始柱、B 為輔助柱、C 為目標柱）
if __name__ == "__main__":
    disks = 3
    print(f"=== {disks} 個盤子的移動步驟 ===")
    hanoi(disks, source="A", auxiliary="B", target="C")