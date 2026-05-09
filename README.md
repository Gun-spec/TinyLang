# TinyScript Programming Language

**A simple, educational programming language built from scratch in Python!**

**TinyScript is a beginner-friendly language designed to teach you how programming languages work. It includes a full compiler pipeline: lexer, parser, optimizer, and interpreter.**

## PULL REQUESTS DO NOT WORK ON TESTING AND MAIN FOR SECURITY AND STABILITY REASONS PLEASE PULL IT TO DEV !
- I wanted to help other kids like me, learn how to make their own programming language.
- Anyone can fork or remake it but give credits please!
- I also want you to help me develop it, give ideas to give it more possibilities and maybe turn it into a real programming languague
- Please report bugs from recent updates!
---

## 🚀 Features

- **Variables** - Store and use values
- **Math Operations** - `+`, `-`, `*`, `/`
- **Comparisons** - `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Conditionals** - `if/else` statements
- **Loops** - `while` loops
- **Functions** - Define and call your own functions
- **Optimization** - Automatic code optimization before execution
- **Interactive REPL** - Test code snippets interactively

---

## 📦 Installation

No installation needed! Just Python 3.6+

```bash
# Clone or download the files
# Run any TinyScript program:
python tinyscript.py example.ts
```

---

## 🎯 Quick Start

### Hello World

```tinyscript
print("Hello, World!")
```

### Variables and Math

```tinyscript
x = 10
y = 20
z = x + y * 2
print(z)  # Output: 50
```

### Conditionals

```tinyscript
age = 18

if age >= 18 {
    print("You are an adult")
} else {
    print("You are a minor")
}
```

### Loops

```tinyscript
counter = 0
while counter < 5 {
    print(counter)
    counter = counter + 1
}
```

### Functions

```tinyscript
func add(a, b) {
    return a + b
}

result = add(5, 3)
print(result)  # Output: 8
```

### Recursive Functions

```tinyscript
func factorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * factorial(n - 1)
    }
}

print(factorial(5))  # Output: 120
```

---

## 🏗️ Architecture

TinyScript is built with 4 main components:

### 1. **Lexer** (`lexer.py`)
Breaks source code into tokens (like words in a sentence)

```
"x = 10" → [IDENTIFIER(x), ASSIGN(=), NUMBER(10)]
```

### 2. **Parser** (`parser.py`)
Builds an Abstract Syntax Tree (AST) from tokens

```
Tokens → AST (tree structure representing your code)
```

### 3. **Optimizer** (`optimizer.py`)
Makes code run faster by:
- **Constant folding**: `2 + 3` becomes `5` at compile time
- **Dead code elimination**: Removes code that never runs
- **Algebraic simplification**: `x + 0` becomes `x`

### 4. **Interpreter** (`interpreter.py`)
Executes the optimized AST

---

## 🛠️ Usage

### Run a File

```bash
python tinyscript.py example.ts
```

### Interactive REPL

```bash
python tinyscript.py --repl
```

Then type code interactively:
```
>>> x = 10
>>> print(x * 2)
20
```

### See What's Happening Under the Hood

Show tokens:
```bash
python tinyscript.py example.ts --show-tokens
```

Show AST:
```bash
python tinyscript.py example.ts --show-ast
```

Disable optimization:
```bash
python tinyscript.py example.ts --no-optimize
```

---

## 📚 Language Reference

### Data Types
- **Numbers**: `42`, `3.14`
- **Strings**: `"hello world"`

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Assignment**: `=`

### Keywords
- `if`, `else` - Conditionals
- `while` - Loops
- `func` - Function definition
- `return` - Return from function
- `print()` - Print output

### Comments
```tinyscript
# This is a comment
x = 10  # Comments can go after code
```

### Syntax Rules
- Statements can end with newlines or semicolons
- Code blocks use curly braces `{ }`
- Function calls need parentheses: `print(x)`

---

## 🎓 Learning Guide

### For Complete Beginners

Start here:

1. **Read `lexer.py`** - Learn how code becomes tokens
2. **Read `parser.py`** - Learn how tokens become a tree
3. **Read `interpreter.py`** - Learn how the tree executes
4. **Read `optimizer.py`** - Learn how code gets faster

### Exercises

1. **Add new operators**
   - Try adding `%` (modulo) operator
   - Add `**` (power) operator

2. **Add new statements**
   - Add `for` loops
   - Add `break` and `continue`

3. **Add new data types**
   - Add lists/arrays
   - Add boolean values (`true`/`false`)

4. **Improve the optimizer**
   - Add more optimization rules
   - Detect infinite loops

---

## 🔧 File Structure

```
├── lexer.py         # Tokenizes source code
├── parser.py        # Builds Abstract Syntax Tree
├── interpreter.py   # Executes the AST
├── optimizer.py     # Optimizes the AST
├── tinyscript.py    # Main compiler/interpreter
├── example.ts       # Example programs
└── README.md        # This file
```

---

## 🧪 Example Programs

### Fibonacci Sequence

```tinyscript
func fibonacci(n) {
    if n <= 1 {
        return n
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2)
    }
}

counter = 0
while counter < 10 {
    print(fibonacci(counter))
    counter = counter + 1
}
```

### Greatest Common Divisor (GCD)

```tinyscript
func gcd(a, b) {
    while b != 0 {
        temp = b
        b = a - (a / b) * b
        a = temp
    }
    return a
}

print(gcd(48, 18))  # Output: 6
```

---

## 🐛 Known Limitations

- No floating-point precision in division (uses Python's `/`)
- No string operations yet (concatenation, slicing)
- No arrays or data structures
- No classes or objects
- No imports or modules

These are great opportunities for you to add features!

---

## 💡 How It Works (High Level)

```
Source Code
    ↓
[Lexer] → Tokens
    ↓
[Parser] → Abstract Syntax Tree (AST)
    ↓
[Optimizer] → Optimized AST
    ↓
[Interpreter] → Execution & Output
```

---

## 📖 Resources for Learning More

- **"Crafting Interpreters"** by Robert Nystrom (free online)
- **"Writing An Interpreter In Go"** by Thorsten Ball
- **"Engineering a Compiler"** by Keith Cooper
- **Python's `ast` module** - See how Python itself parses code

---

## 🤝 Contributing

This is an educational project! Feel free to:
- Add new features
- Fix bugs
- Improve documentation
- Create more example programs

---

## 📝 License

Free to use for learning! Do whatever you want with it.

---

## 🎉 Have Fun!

Building a programming language is one of the most rewarding projects you can do as a programmer. You'll learn:

- How compilers work
- How parsers work
- How optimization works
- How programming languages are designed

**Now go build something amazing!** 🚀
