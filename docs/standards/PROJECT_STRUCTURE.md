# PyQalculate 项目结构文档

## 1. 项目概述

PyQalculate 是 libqalculate 的纯 Python 移植版本，包含核心数学引擎、CLI 和 GUI。

**版本**: v2.1.2  
**仓库**: https://github.com/anotlife/pyqalculate  
**Python**: 3.8+  
**依赖**: sympy, gmpy2 (可选), matplotlib (可选)

---

## 2. 目录结构

```
pyqalculate/
├── pyqalculate/                # 核心库
│   ├── __init__.py
│   ├── calculator.py           # Calculator 主类 (906+ 行)
│   ├── math_structure.py       # MathStructure AST (1200+ 行)
│   ├── parser.py               # 表达式解析器
│   ├── builtin_functions.py    # 151+ 内置函数 (3400+ 行)
│   ├── number.py               # 任意精度数字 (2500+ 行)
│   ├── unit.py                 # 单位系统
│   ├── variable.py             # 变量管理
│   ├── function.py             # 函数基类
│   ├── dataset.py              # 数据集
│   ├── datetime_ext.py         # 日期时间扩展
│   ├── definitions.py          # 定义加载
│   ├── expression_item.py      # 表达式项基类
│   ├── prefix.py               # 前缀 (SI, 二进制)
│   ├── plot.py                 # 绘图模块 (322 行)
│   └── types.py                # 类型定义
│
├── pyqalc/                     # CLI 模块
│   ├── __init__.py
│   ├── __main__.py             # python -m pyqalc 入口
│   └── cli.py                  # CLI 实现 (602 行)
│
├── pyqalculate_gui/            # GUI 模块 (v2.2 重建中)
│   ├── __init__.py
│   ├── __main__.py             # python -m pyqalculate_gui 入口
│   ├── main_window.py          # 主窗口 (235 行)
│   ├── input_widget.py         # 输入组件 (136 行)
│   ├── result_widget.py        # 结果显示 (143 行)
│   ├── plot_widget.py          # 绘图组件 (204 行)
│   └── sidebar_widget.py       # 侧边栏 (307 行)
│
├── pyqalculate_data/           # 数据文件
│   ├── functions.json          # 函数定义
│   ├── units.json              # 单位定义
│   ├── variables.json          # 变量定义
│   ├── datasets.json           # 数据集定义
│   └── prefixes.json           # 前缀定义
│
├── tests/                      # 测试文件
│   ├── test_calculator.py      # Calculator 测试
│   ├── test_functions.py       # 函数测试
│   ├── test_parser.py          # 解析器测试
│   ├── test_number.py          # 数字测试
│   ├── test_unit.py            # 单位测试
│   ├── test_plot.py            # 绘图测试 (27 个测试)
│   ├── test_cli.py             # CLI 测试 (372 行)
│   ├── test_gui.py             # GUI 测试 (73 行)
│   ├── test_integration.py     # 集成测试
│   └── test_qalculate_reference.py  # 参考测试 (79 个)
│
├── docs/                       # 文档
│   ├── development/            # 开发文档
│   │   ├── PROJECT_STRUCTURE.md
│   │   ├── INTERFACE_SPEC.md
│   │   └── CODING_GUIDELINES.md
│   └── gui_analysis/           # GUI 分析文档
│       ├── mainwindow.md
│       ├── expression_edit.md
│       ├── result_view.md
│       ├── history_view.md
│       ├── keypad_analysis.md
│       ├── conversionview_analysis.md
│       ├── menu_dialog_system_analysis.md
│       └── overview.md
│
├── cli.py                      # CLI 入口脚本
├── gui.py                      # GUI 入口脚本
├── demo.py                     # 演示脚本
├── test_runner.py              # 测试运行器
├── run_plot_tests.py           # 绘图测试
├── run_pyqalculate_tests.py    # 对比测试
├── start.bat                   # Windows 启动器
│
├── pyproject.toml              # 项目配置
├── pytest.ini                  # pytest 配置
├── README.md                   # 项目说明
├── LICENSE                     # MIT 许可证
│
├── DEVELOPMENT_PLAN.md         # v1.0 开发计划
├── DEVELOPMENT_PLAN_V2.md      # v2.0 开发计划
├── DEVELOPMENT_PLAN_V2.1.md    # v2.1 开发计划
├── DEVELOPMENT_PLAN_V2.1.1.md  # v2.1.1 开发计划
├── DEVELOPMENT_PLAN_V2.1.2.md  # v2.1.2 开发计划
└── DEVELOPMENT_PLAN_V2.2.md    # v2.2 开发计划 (GUI 重建)
```

---

## 3. 核心模块说明

### 3.1 Calculator (calculator.py)

**职责**: 主计算引擎，协调所有模块

**关键方法**:
```python
class Calculator:
    def parse(self, expression: str) -> MathStructure
    def calculate(self, mstruct: MathStructure, eo: EvaluationOptions) -> MathStructure
    def calculate_and_print(self, expression: str, eo=None, po=None) -> str
    def add_function(self, function: MathFunction) -> bool
    def add_variable(self, variable: Variable) -> bool
    def add_unit(self, unit: Unit) -> bool
    def find_function(self, name: str) -> MathFunction
    def find_variable(self, name: str) -> Variable
    def find_unit(self, name: str) -> Unit
    def load_definitions(self) -> None
    def load_global_definitions(self) -> None
```

**全局实例**:
```python
# pyqalculate/calculator.py
_calculator: Calculator | None = None

def get_calculator() -> Calculator:
    global _calculator
    if _calculator is None:
        _calculator = Calculator()
    return _calculator
```

### 3.2 MathStructure (math_structure.py)

**职责**: 数学表达式的 AST 表示

**结构类型** (StructureType):
- NUMBER: 数字 (int, float, complex)
- SYMBOLIC: 符号 (pi, e, x)
- VARIABLE: 变量引用
- UNIT: 单位引用
- FUNCTION: 函数调用
- ADDITION: 加法 (x + y)
- MULTIPLICATION: 乘法 (x * y)
- POWER: 幂 (x ^ y)
- COMPARISON: 比较 (x = y)
- VECTOR: 向量
- MATRIX: 矩阵
- UNDEFINED: 未定义

**工厂方法**:
```python
MathStructure.from_number(number: Number) -> MathStructure
MathStructure.from_variable(variable: Variable) -> MathStructure
MathStructure.from_unit(unit: Unit, prefix=None) -> MathStructure
MathStructure.from_symbol(symbol: str) -> MathStructure
MathStructure.addition(*children) -> MathStructure
MathStructure.multiplication(*children) -> MathStructure
MathStructure.power(base, exponent) -> MathStructure
MathStructure.vector(*elements) -> MathStructure
MathStructure.matrix(rows) -> MathStructure
```

**SymPy 转换**:
```python
MathStructure.to_sympy() -> sp.Expr
MathStructure.from_sympy(expr: sp.Expr) -> MathStructure
```

### 3.3 Parser (parser.py)

**职责**: 将字符串表达式解析为 MathStructure

**关键函数**:
```python
def parse_expression(expression: str, calculator: Calculator) -> MathStructure
```

**处理流程**:
1. 词法分析 (Tokenization)
2. 语法分析 (Parsing)
3. AST 构建 (MathStructure)

### 3.4 BuiltinFunctions (builtin_functions.py)

**职责**: 151+ 内置数学函数

**函数分类**:
- 三角函数: sin, cos, tan, asin, acos, atan
- 对数函数: log, ln, log2
- 代数函数: solve, factor, expand
- 微积分: diff, integrate, limit
- 矩阵: det, inverse, eigenvalues
- 统计: mean, stdev, median
- 单位转换: convert
- 绘图: plot (FUNCTION_ID_PLOT = 2690)

**注册函数**:
```python
def get_default_registry() -> FunctionRegistry:
    registry = FunctionRegistry()
    registry.register(SinFunction())
    registry.register(CosFunction())
    # ... 151+ 函数
    return registry
```

### 3.5 Number (number.py)

**职责**: 任意精度数字运算

**依赖**: gmpy2 (可选), 后备到 Python float

**关键类**:
```python
class Number:
    def __init__(self, value=0)
    def float_value(self) -> float
    def is_integer(self) -> bool
    def is_rational(self) -> bool
    def is_complex(self) -> bool
```

### 3.6 Unit (unit.py)

**职责**: 单位系统

**单位类型**:
- Unit: 基本单位 (m, kg, s)
- AliasUnit: 别名单位 (meter = m)
- CompositeUnit: 复合单位 (m/s)

**单位数量**: 573+

### 3.7 Plot (plot.py)

**职责**: 函数绘图

**关键类**:
```python
class Plotter:
    def __init__(self, calculator=None)
    def plot(self, expression, x_min=-10, x_max=10, filename=None) -> str
    def plot_multi(self, expressions, x_min=-10, x_max=10, filename=None) -> str
    def plot_data(self, x_values, y_values, filename=None) -> str
    def generate_data(self, expression, x_min=-10, x_max=10) -> PlotData
```

---

## 4. 接口规范

### 4.1 Calculator 公共 API

```python
# 计算
result: str = calculator.calculate_and_print("2 + 3")
result: str = calculator.calculate_and_print("sin(pi/2)")
result: str = calculator.calculate_and_print("5 ft to m")

# 解析
mstruct: MathStructure = calculator.parse("x^2 + 2x + 1")

# 计算 (带选项)
eo = EvaluationOptions()
eo.approximation = ApproximationMode.EXACT
result = calculator.calculate_and_print("sqrt(2)", eo=eo)

# 打印选项
po = PrintOptions()
po.decimal_places = 10
result = calculator.calculate_and_print("pi", po=po)

# 查找对象
func = calculator.find_function("sin")
var = calculator.find_variable("pi")
unit = calculator.find_unit("m")

# 添加对象
calculator.add_function(my_func)
calculator.add_variable(my_var)
calculator.add_unit(my_unit)

# 统计
n_funcs = calculator.count_functions()
n_units = calculator.count_units()
n_vars = calculator.count_variables()
```

### 4.2 MathStructure 公共 API

```python
# 创建
m = MathStructure(42)  # 数字
m = MathStructure.from_number(Number(42))
m = MathStructure.from_symbol("x")
m = MathStructure.from_variable(var)
m = MathStructure.from_unit(unit)

# 组合
m = MathStructure.addition(a, b)  # a + b
m = MathStructure.multiplication(a, b)  # a * b
m = MathStructure.power(base, exp)  # base ^ exp
m = MathStructure.vector(a, b, c)  # [a, b, c]
m = MathStructure.matrix([row1, row2])  # [[a,b],[c,d]]

# 查询
m.is_number() -> bool
m.is_symbolic() -> bool
m.is_variable() -> bool
m.is_unit() -> bool
m.is_function() -> bool
m.is_vector() -> bool
m.is_matrix() -> bool

# 转换
m.to_sympy() -> sp.Expr
MathStructure.from_sympy(expr) -> MathStructure
m.print() -> str
```

### 4.3 Plotter 公共 API

```python
# 单函数绘图
plotter = Plotter(calculator=calc)
result = plotter.plot("x^2", x_min=-5, x_max=5, filename="plot.png")

# 多函数绘图
result = plotter.plot_multi(["sin(x)", "cos(x)"], x_min=0, x_max=6.28)

# 数据绘图
result = plotter.plot_data([1,2,3,4], [1,4,9,16])

# 生成数据
data = plotter.generate_data("x^2", x_min=-5, x_max=5)
# data.x_values, data.y_values
```

### 4.4 CLI 公共 API

```python
# 单次计算
pyqalc "2 + 3"

# 交互模式
pyqalc

# 选项
pyqalc -t "2 + 3"  # 简洁模式
pyqalc -b hex "255"  # 进制转换
pyqalc -s "precision 10"  # 设置选项
```

---

## 5. 数据流

### 5.1 表达式计算流程

```
用户输入 "2 + 3"
    ↓
Parser.parse("2 + 3")
    ↓
MathStructure (ADDITION: [NUMBER(2), NUMBER(3)])
    ↓
Calculator.calculate(mstruct, eo)
    ↓
MathStructure (NUMBER(5))
    ↓
Calculator.print(mstruct, po)
    ↓
"5"
```

### 5.2 单位转换流程

```
用户输入 "5 ft to m"
    ↓
Parser.parse("5 ft to m")
    ↓
MathStructure (UNIT_CONVERSION: [NUMBER(5) * UNIT(ft), UNIT(m)])
    ↓
Calculator.calculate(mstruct, eo)
    ↓
MathStructure (NUMBER(1.524) * UNIT(m))
    ↓
Calculator.print(mstruct, po)
    ↓
"1.524 m"
```

### 5.3 函数调用流程

```
用户输入 "sin(pi/2)"
    ↓
Parser.parse("sin(pi/2)")
    ↓
MathStructure (FUNCTION: sin, [DIVISION: [VARIABLE(pi), NUMBER(2)]])
    ↓
Calculator.calculate(mstruct, eo)
    ↓
SinFunction.calculate(vargs, eo)
    ↓
MathStructure (NUMBER(1))
    ↓
Calculator.print(mstruct, po)
    ↓
"1"
```

---

## 6. 依赖关系

### 6.1 内部依赖

```
calculator.py
├── parser.py
├── math_structure.py
├── builtin_functions.py
├── number.py
├── unit.py
├── variable.py
├── function.py
├── dataset.py
├── datetime_ext.py
├── definitions.py
└── plot.py

math_structure.py
├── number.py
├── unit.py
├── variable.py
├── function.py
└── types.py

builtin_functions.py
├── math_structure.py
├── number.py
└── types.py
```

### 6.2 外部依赖

**必需**:
- sympy: 符号计算
- numpy: 数值计算

**可选**:
- gmpy2: 任意精度 (推荐)
- matplotlib: 绘图 (推荐)

---

## 7. 测试规范

### 7.1 测试文件命名

- `test_*.py` - pytest 测试文件
- `*_test.py` - 备选命名

### 7.2 测试结构

```python
import pytest
from pyqalculate.calculator import Calculator

@pytest.fixture
def calc():
    c = Calculator()
    c.load_definitions()
    return c

class TestFeature:
    def test_basic(self, calc):
        result = calc.calculate_and_print("2 + 3")
        assert result == "5"
    
    def test_edge_case(self, calc):
        result = calc.calculate_and_print("0 / 0")
        assert "undefined" in result.lower()
```

### 7.3 测试运行

```bash
# 运行所有测试
pytest tests -v

# 运行特定测试
pytest tests/test_calculator.py -v

# 运行带覆盖率
pytest tests --cov=pyqalculate
```

---

## 8. 构建和发布

### 8.1 安装

```bash
# 开发安装
pip install -e .

# 生产安装
pip install .
```

### 8.2 依赖安装

```bash
# 基础依赖
pip install sympy numpy

# 推荐依赖
pip install gmpy2 matplotlib

# 开发依赖
pip install pytest pytest-cov
```

### 8.3 发布

```bash
# 构建
python -m build

# 上传
twine upload dist/*
```

---

## 9. 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1.0 | 2026-06 | 核心库、CLI、基础 GUI |
| v2.0 | 2026-06 | 微积分、代数、统计、绘图 |
| v2.1 | 2026-06 | 79/79 参考测试通过 |
| v2.1.1 | 2026-06 | 区间算术、相关系数修正 |
| v2.1.2 | 2026-06 | 绘图集成 |
| v2.2 | 开发中 | GUI 重建、CSV 支持 |

---

## 10. 开发指南

### 10.1 代码风格

- PEP 8 规范
- 类型注解 (Type Hints)
- 文档字符串 (Docstrings)
- 最大行宽 88 字符

### 10.2 Git 规范

- 提交信息: `type: description`
- 类型: feat, fix, docs, test, refactor
- 分支: master (稳定), dev (开发)

### 10.3 测试要求

- 新功能必须有测试
- 测试覆盖率 > 80%
- 所有测试通过才能提交

---

*文档版本: 1.0*  
*最后更新: 2026-06-21*
