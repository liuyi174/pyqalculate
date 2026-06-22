# 第4章 命令行界面 (CLI) - 完整参考

> **验证状态**: ✅ 已验证  
> **来源**: `pyqalc/cli.py` (752 行)

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
| `-h` | `--help` | 显示帮助信息 | argparse 自动提供 |

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

**新增功能**: `help <function>` 显示函数详细帮助 [来源: cli.py:453-470]

```
> help sin
  sin - Sine
  Category: Trigonometry
  Syntax: sin(x:number)

> help solve
  solve - Solve equation
  Category: Algebra
  Syntax: solve(equation:symbolic, [variable:symbolic])
```

### functions

列出所有可用函数 [来源: cli.py:473-475]

```
> functions
  Algebra:
    coeff, degree, dsolve, expand, factor, multisolve, roots, solve

  Base:
    base, bases, bin, float, floaterror, hex, oct, roman

  Bitwise:
    bitand, bitnot, bitor, bitxor, shift

  Calculus:
    diff, integrate, limit, product, sum

  Combinatorics:
    binomial, double_factorial, factorial, gamma, multinomial

  Date & Time:
    date, days, lunarphase, months, now, stamptodate, timestamp, today, weeks, years

  Exponents & Logarithms:
    cbrt, cis, exp, exp10, exp2, lambertw, ln, log10, log2, logn, root, sqrt, square

  Logical:
    and, not, or, xor

  Matrix:
    adj, cofactor, cross, det, dot, eigenvalues, hadamard, identity, inverse, magnitude, norm, rank, rref, trace, transpose

  Number Theory:
    abs, arg, bernoulli, ceil, denominator, floor, frac, gcd, im, int, interval, is_prime, lcm, mod, next_prime, nth_prime, numerator, parallel, powermod, prev_prime, prime_count, re, rem, round, signum, totient, trunc, uncertainty

  Special:
    airy, besselj, bessely, beta, digamma, dirac, erf, erfc, fresnelc, fresnels, heaviside, zeta

  Statistics:
    correlation, covariance, max, mean, median, min, mode, normdist, percentile, quartile, rand, stdev, variance

  Trigonometry:
    acos, acosh, asin, asinh, atan, atan2, atanh, cos, cosh, sin, sinc, sinh, tan, tanh

  Utility:
    concatenate, even, export, for, genvector, if, is_integer, is_number, is_rational, is_real, length, load, odd, plot, replace, tostring
```

### constants

列出所有物理常量 [来源: cli.py:477-479]

```
> constants
  Physical Constants:
    alpha = 0.0072973526
    avogadro = 6.0221408e+23
    boltzmann = 1.380649e-23
    c = 299792458
    e = 2.7182818
    e_charge = 1.6021766e-19
    elementary_charge = 1.6021766e-19
    g = 6.6743e-11
    k_b = 1.380649e-23
    n_a = 6.0221408e+23
    ... and 54 more
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

**增强功能**: 当只有一个匹配项时，显示函数描述 [来源: cli.py:214-232]

```
> sin<TAB>
  sin - Sine
```

---

## 4.6 彩色输出

自动检测终端支持 [来源: cli.py:33-58]:

- 绿色：结果
- 青色：提示符
- 黄色：警告
- 禁用：`--no-color` 参数
