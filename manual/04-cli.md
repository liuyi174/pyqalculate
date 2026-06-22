# 第4章 命令行界面 (CLI)

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalc/cli.py` (602 行)

---

## 4.1 启动方式

```bash
# 直接启动
python -m pyqalc

# 通过启动器
start.bat → 选择 [1]
```

[来源: pyqalc/__main__.py:3]

---

## 4.2 命令行参数

| 参数 | 长参数 | 说明 | 来源 |
|------|--------|------|------|
| `expression` | — | 要计算的表达式（位置参数） | `cli.py:72-76` |
| `-t` | `--terse` | 只显示结果（不回显表达式） | `cli.py:77-83` |
| `-b` | `--base BASE` | 设置输出进制 (2, 8, 10, 16) | `cli.py:84-91` |
| `-s` | `--set OPTION` | 设置选项（如 `"precision 20"`） | `cli.py:92-99` |
| `-e` | `--exrates` | 启动时更新汇率 | `cli.py:100-106` |
| `-v` | `--version` | 显示版本 | `cli.py:107-112` |
| — | `--no-color` | 禁用彩色输出 | `cli.py:113-118` |

---

## 4.3 使用模式

### 单次计算模式

```bash
# 基本计算
python -m pyqalc "1 + 1"
# 输出: 1 + 1 = 2

# 简洁模式
python -m pyqalc -t "sin(pi/2)"
# 输出: 1

# 多表达式
python -m pyqalc "2+3" "4*5"
# 输出: 2+3 = 5
#        4*5 = 20
```

[来源: cli.py:583-595]

### 交互式 REPL

```bash
python -m pyqalc
> 2 + 3
  5
> sin(pi/2)
  1
> quit
```

[来源: cli.py:412-533]

**REPL 特性**:
- 命令历史（保存到 `~/.pyqalc_history`）[来源: cli.py:134]
- Tab 补全（函数、变量、单位）[来源: cli.py:155-183]
- `ans` 变量存储上次结果 [来源: cli.py:429-435]
- 彩色输出 [来源: cli.py:439, 527]

---

## 4.4 REPL 元命令

### help

显示帮助信息 [来源: cli.py:190-205, 453-455]

```
> help
```

### set

显示或设置选项 [来源: cli.py:208-257]

```
> set                    # 显示所有设置
> set precision 20       # 设置精度为 20 位
> set base 16            # 设置输出进制为十六进制
> set approx approximate # 设置近似模式
```

**set 子选项**:

| 选项 | 值 | 说明 |
|------|-----|------|
| `precision` | 整数 | 有效数字位数 |
| `base` | 2-36 | 输出进制 |
| `approx` | `exact`, `approx`, `try_exact` | 近似模式 |

[来源: cli.py:228-257]

### base

改变输出进制 [来源: cli.py:260-287]

```
> base bin    # 二进制
> base oct    # 八进制
> base dec    # 十进制
> base hex    # 十六进制
> base 16     # 十六进制（数字形式）
```

### save

保存变量 [来源: cli.py:290-317]

```
> save x 42      # 保存 x = 42
> save result    # 保存上次结果为 result
```

### delete

删除用户变量 [来源: cli.py:320-335]

```
> delete x       # 删除变量 x
```

### assume

设置未知数假设 [来源: cli.py:338-347]

```
> assume x > 0
```

### mode

显示或切换模式 [来源: cli.py:350-385]

```
> mode              # 显示当前模式
> mode exact        # 精确模式
> mode approx       # 近似模式
> mode fraction     # 分数显示
> mode decimal      # 小数显示
```

**模式说明**:

| 模式 | 效果 |
|------|------|
| `exact` | 精确模式，不近似 |
| `approx` | 近似模式，浮点计算 |
| `fraction` | 分数显示 |
| `decimal` | 小数显示 |

[来源: cli.py:365-385]

### factorize

因式分解上次结果 [来源: cli.py:497-511]

```
> 12
  12
> factorize
  2^2 * 3
```

### simplify

简化上次结果 [来源: cli.py:513-521]

```
> (x^2 - 4)/(x - 2)
  (x^2 - 4)/(x - 2)
> simplify
  x + 2
```

### quit / exit / q

退出 REPL [来源: cli.py:450-451]

---

## 4.5 Tab 补全

支持补全的内容 [来源: cli.py:155-183]:

- 内置函数名（如 `sin`, `cos`, `sqrt`）
- 变量名（如 `pi`, `e`）
- 单位名（如 `m`, `kg`, `ft`）
- 元命令（如 `set`, `help`, `mode`）

---

## 4.6 彩色输出

自动检测终端支持 [来源: cli.py:33-58]:

- 绿色：结果
- 青色：提示符
- 黄色：警告
- 禁用：`--no-color` 参数
