# arXiv 论文批量检索助手 / arXiv Paper Batch Retrieval Assistant

[English](#english) | [中文](#中文)

---

## English

### 📖 Overview

**arXiv Paper Batch Retrieval Assistant** is a GUI-based tool designed to efficiently search and filter papers from arXiv, specifically tailored for finding time series forecasting papers from top-tier conferences (e.g., AAAI, NeurIPS). It supports filtering by keywords, detecting open-source papers (with GitHub links), and batch downloading PDFs.

### ✨ Features

- **🎯 Conference Filtering**: Search papers by conference name and year (e.g., "AAAI 2026", "NeurIPS 2025")
- **🔍 Flexible Keyword Search**: 
  - Filter by title keywords with AND/OR logic
  - Filter by abstract keywords with AND/OR logic
  - Support for comma-separated multiple keywords
- **💻 Open-Source Detection**: Automatically detect papers with GitHub links (in metadata or PDF content)
- **📥 Batch PDF Download**: Download filtered papers' PDFs in bulk
- **💾 Configuration Persistence**: Automatically save and restore your search settings
- **📊 Excel Export**: Export results to Excel files with detailed metadata
- **🖥️ User-Friendly GUI**: Clean, intuitive interface with real-time progress logging

### 🚀 Quick Start

#### Prerequisites

- Python 3.8+
- Required packages:
  ```bash
  pip install arxiv pandas requests pdfplumber openpyxl
  ```

#### Running the Application

**Option 1: Run from source**
```bash
python gui.py
```

**Option 2: Use pre-built executable**
1. Download the latest release from the [Releases](https://github.com/yangqingyuan-byte/auto_grab_arxiv/releases/tag/exe) page
2. Extract the `arxiv_paper_gui` folder
3. Run `arxiv_paper_gui.exe`

### 📝 Usage Guide

1. **Set max_results**: Maximum number of papers to scan (default: 30000, maximum: 30000)
2. **Enter comment**: Conference name and year (e.g., "AAAI 2026", "NeurIPS 2025")
3. **Configure title keywords**: Comma-separated keywords for title filtering
   - **AND logic**: Title must contain ALL keywords
   - **OR logic**: Title contains ANY keyword
4. **Configure abstract keywords**: Similar to title keywords
5. **Optional filters**:
   - ✅ Check "只保留含 GitHub（开源）论文" to filter only open-source papers
   - ✅ Check "批量下载论文 PDF" to download PDFs automatically
6. **Set output directory**: Where to save Excel results and PDFs
7. **Click "开始检索"**: Start the search process

### 🎯 Example Use Cases

**Find AAAI 2026 time series forecasting papers:**
- Comment: `AAAI 2026`
- Title keywords: `time series, forecasting` (OR logic)
- Abstract keywords: `time series forecasting, temporal forecasting` (OR logic)
- ✅ Check "只保留含 GitHub（开源）论文"

**Find NeurIPS 2025 papers with specific methods:**
- Comment: `NeurIPS 2025`
- Title keywords: `transformer, attention` (AND logic)
- Abstract keywords: `multivariate time series` (OR logic)

### 📦 Building from Source

To build an executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --name arxiv_paper_gui --noconsole gui.py
```

The executable will be generated in `dist/arxiv_paper_gui/`.

### 📁 Project Structure

```
auto_grab_arxiv/
├── gui.py                 # Main GUI application
├── gui_config.json        # Configuration file (auto-generated)
├── README.md             # This file
└── dist/                 # Build output directory (after packaging)
    └── arxiv_paper_gui/  # Packaged executable
```

### ⚙️ Configuration

The application automatically saves your settings to `gui_config.json` in the same directory as the executable (or script). Settings include:
- max_results
- comment text
- title/abstract keywords and logic
- GitHub filter toggle
- PDF download toggle
- Output directory

### 🔧 Technical Details

- **arXiv API**: Uses the `arxiv` Python library for paper retrieval
- **PDF Parsing**: Uses `pdfplumber` to extract text from PDFs for GitHub link detection
- **GUI Framework**: Built with `tkinter` (Python's built-in GUI library)
- **Data Export**: Uses `pandas` and `openpyxl` for Excel file generation

### ⚠️ Notes

- The tool searches arXiv's comment field for conference information. Papers must have their conference name in the comment field to be found.
- PDF parsing for GitHub detection may take time for large batches. Consider filtering by metadata first.
- Empty comment field will use a very broad query (`all:time`), relying entirely on local keyword filtering.

### 📄 License

This project is open source. Feel free to use, modify, and distribute.

### 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

---

## 中文

### 📖 项目简介

**arXiv 论文批量检索助手** 是一个基于图形界面的工具，用于高效搜索和筛选 arXiv 上的论文，特别适用于从顶级会议（如 AAAI、NeurIPS）中查找时间序列预测相关的论文。支持关键词筛选、开源论文检测（GitHub 链接）和批量下载 PDF。

### ✨ 主要功能

- **🎯 会议筛选**：按会议名称和年份搜索论文（如 "AAAI 2026"、"NeurIPS 2025"）
- **🔍 灵活的关键词搜索**：
  - 标题关键词筛选（支持 AND/OR 逻辑）
  - 摘要关键词筛选（支持 AND/OR 逻辑）
  - 支持逗号分隔的多个关键词
- **💻 开源检测**：自动检测包含 GitHub 链接的论文（在元数据或 PDF 正文中）
- **📥 批量 PDF 下载**：批量下载筛选后的论文 PDF
- **💾 配置持久化**：自动保存和恢复搜索设置
- **📊 Excel 导出**：将结果导出为包含详细元数据的 Excel 文件
- **🖥️ 友好的图形界面**：简洁直观的界面，实时显示进度日志

### 🚀 快速开始

#### 环境要求

- Python 3.8+
- 所需依赖包：
  ```bash
  pip install arxiv pandas requests pdfplumber openpyxl
  ```

#### 运行方式

**方式一：从源码运行**
```bash
python gui.py
```

**方式二：使用预编译可执行文件**
1. 从 [Releases](https://github.com/yangqingyuan-byte/auto_grab_arxiv/releases/tag/exe) 页面下载最新版本
2. 解压 `arxiv_paper_gui` 文件夹
3. 运行 `arxiv_paper_gui.exe`

### 📝 使用指南

1. **设置 max_results**：最多扫描的论文数量（默认：30000，最大值：30000）
2. **填写 comment**：会议名称和年份（如 "AAAI 2026"、"NeurIPS 2025"）
3. **配置标题关键词**：逗号分隔的关键词，用于标题筛选
   - **AND 逻辑**：标题必须包含所有关键词
   - **OR 逻辑**：标题包含任意一个关键词即可
4. **配置摘要关键词**：与标题关键词类似
5. **可选筛选**：
   - ✅ 勾选 "只保留含 GitHub（开源）论文" 以仅筛选开源论文
   - ✅ 勾选 "批量下载论文 PDF" 以自动下载 PDF
6. **设置输出目录**：保存 Excel 结果和 PDF 的位置
7. **点击 "开始检索"**：开始搜索过程

### 🎯 使用示例

**查找 AAAI 2026 时间序列预测论文：**
- Comment：`AAAI 2026`
- 标题关键词：`time series, forecasting`（OR 逻辑）
- 摘要关键词：`time series forecasting, temporal forecasting`（OR 逻辑）
- ✅ 勾选 "只保留含 GitHub（开源）论文"

**查找 NeurIPS 2025 特定方法的论文：**
- Comment：`NeurIPS 2025`
- 标题关键词：`transformer, attention`（AND 逻辑）
- 摘要关键词：`multivariate time series`（OR 逻辑）

### 📦 从源码构建

使用 PyInstaller 构建可执行文件：

```bash
pip install pyinstaller
pyinstaller --name arxiv_paper_gui --noconsole gui.py
```

可执行文件将生成在 `dist/arxiv_paper_gui/` 目录中。

### 📁 项目结构

```
auto_grab_arxiv/
├── gui.py                 # 主 GUI 应用程序
├── gui_config.json        # 配置文件（自动生成）
├── README.md             # 本文件
└── dist/                 # 构建输出目录（打包后）
    └── arxiv_paper_gui/  # 打包后的可执行文件
```

### ⚙️ 配置说明

应用程序会自动将设置保存到可执行文件（或脚本）同目录下的 `gui_config.json`。设置包括：
- max_results
- comment 文本
- 标题/摘要关键词和逻辑
- GitHub 筛选开关
- PDF 下载开关
- 输出目录

### 🔧 技术细节

- **arXiv API**：使用 `arxiv` Python 库进行论文检索
- **PDF 解析**：使用 `pdfplumber` 从 PDF 中提取文本以检测 GitHub 链接
- **GUI 框架**：使用 `tkinter`（Python 内置 GUI 库）构建
- **数据导出**：使用 `pandas` 和 `openpyxl` 生成 Excel 文件

### ⚠️ 注意事项

- 工具通过搜索 arXiv 的 comment 字段来查找会议信息。论文必须在 comment 字段中包含会议名称才能被找到。
- 对大批量论文进行 PDF 解析以检测 GitHub 链接可能需要较长时间。建议先通过元数据筛选。
- 如果 comment 字段为空，将使用非常宽泛的查询（`all:time`），完全依赖本地关键词筛选。

### 📄 许可证

本项目为开源项目。欢迎使用、修改和分发。

### 🤝 贡献

欢迎贡献！如有问题或建议，请提交 Issue 或 Pull Request。