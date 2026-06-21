# PyQalculate 编码规范

## 1. Python 版本

- **最低版本**: Python 3.8
- **推荐版本**: Python 3.10+

## 2. 代码风格

### 2.1 PEP 8 规范

遵循 PEP 8 规范，主要规则：

- **缩进**: 4 个空格，不使用 Tab
- **行宽**: 最大 88 字符（Black 默认）
- **命名**:
  - 类名: `PascalCase` (如 `Calculator`, `MathStructure`)
  - 函数/方法: `snake_case` (如 `calculate_and_print`, `to_sympy`)
  - 常量: `UPPER_SNAKE_CASE` (如 `FUNCTION_ID_PLOT`, `DEFAULT_PRECISION`)
  - 私有成员: `_single_leading_underscore` (如 `_calculator`, `_children`)
- **导入**: 每行一个导入，按标准库、第三方库、本地库分组

### 2.2 类型注解

**必须**使用类型注解（Type Hints）：

```python
# ✅ 正确
def calculate(self, expression: str, eo: EvaluationOptions | None = None) -> MathStructure:
    ...

# ❌ 错误
def calculate(self, expression, eo=None):
    ...
```

**规则**:
- 函数参数和返回值必须有类型注解
- 复杂类型使用 `TypeAlias` 定义别名
- 可选参数使用 `X | None` 或 `Optional[X]`

### 2.3 文档字符串

**必须**为公共 API 编写文档字符串：

```python
def calculate_and_print(
    self,
    expression: str,
    eo: EvaluationOptions | None = None,
    po: PrintOptions | None = None,
) -> str:
    """Calculate an expression and return formatted result.

    Args:
        expression: Mathematical expression string (e.g., "2 + 3", "sin(pi/2)").
        eo: Evaluation options (precision, approximation mode, etc.).
        po: Print options (decimal places, notation, etc.).

    Returns:
        Formatted result string.

    Raises:
        ValueError: If expression cannot be parsed.

    Examples:
        >>> calc = Calculator()
        >>> calc.calculate_and_print("2 + 3")
        '5'
        >>> calc.calculate_and_print("sin(pi/2)")
        '1'
    """
    ...
```

**格式**: Google 风格（Args, Returns, Raises, Examples）

## 3. 架构规范

### 3.1 模块职责

每个模块有**单一职责**：

| 模块 | 职责 | 禁止 |
|------|------|------|
| `calculator.py` | 协调计算流程 | 不包含数学逻辑 |
| `math_structure.py` | AST 表示 | 不执行计算 |
| `parser.py` | 字符串 → AST | 不修改 AST |
| `builtin_functions.py` | 函数实现 | 不处理解析 |
| `number.py` | 数值运算 | 不处理表达式 |

### 3.2 依赖方向

```
calculator.py
    ├── parser.py
    ├── math_structure.py
    ├── builtin_functions.py
    ├── number.py
    ├── unit.py
    ├── variable.py
    └── plot.py

math_structure.py
    ├── number.py
    ├── unit.py
    └── variable.py

builtin_functions.py
    └── math_structure.py
```

**禁止循环依赖**：如果 A 依赖 B，则 B 不能依赖 A。

### 3.3 全局状态

**最小化**全局状态：

```python
# ✅ 推荐：通过参数传递
def calculate(expr: str, calc: Calculator) -> str:
    return calc.calculate_and_print(expr)

# ❌ 避免：全局变量
_calculator: Calculator | None = None

def calculate(expr: str) -> str:
    global _calculator
    if _calculator is None:
        _calculator = Calculator()
    return _calculator.calculate_and_print(expr)
```

**例外**: `Calculator` 的全局实例 `_calculator` 是允许的，因为它代表应用状态。

## 4. 错误处理

### 4.1 异常类型

使用**具体的异常类型**：

```python
# ✅ 正确
class ParseError(Exception):
    """Expression parsing failed."""
    pass

class CalculationError(Exception):
    """Calculation failed."""
    pass

# ❌ 错误
raise Exception("Something went wrong")
```

### 4.2 异常捕获

**不要**捕获所有异常：

```python
# ✅ 正确
try:
    result = calc.calculate_and_print(expr)
except ParseError as e:
    return f"Parse error: {e}"
except CalculationError as e:
    return f"Calculation error: {e}"

# ❌ 错误
try:
    result = calc.calculate_and_print(expr)
except Exception:
    return "Error"
```

### 4.3 空值处理

使用**明确的空值检查**：

```python
# ✅ 正确
if value is None:
    return default_value

if not items:
    return []

# ❌ 错误
if value == None:
    return default_value

if len(items) == 0:
    return []
```

## 5. 测试规范

### 5.1 测试文件结构

```
tests/
├── test_calculator.py      # Calculator 测试
├── test_functions.py       # 内置函数测试
├── test_parser.py          # 解析器测试
├── test_number.py          # 数值运算测试
├── test_unit.py            # 单位测试
├── test_plot.py            # 绘图测试
├── test_cli.py             # CLI 测试
├── test_gui.py             # GUI 测试
└── test_integration.py     # 集成测试
```

### 5.2 测试命名

```python
class TestCalculator:
    """Calculator 类的测试。"""

    def test_basic_addition(self):
        """测试基本加法。"""
        ...

    def test_complex_expression(self):
        """测试复杂表达式。"""
        ...

    def test_error_handling_invalid_expression(self):
        """测试无效表达式的错误处理。"""
        ...
```

**规则**: `test_<功能>_<场景>_<预期结果>`

### 5.3 测试覆盖率

- **目标**: ≥ 80% 代码覆盖率
- **必须测试**:
  - 公共 API 的所有方法
  - 边界条件
  - 错误处理路径
- **可选测试**:
  - 私有方法（通过公共方法间接测试）
  - 纯 UI 代码

### 5.4 测试运行

```bash
# 运行所有测试
pytest tests -v

# 运行特定测试文件
pytest tests/test_calculator.py -v

# 运行带覆盖率
pytest tests --cov=pyqalculate --cov-report=html

# 运行匹配的测试
pytest tests -k "test_addition"
```

## 6. Git 规范

### 6.1 提交信息格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**类型**:
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 代码重构
- `perf`: 性能优化
- `chore`: 构建/工具相关

**示例**:
```
feat(calculator): add CSV import support

- Add Calculator.importCSV() method
- Add LoadFunction class
- Add tests for CSV import

Closes #123
```

### 6.2 分支策略

- `master`: 稳定版本，随时可发布
- `dev`: 开发分支，功能合并到这里
- `feature/*`: 功能分支，从 dev 分出
- `fix/*`: 修复分支，从 master 分出

### 6.3 Pull Request 规范

- 标题清晰描述变更
- 包含变更说明
- 关联相关 Issue
- 通过所有测试
- 代码审查通过

## 7. 文档规范

### 7.1 文档结构

```
docs/
├── plans/              # 开发计划（过程文档）
├── standards/          # 编码规范（产品文档）
├── analysis/           # 分析文档（产品文档）
└── README.md           # 文档索引
```

### 7.2 文档命名

- 使用 `UPPER_SNAKE_CASE.md`
- 名称清晰描述内容
- 示例: `PROJECT_STRUCTURE.md`, `CODING_GUIDELINES.md`

### 7.3 文档更新

- 代码变更时同步更新文档
- 重大变更需要文档审查
- 过时文档及时归档或删除

## 8. 性能规范

### 8.1 响应时间

- **CLI 响应**: < 100ms（简单表达式）
- **GUI 响应**: < 200ms（用户交互）
- **复杂计算**: < 5s（积分、求解方程）

### 8.2 内存使用

- **基础内存**: < 50MB（Calculator 实例）
- **峰值内存**: < 200MB（复杂计算）

### 8.3 优化策略

- 使用 `__slots__` 减少内存占用
- 使用 `functools.lru_cache` 缓存计算结果
- 使用生成器处理大数据集

## 9. 安全规范

### 9.1 输入验证

**所有外部输入**必须验证：

```python
def parse_expression(expression: str) -> MathStructure:
    if not isinstance(expression, str):
        raise TypeError("Expression must be a string")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression too long")
    ...
```

### 9.2 文件操作

**文件操作**必须使用安全路径：

```python
# ✅ 正确
path = os.path.join(base_dir, filename)
if not path.startswith(base_dir):
    raise ValueError("Invalid path")

# ❌ 错误
path = base_dir + "/" + filename  # 路径遍历风险
```

### 9.3 依赖管理

- 定期更新依赖（安全补丁）
- 使用 `pip-audit` 检查已知漏洞
- 锁定依赖版本（`requirements.txt` 或 `pyproject.toml`）

## 10. 代码审查清单

提交代码前检查：

- [ ] 类型注解完整
- [ ] 文档字符串完整
- [ ] 测试覆盖新功能
- [ ] 无 `print()` 调试语句
- [ ] 无硬编码值
- [ ] 无循环依赖
- [ ] 异常处理正确
- [ ] 代码风格符合 PEP 8

---

*文档版本: 1.0*  
*最后更新: 2026-06-21*
