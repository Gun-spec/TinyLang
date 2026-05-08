# Advanced TinyScript Examples
# Demonstrating all language features

# ============================================
# 1. Prime Number Checker
# ============================================

func is_prime(n) {
    if n <= 1 {
        return 0
    }
    
    if n == 2 {
        return 1
    }
    
    divisor = 2
    while divisor * divisor <= n {
        remainder = n - (n / divisor) * divisor
        if remainder == 0 {
            return 0
        }
        divisor = divisor + 1
    }
    
    return 1
}

print("Prime numbers from 1 to 20:")
num = 1
while num <= 20 {
    if is_prime(num) {
        print(num)
    }
    num = num + 1
}

# ============================================
# 2. Tower of Hanoi (Recursive Algorithm)
# ============================================

func hanoi(n, source, target, auxiliary) {
    if n == 1 {
        print("Move disk 1 from rod ")
        print(source)
        print(" to rod ")
        print(target)
        return 1
    }
    
    hanoi(n - 1, source, auxiliary, target)
    print("Move disk ")
    print(n)
    print(" from rod ")
    print(source)
    print(" to rod ")
    print(target)
    hanoi(n - 1, auxiliary, target, source)
    
    return 1
}

print("Tower of Hanoi with 3 disks:")
hanoi(3, 1, 3, 2)

# ============================================
# 3. Sum of Digits
# ============================================

func sum_digits(n) {
    sum = 0
    while n > 0 {
        digit = n - (n / 10) * 10
        sum = sum + digit
        n = n / 10
    }
    return sum
}

print("Sum of digits of 12345:")
print(sum_digits(12345))

# ============================================
# 4. Power Function
# ============================================

func power(base, exp) {
    if exp == 0 {
        return 1
    }
    
    result = 1
    counter = 0
    while counter < exp {
        result = result * base
        counter = counter + 1
    }
    
    return result
}

print("2 to the power of 10:")
print(power(2, 10))

# ============================================
# 5. Nested Function Calls
# ============================================

func add(a, b) {
    return a + b
}

func multiply(a, b) {
    return a * b
}

func calculate(x) {
    return multiply(add(x, 5), 2)
}

print("Calculate (x + 5) * 2 where x = 10:")
print(calculate(10))
