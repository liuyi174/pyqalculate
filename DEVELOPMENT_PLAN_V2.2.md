# PyQalculate v2.2 开发规划文档

## 1. 项目概述

**版本**: v2.2  
**目标**: 重建完整 GUI 应用 + 实现 CSV 导入导出功能  
**预计工作量**: 大型工程（5-10 天）  
**当前状态**: v2.1.2 已完成（79/79 参考测试通过，978 单元测试通过）

---

## 2. v2.1.2 回顾

### 已完成功能
- ✅ 核心数学引擎（151+ 内置函数）
- ✅ 单位转换系统（573+ 单位）
- ✅ 物理常数
- ✅ 代数方程求解
- ✅ 微积分（导数、积分、极限）
- ✅ 矩阵运算
- ✅ 统计函数
- ✅ 进制转换
- ✅ 时间日期处理
- ✅ 绘图功能（matplotlib）
- ✅ CLI 模式（pyqalc）
- ✅ 基础 GUI 模式（pyqalculate_gui）

### 测试结果
- 单元测试：978 通过，2 跳过，0 失败
- 参考测试：79/79 通过（100%）
- 绘图测试：7/7 通过

---

## 3. v2.2 开发目标

### 3.1 GUI 重建（主要任务）

原项目 qalculate-gtk 有 90 个源文件，约 30,000+ 行代码。我们需要用 tkinter 重建一个功能完整的 GUI。

#### 核心模块

| 模块 | 原项目代码 | 优先级 | 预计工作量 |
|------|-----------|--------|-----------|
| 主窗口 | mainwindow.cc (9,300 行) | P0 | 2-3 天 |
| 表达式输入 | expressionedit.cc (2,079 行) | P0 | 1 天 |
| 结果显示 | resultview.cc (1,458 行) | P0 | 1 天 |
| 历史记录 | historyview.cc (3,798 行) | P1 | 1 天 |
| 键盘 | keypad.cc (3,846 行) | P1 | 1 天 |
| 单位转换 | conversionview.cc (561 行) | P1 | 0.5 天 |
| 菜单栏 | menubar.cc (2,775 行) | P1 | 0.5 天 |
| 绘图对话框 | plotdialog.cc (885 行) | P2 | 0.5 天 |
| 偏好设置 | preferencesdialog.cc (1,228 行) | P2 | 0.5 天 |
| CSV 导入 | importcsvdialog.cc (201 行) | P2 | 0.5 天 |
| CSV 导出 | exportcsvdialog.cc (203 行) | P2 | 0.5 天 |

#### 功能映射

**原项目功能 → pyqalculate 实现**

1. **表达式输入**
   - 原：GtkTextView + GtkTextBuffer
   - 新：tkinter Text 组件
   - 功能：Enter 执行、Escape 清除、上下键历史、Ctrl+Z/Y 撤销重做

2. **结果显示**
   - 原：Cairo 渲染的自定义组件
   - 新：tkinter Canvas 或 Label
   - 功能：自动缩放、格式化显示、右键菜单

3. **历史记录**
   - 原：GtkTreeView + answer()/expression() 函数
   - 新：tkinter Treeview
   - 功能：历史浏览、书签、answer(N) 引用

4. **键盘**
   - 原：49 个按钮，支持左/右/中键点击
   - 新：tkinter Button 网格
   - 功能：数字、运算符、函数、RPN 模式

5. **单位转换**
   - 原：双面板（类别树 + 单位列表）
   - 新：tkinter PanedWindow
   - 功能：类别筛选、单位搜索、实时转换

6. **菜单栏**
   - 原：GtkMenuBar + 动态生成的函数/变量/单位菜单
   - 新：tkinter Menu
   - 功能：文件、编辑、视图、帮助

7. **绘图对话框**
   - 原：Gnuplot 后端
   - 新：matplotlib 嵌入
   - 功能：函数绘图、数据绘图、样式配置

8. **偏好设置**
   - 原：80+ 回调函数
   - 新：tkinter Toplevel + 配置保存
   - 功能：字体、颜色、精度、进制等

### 3.2 CSV 导入导出（次要任务）

原项目通过 Calculator 类实现 CSV 功能：

```cpp
// 导入
bool Calculator::importCSV(MathStructure &mstruct, const char *file_name, 
                           int first_row, string delimiter, vector<string> *headers);
bool Calculator::importCSV(const char *file_name, int first_row, bool headers,
                           string delimiter, bool to_matrix, string name, 
                           string title, string category);

// 导出
bool Calculator::exportCSV(const MathStructure &mstruct, const char *file_name, 
                           string delimiter);
```

**实现计划**：

1. **Calculator.importCSV()** - 使用 Python csv 模块
2. **Calculator.exportCSV()** - 写入 CSV 文件
3. **LoadFunction** - 替换 stub 为真实实现
4. **ExportFunction** - 创建新类
5. **column() 函数** - 从矩阵提取列

---

## 4. 开发任务分解

### 任务 1：创建 GUI 框架 [P0 - 1 天]

**目标**：建立基础 GUI 框架和主窗口

**文件**：
- `pyqalculate_gui/main_window.py` - 重写主窗口
- `pyqalculate_gui/app.py` - 应用程序入口

**实现**：
```python
class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PyQalculate")
        self.root.geometry("800x600")
        
        # 创建主布局
        self.create_menu_bar()
        self.create_expression_input()
        self.create_result_display()
        self.create_keypad()
        self.create_history_panel()
        self.create_status_bar()
```

**验证**：窗口能正常显示，所有组件布局正确

### 任务 2：实现表达式输入 [P0 - 1 天]

**目标**：完整的表达式输入功能

**文件**：
- `pyqalculate_gui/expression_edit.py`

**实现**：
- Enter 执行计算
- Escape 清除输入
- 上下键浏览历史
- Ctrl+Z/Y 撤销重做
- 括号高亮匹配
- 自动补全

**验证**：输入表达式能正确计算并显示结果

### 任务 3：实现结果显示 [P0 - 1 天]

**目标**：格式化显示计算结果

**文件**：
- `pyqalculate_gui/result_view.py`

**实现**：
- 显示表达式和结果
- 支持精确/近似模式切换
- 右键菜单（复制、转换单位等）
- 自动缩放长结果

**验证**：结果正确显示，右键菜单功能正常

### 任务 4：实现历史记录 [P1 - 1 天]

**目标**：历史记录浏览和引用

**文件**：
- `pyqalculate_gui/history_view.py`

**实现**：
- 历史列表显示
- answer(N) 函数支持
- 书签功能
- 历史搜索

**验证**：能浏览历史，answer(N) 能正确引用

### 任务 5：实现键盘 [P1 - 1 天]

**目标**：虚拟键盘

**文件**：
- `pyqalculate_gui/keypad.py`

**实现**：
- 数字键（0-9）
- 运算符（+、-、*、/、^）
- 函数键（sin、cos、tan、log、ln）
- 常量键（π、e）
- 变量键（ans）

**验证**：点击按钮能正确输入对应内容

### 任务 6：实现单位转换 [P1 - 0.5 天]

**目标**：单位转换面板

**文件**：
- `pyqalculate_gui/conversion_view.py`

**实现**：
- 类别树（长度、质量、时间等）
- 单位列表（可筛选）
- 转换结果实时显示

**验证**：能选择类别和单位，转换结果正确

### 任务 7：实现菜单栏 [P1 - 0.5 天]

**目标**：完整菜单系统

**文件**：
- `pyqalculate_gui/menu_bar.py`

**实现**：
- 文件菜单（新建、打开、保存、退出）
- 编辑菜单（撤销、重做、复制、粘贴）
- 视图菜单（精确模式、近似模式）
- 工具菜单（绘图、CSV 导入导出）
- 帮助菜单（关于、帮助）

**验证**：所有菜单项可点击，功能正常

### 任务 8：实现绘图对话框 [P2 - 0.5 天]

**目标**：函数绘图界面

**文件**：
- `pyqalculate_gui/plot_dialog.py`

**实现**：
- 表达式输入
- 范围设置（x_min、x_max）
- 绘图样式配置
- matplotlib 嵌入显示
- 保存为图片

**验证**：能输入表达式并显示绘图结果

### 任务 9：实现偏好设置 [P2 - 0.5 天]

**目标**：设置对话框

**文件**：
- `pyqalculate_gui/preferences_dialog.py`

**实现**：
- 精度设置
- 进制设置
- 字体设置
- 颜色主题
- 其他选项

**验证**：设置能保存并生效

### 任务 10：实现 CSV 导入导出 [P2 - 1 天]

**目标**：CSV 文件处理

**文件**：
- `pyqalculate/calculator.py` - 添加 importCSV/exportCSV
- `pyqalculate/builtin_functions.py` - 实现 LoadFunction/ExportFunction
- `pyqalculate_gui/import_csv_dialog.py`
- `pyqalculate_gui/export_csv_dialog.py`

**实现**：
```python
class Calculator:
    def importCSV(self, filename, first_row=1, headers=True, 
                  delimiter=",", to_matrix=False, name=""):
        """导入 CSV 文件"""
        import csv
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            # ... 解析逻辑
        
    def exportCSV(self, mstruct, filename, delimiter=","):
        """导出为 CSV 文件"""
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter)
            # ... 写入逻辑
```

**验证**：能导入 CSV 为矩阵，能导出矩阵为 CSV

### 任务 11：集成测试 [P0 - 0.5 天]

**目标**：端到端测试

**文件**：
- `tests/test_gui_integration.py`

**测试用例**：
1. 启动 GUI，输入表达式，验证结果
2. 使用键盘输入，验证功能
3. 浏览历史记录，验证 answer(N)
4. 进行单位转换，验证结果
5. 绘制函数图像，验证显示
6. 导入导出 CSV，验证数据完整性

**验证**：所有测试通过

---

## 5. 技术方案

### 5.1 GUI 框架选择

**选择：tkinter**

理由：
- Python 内置，无需额外安装
- 跨平台支持
- 足够实现所有功能
- 学习曲线低

### 5.2 架构设计

```
pyqalculate_gui/
├── __init__.py
├── __main__.py
├── app.py                  # 应用程序入口
├── main_window.py          # 主窗口
├── expression_edit.py      # 表达式输入
├── result_view.py          # 结果显示
├── history_view.py         # 历史记录
├── keypad.py               # 虚拟键盘
├── conversion_view.py      # 单位转换
├── menu_bar.py             # 菜单栏
├── plot_dialog.py          # 绘图对话框
├── preferences_dialog.py   # 偏好设置
├── import_csv_dialog.py    # CSV 导入
├── export_csv_dialog.py    # CSV 导出
└── widgets/                # 自定义组件
    ├── __init__.py
    ├── math_entry.py       # 数学输入框
    ├── result_display.py   # 结果显示组件
    └── keypad_button.py    # 键盘按钮
```

### 5.3 数据流

```
用户输入 → 表达式解析 → Calculator.calculate() → 结果格式化 → 显示
    ↓
历史记录 ← 存储 MathStructure ← 结果对象
    ↓
answer(N) → 从历史获取 MathStructure → 重新计算
```

### 5.4 线程模型

- **主线程**：UI 更新
- **计算线程**：长时间计算（使用 threading）
- **自动计算线程**：实时预览（使用 debounce）

---

## 6. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| tkinter 性能不足 | 低 | 中 | 优化渲染，使用 Canvas 代替 Label |
| 原项目功能过多 | 中 | 高 | 分阶段实现，优先核心功能 |
| CSV 解析复杂 | 低 | 中 | 使用 Python csv 模块 |
| 跨平台兼容性 | 中 | 中 | 测试 Windows/Linux/macOS |

---

## 7. 交付物

### 代码文件
- `pyqalculate_gui/` - 完整 GUI 模块（12 个文件）
- `pyqalculate/calculator.py` - 添加 CSV 方法
- `pyqalculate/builtin_functions.py` - 实现 Load/Export 函数
- `tests/test_gui_integration.py` - 集成测试

### 文档
- `docs/gui_analysis/` - 原项目 GUI 分析（已完成）
- `DEVELOPMENT_PLAN_V2.2.md` - 本文档
- `README.md` - 更新使用说明

### 测试结果
- 单元测试：978+ 通过
- GUI 集成测试：10+ 通过
- CSV 功能测试：5+ 通过

---

## 8. 执行顺序

### 第一阶段：GUI 框架（1-2 天）
1. 任务 1：创建 GUI 框架
2. 任务 2：实现表达式输入
3. 任务 3：实现结果显示

### 第二阶段：核心功能（2-3 天）
4. 任务 4：实现历史记录
5. 任务 5：实现键盘
6. 任务 6：实现单位转换
7. 任务 7：实现菜单栏

### 第三阶段：扩展功能（1-2 天）
8. 任务 8：实现绘图对话框
9. 任务 9：实现偏好设置
10. 任务 10：实现 CSV 导入导出

### 第四阶段：测试和优化（1 天）
11. 任务 11：集成测试
12. 性能优化
13. 文档更新

---

## 9. 验证标准

### GUI 功能验证
- [ ] 窗口正常显示
- [ ] 表达式输入并计算
- [ ] 结果正确显示
- [ ] 历史记录浏览
- [ ] 键盘输入功能
- [ ] 单位转换功能
- [ ] 菜单项可点击
- [ ] 绘图对话框工作
- [ ] 偏好设置保存

### CSV 功能验证
- [ ] 导入 CSV 为矩阵
- [ ] 导入 CSV 为变量
- [ ] 导出矩阵为 CSV
- [ ] 导出变量为 CSV
- [ ] load() 函数工作
- [ ] export() 函数工作

### 测试验证
- [ ] 所有单元测试通过
- [ ] GUI 集成测试通过
- [ ] CSV 功能测试通过
- [ ] 无内存泄漏
- [ ] 响应时间 < 100ms

---

## 10. 总结

v2.2 是一个大型工程，需要重建完整的 GUI 应用并实现 CSV 功能。通过分阶段实施，优先核心功能，可以确保项目按时交付。

**关键成功因素**：
1. 清晰的架构设计
2. 分阶段实施
3. 充分的测试
4. 及时的风险应对

**预计完成时间**：5-10 天

**下一步行动**：开始任务 1 - 创建 GUI 框架
