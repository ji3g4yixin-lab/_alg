def quicksort(arr):
    """使用 filter 與遞迴實作的純函數式快速排序"""
    if len(arr) <= 1:
        return arr

    pivot = arr[0]

    return (
        quicksort(list(filter(lambda x: x < pivot, arr)))
        + list(filter(lambda x: x == pivot, arr))
        + quicksort(list(filter(lambda x: x > pivot, arr)))
    )


# ================= 測試範例 =================
if __name__ == "__main__":
    nums = [38, 27, 43, 3, 9, 82, 10, 27]
    print(f"排序前: {nums}")
    print(f"排序後: {quicksort(nums)}")