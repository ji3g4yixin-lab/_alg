from functools import reduce


def is_sorted(arr):
    """【狀態檢驗】使用 map 與 filter 檢查是否已無逆序對（提早終止判斷）"""
    if len(arr) <= 1:
        return True

    # 1. map：取出所有相鄰元素組 (arr[i], arr[i+1])
    pairs = map(lambda i: (arr[i], arr[i + 1]), range(len(arr) - 1))

    # 2. filter：篩選出前大於後的逆序對
    inversions = list(filter(lambda p: p[0] > p[1], pairs))

    # 若無任何逆序對，表示已完全排序
    return len(inversions) == 0


def bubble_pass(arr):
    """【內層單趟冒泡】使用 reduce 走訪一輪串列，將較大元素推往尾端"""

    def step(acc, x):
        if not acc:
            return [x]
        prev = acc[-1]
        if prev > x:
            # 發生逆序：將當前較小的 x 往前擺，較大的 prev 推向後方
            return acc[:-1] + [x, prev]
        # 順序正確：直接附加於尾端
        return acc + [x]

    return reduce(step, arr, [])


def bubble_sort(arr):
    """【外層控制】使用 reduce 驅動每回合冒泡，完全不依賴 for/while 迴圈"""
    if len(arr) <= 1:
        return arr

    def outer_step(current_arr, _):
        # 提早結束優化：若已經排序完成，直接跳過後續回合
        if is_sorted(current_arr):
            return current_arr
        return bubble_pass(current_arr)

    # 泡沫排序最多需執行 len(arr) - 1 次冒泡
    return reduce(outer_step, range(len(arr) - 1), list(arr))


# ================= 測試範例 =================
if __name__ == "__main__":
    test_cases = [
        [64, 34, 25, 12, 22, 11, 90],
        [5, 1, 4, 2, 8],
        [1, 2, 3, 4, 5],  # 已經排序（触發提早終止）
        [9, 8, 7, 6, 5],  # 完全反序
        [3, 3, 1, 2, 2],  # 含重複值
    ]

    for nums in test_cases:
        sorted_nums = bubble_sort(nums)
        print(f"原陣列: {nums:<25} -> 排序後: {sorted_nums}")