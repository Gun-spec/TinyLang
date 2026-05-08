# Example TinyScript Program
# Fibonacci sequence calculator

func fibonacci(n) {
    if n <= 1 {
        return n
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2)
    }
}

print("Fibonacci sequence:")
counter = 0
while counter < 10 {
    result = fibonacci(counter)
    print(result)
    counter = counter + 1
}

# Factorial calculator
func factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

print("Factorial of 5:")
print(factorial(5))

# Simple conditional
x = 100
y = 50

if x > y {
    print("x is greater than y")
} else {
    print("x is not greater than y")
}
