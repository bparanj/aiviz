Here are **10 search examples** using **ripgrep (`rg`)** on text files from the command line:

---

### 1. Basic text search in a file
```bash
rg "hello world" myfile.txt
```

---

### 2. Case-insensitive search
```bash
rg -i "hello world" myfile.txt
```

---

### 3. Search recursively in all files under a directory
```bash
rg "search_term" mydirectory/
```

---

### 4. Show line numbers in results
```bash
rg -n "search_term" file.txt
```

---

### 5. Search exact words only
```bash
rg -w "exactword" file.txt
```

---

### 6. Search multiple file types (e.g., `.txt` and `.md`)
```bash
rg "search_term" -g '*.txt' -g '*.md'
```

---

### 7. Invert match (show lines not matching)
```bash
rg -v "exclude_this" file.txt
```

---

### 8. Count occurrences of matches
```bash
rg -c "search_term" file.txt
```

---

### 9. Limit search depth (e.g., 1-level deep directories only)
```bash
rg --max-depth 1 "search_term" .
```

---

### 10. Search using a regular expression (regex)
_Example: Find all email addresses_
```bash
rg "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" file.txt
```

---

### **Key Takeaway (Insights):**

- **Default recursive search:** ripgrep automatically searches directories recursively.
- **Great performance:** Optimized for speed, even with complex regex.
- **Intuitive defaults:** easy-to-remember flags for common operations (`-i`, `-n`, `-w`, `-c`).

These 10 examples cover most common scenarios when searching text files using ripgrep.