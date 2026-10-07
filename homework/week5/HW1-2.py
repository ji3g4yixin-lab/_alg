def hanoi_stack(n, source, auxiliary, target):
    """使用自建堆疊模擬遞迴呼叫的河內塔解法"""
    # 堆疊元素格式：(當前盤數, 來源柱, 輔助柱, 目標柱)
    stack = [(n, source, auxiliary, target)]

    while stack:
        disks, src, aux, tgt = stack.pop()

        if disks == 1:
            print(f"盤子 1：從 {src} 移動到 {tgt}")
        else:
            # 由於堆疊是 LIFO（後進先出），放入順序需與遞迴執行順序相反：
            # 實際執行順序：步驟 1 -> 步驟 2 -> 步驟 3
            # 壓入堆疊順序：步驟 3 -> 步驟 2 -> 步驟 1
            stack.append((disks - 1, aux, src, tgt))  # 步驟 3
            stack.append((1, src, aux, tgt))          # 步驟 2（移動最大的盤子）
            stack.append((disks - 1, src, tgt, aux))  # 步驟 1


if __name__ == "__main__":
    print("=== 堆疊法模擬（3 個盤子）===")
    hanoi_stack(3, "A", "B", "C")
    
def move_disks_between_pegs(peg1, peg2, name1, name2):
    """在兩根柱子之間執行唯一合法的移動"""
    if not peg1:
        # peg1 為空，將 peg2 頂端移過去
        disk = peg2.pop()
        peg1.append(disk)
        print(f"盤子 {disk}：從 {name2} 移動到 {name1}")
    elif not peg2:
        # peg2 為空，將 peg1 頂端移過去
        disk = peg1.pop()
        peg2.append(disk)
        print(f"盤子 {disk}：從 {name1} 移動到 {name2}")
    elif peg1[-1] > peg2[-1]:
        # peg2 頂端較小，移到 peg1
        disk = peg2.pop()
        peg1.append(disk)
        print(f"盤子 {disk}：從 {name2} 移動到 {name1}")
    else:
        # peg1 頂端較小，移到 peg2
        disk = peg1.pop()
        peg2.append(disk)
        print(f"盤子 {disk}：從 {name1} 移動到 {name2}")


def hanoi_iterative(n):
    """數學規律迭代法"""
    src, aux, tgt = list(range(n, 0, -1)), [], []
    src_name, aux_name, tgt_name = "A", "B", "C"

    # 若盤數為偶數，交換目標柱與輔助柱的處理順序
    if n % 2 == 0:
        aux_name, tgt_name = tgt_name, aux_name
        aux, tgt = tgt, aux

    total_moves = (1 << n) - 1  # 2^n - 1

    for step in range(1, total_moves + 1):
        remainder = step % 3
        if remainder == 1:
            move_disks_between_pegs(src, tgt, src_name, tgt_name)
        elif remainder == 2:
            move_disks_between_pegs(src, aux, src_name, aux_name)
        elif remainder == 0:
            move_disks_between_pegs(aux, tgt, aux_name, tgt_name)


if __name__ == "__main__":
    print("\n=== 數學迭代法（3 個盤子）===")
    hanoi_iterative(3)
    
