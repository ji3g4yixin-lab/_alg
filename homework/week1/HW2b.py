# 方法2b：用遞迴
def power2n(n):
    result = 2*power2n(n-1)
    return result


print('power2n(100)=', power2n(100))