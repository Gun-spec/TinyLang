# TinyScript Programming Language

**A simple, educational programming language built from scratch in Python!**

**TinyScript is a beginner-friendly language designed to teach you how programming languages work. It includes a full compiler pipeline: lexer, parser, optimizer, and interpreter.**

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
- **Clearer diagnostics** - Syntax errors with line and column where possible; runtime errors name the problem (`undefined variable`, division by zero, bad operand types, `return` outside a function)
- **Script-friendly CLI** - Running a file prints errors to **stderr**, uses **exit code `1`** on failure, and reads sources as **UTF-8**
- **Auto-update system** - `tinyscript.py` can check a lightweight update server and pull down the newest release automatically, with SHA-256 verification before anything touches disk

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

TinyScript is built with these main components:

### 1. **Lexer** (`lexer.py`)
Breaks source code into tokens (like words in a sentence). Strips a leading **UTF-8 BOM** if present, reports **unterminated strings** and bad escapes clearly, and gives clearer errors for unknown characters.

```
"x = 10" → [IDENTIFIER(x), ASSIGN(=), NUMBER(10)]
```

### 2. **Parser** (`parser.py`)
Builds an Abstract Syntax Tree (AST) from tokens. Allows **newlines** in more places (e.g. after `=`, inside parentheses, and between operators in expressions), accepts optional **semicolons**, rejects **duplicate function parameter names**, and includes **column** information in many parse errors.

```
Tokens → AST (tree structure representing your code)
```

### 3. **Optimizer** (`optimizer.py`)
Makes code run faster by:
- **Constant folding**: `2 + 3` becomes `5` at compile time
- **Dead code elimination**: Removes code that never runs
- **Algebraic simplification**: `x + 0` becomes `x`

Constant folding uses explicit exception handling (no silent “catch everything”).

### 4. **Interpreter** (`interpreter.py`)
Executes the optimized AST. Raises structured **`TinyScriptRuntimeError`** (see `errors.py`) for undefined names, bad types in operations, division by zero, invalid calls, and **`return` outside a function**.

### 5. **Errors** (`errors.py`)
Shared **`TinyScriptRuntimeError`** type with optional **line/column** so messages are easier to read.

### 6. **Driver** (`tinyscript.py`)
Wires everything together. When you run a **file**, program `print` output is captured so the **OUTPUT** banner only appears after a successful run; failures go to **stderr** without a misleading empty output block. Also contains the **auto-update client** (see below).

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

### Exit codes and output

- **Success** when running a file: process exits with **`0`**.
- **Syntax error, runtime error, file not found, or I/O error**: exits with **`1`**.
- Error messages are written to **stderr**; normal program output from `print()` goes to **stdout**.

---

## 🔄 Auto-Update

TinyScript ships with a small updater built into `tinyscript.py`. It talks to a tiny update server (a Cloudflare Worker) that only ever tells the client **which version exists per channel** and **where to download it** — the update server itself never hosts the files. The actual release ZIPs live on GitHub Releases.

### Checking / applying an update

```bash
# Check for updates and apply them before running (or entering the REPL)
python tinyscript.py --auto-update

# Only check/apply the update, then exit (don't run a file or start the REPL)
python tinyscript.py --self-update

# Force a re-apply even if the local version already matches
python tinyscript.py --auto-update --force-update

# Point at a different update server or channel
python tinyscript.py --auto-update --update-url https://your-worker.workers.dev --update-channel beta
```

Available channels: `stable`, `beta`, `nightly`.

### What happens under the hood

1. The client sends `GET {update-url}/update?channel={channel}` to the Worker.
2. The Worker replies with JSON: `version`, `url` (the GitHub Release asset), `sha256`, `published_at`, `minimum_version`, `mandatory`, and `notes`.
3. `tinyscript.py` downloads the file from `url`, computes its own SHA-256, and **compares it against the hash the server sent**. If they don't match, the update is aborted — nothing is written to disk.
4. Only after the hash check passes does it safely extract the archive (with protection against path-traversal / zip-slip) and copy the files into place. Existing files are overwritten, new files are added, nothing is deleted.
5. The applied version is remembered locally in `.tinyscript_update_state.json`, so re-running `--auto-update` is a no-op once you're already current.

This means TinyScript never trusts a download just because it came from the expected URL — the SHA-256 the Worker reports has to match the actual bytes every single time.

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
- Statements can end with newlines or optional semicolons (`;`); extra `;`-only lines are allowed
- You can break lines before `=` in assignments and inside `( )` for calls and grouped expressions (the parser skips newline tokens between related tokens)
- Code blocks use curly braces `{ }`
- Function calls need parentheses: `print(x)`
- Function parameters must have **unique names** (duplicates are a syntax error)
- **`return`** is only valid **inside** a function body

---

## 🎓 Learning Guide

### For Complete Beginners

Start here:

1. **Read `lexer.py`** - Learn how code becomes tokens
2. **Read `parser.py`** - Learn how tokens become a tree
3. **Read `interpreter.py`** - Learn how the tree executes
4. **Read `optimizer.py`** - Learn how code gets faster
5. **Read `errors.py`** - See how runtime errors attach source locations
6. **Read the `tinyscript-update-worker` project** - See how a minimal, stateless update server can be built on Cloudflare Workers

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

5. **Extend the update system**
   - Add OS/architecture-specific downloads (`?channel=stable&os=linux&arch=x64`)
   - Add percentage-based rollout
   - Add digital signature verification on top of SHA-256

---

## 🔧 File Structure

```
├── lexer.py         # Tokenizes source code
├── parser.py        # Builds Abstract Syntax Tree
├── interpreter.py   # Executes the AST
├── optimizer.py     # Optimizes the AST
├── errors.py        # TinyScriptRuntimeError and message helpers
├── tinyscript.py    # Main compiler/interpreter (CLI + wiring + auto-update client)
├── example.ts       # Example programs
├── advanced_example.ts
└── README.md        # This file
```

The update server itself lives in a separate small project, `tinyscript-update-worker/` (Cloudflare Worker, ES Modules):

```
tinyscript-update-worker/
├── wrangler.toml
├── package.json
└── src/
    ├── index.js      # Routing: GET /update, GET /health
    ├── versions.js   # Per-channel version data (version, url, sha256, notes...)
    └── http.js       # Shared JSON response helpers
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
Source Code (UTF-8)
    ↓
[Lexer] → Tokens
    ↓
[Parser] → Abstract Syntax Tree (AST)
    ↓
[Optimizer] → Optimized AST
    ↓
[Interpreter] → Execution & Output (errors → TinyScriptRuntimeError / stderr)
```

Update flow (separate from program execution):

```
tinyscript.py --auto-update
    ↓
GET {update-url}/update?channel={channel}  → Cloudflare Worker
    ↓
JSON: { version, url, sha256, mandatory, notes, ... }
    ↓
Download file from `url` → verify SHA-256 → safe-extract → copy into place
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