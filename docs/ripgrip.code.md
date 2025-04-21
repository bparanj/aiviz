Here are the top **10 practical ripgrep (`rg`) search examples** optimized for **searching a codebase**:

---

### 1. **Find occurrences of a function name**
```bash
rg "fetchUserData"
```

---

### 2. **Case-insensitive search across code**
```bash
rg -i "rendercomponent"
```

---

### 3. **Search for a word only in specific file types (e.g., JavaScript files)**
```bash
rg "useEffect" -g "*.js"
```

---

### 4. **Search while ignoring specific directories (e.g., `node_modules`)**
```bash
rg "setState" --glob '!node_modules/*'
```

---

### 5. **Find definition of a class or method with line numbers**
```bash
rg -n "class UserController"
```

---

### 6. **Regex search for all TODO comments**
```bash
rg "TODO.*"
```

---

### 7. **Search by exact word match (not substring)**
```bash
rg -w "user"
```

---

### 8. **Count number of occurrences across files**
```bash
rg -c "handleClick"
```

---

### 9. **Show context (lines around match)**
```bash
rg -C 3 "submitForm"
```

(_This shows 3 lines above and below each match._)

---

### 10. **List only filenames containing matches**
```bash
rg -l "apiEndpoint"
```

---

### Key Takeaways (Insights):
- Use `-g` for filtering by file type (e.g., `-g '*.py'`).
- Use `--glob '!directory/*'` to exclude directories.
- `-w` ensures exact-word matches, helping avoid false positives.
- `-C` provides context around matches—useful for quick understanding.
- `-l` lists matching filenames quickly without showing the matched lines.

These examples cover common, real-world codebase searching tasks.