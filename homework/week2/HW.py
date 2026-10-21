import math

# 1. T(n) = T(n-1) + 8, T(1) = 1
def solve_1(n: int) -> int:
    """精確公式: 8n - 7 (Big O: O(n))"""
    if n < 1:
        raise ValueError("n 必須大於等於 1")
    return 8 * n - 7

# 2. T(n) = 2*T(n-1) + 9, T(1) = 1
def solve_2(n: int) -> int:
    """精確公式: 5 * (2**n) - 9 (Big O: O(2^n))"""
    if n < 1:
        raise ValueError("n 必須大於等於 1")
    return 5 * (2 ** n) - 9

# 3. T(n) = 2*T(n/2) + 1, T(1) = 1 (假設 n 為 2 的次方)
def solve_3(n: int) -> int:
    """精確公式: 2n - 1 (Big O: O(n))"""
    if n < 1:
        raise ValueError("n 必須大於等於 1")
    return 2 * n - 1

# 4. T(n) = T(n/2) + 1, T(1) = 1 (假設 n 為 2 的次方)
def solve_4(n: int) -> int:
    """精確公式: log2(n) + 1 (Big O: O(log n))"""
    if n < 1:
        raise ValueError("n 必須大於等於 1")
    return int(math.log2(n)) + 1


if __name__ == "__main__":
    print("=== 精確公式計算結果 ===")
    
    # 測試題 1 與題 2 (可代入任意整數 n)
    test_n = 5
    print(f"1. T({test_n}) = T({test_n}-1) + 8  -> 精確值: {solve_1(test_n)} | Big O: O(n)")
    print(f"2. T({test_n}) = 2*T({test_n}-1) + 9 -> 精確值: {solve_2(test_n)} | Big O: O(2^n)")
    
    # 測試題 3 與題 4 (以 n = 16 = 2^4 為例)
    pow2_n = 16
    print(f"3. T({pow2_n}) = 2*T({pow2_n}/2) + 1  -> 精確值: {solve_3(pow2_n)} | Big O: O(n)")
    print(f"4. T({pow2_n}) = T({pow2_n}/2) + 1    -> 精確值: {solve_4(pow2_n)} | Big O: O(log n)")

    # 驗證模擬
    print("\n=== 模擬遞迴過程比對 (以第 3 題為例) ===")
    def simulate_3(n):
        val = 1
        curr = 1
        while curr < n:
            curr *= 2
            val = 2 * val + 1
        return val

    print(f"simulate_3({pow2_n}) = {simulate_3(pow2_n)}, 公式解 = {solve_3(pow2_n)}")