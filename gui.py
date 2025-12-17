import threading
import os
import tempfile
import json
import sys
from datetime import datetime

import arxiv
import pandas as pd
import requests

try:
    import pdfplumber  # type: ignore
except ImportError:
    pdfplumber = None

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import font as tkfont


MAX_RESULTS_LIMIT = 30000


def get_base_dir() -> str:
    """
    获取配置文件等的基础目录：
    - 普通运行：使用当前脚本所在目录；
    - PyInstaller 打包后：使用可执行文件所在目录（可读写），避免写到只读的 bundle 里。
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # 在 PyInstaller 打包环境中
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(get_base_dir(), "gui_config.json")


def log(msg: str, text_widget: ScrolledText):
    text_widget.insert(tk.END, msg + "\n")
    text_widget.see(tk.END)
    text_widget.update_idletasks()


def split_keywords(s: str):
    return [x.strip() for x in s.split(",") if x.strip()]


def match_keywords(text: str, keywords, mode: str) -> bool:
    if not keywords:
        return True
    text = text.lower()
    if mode == "AND":
        return all(k.lower() in text for k in keywords)
    else:
        return any(k.lower() in text for k in keywords)


def pdf_contains_github(pdf_url: str, text_widget: ScrolledText) -> bool:
    if not pdfplumber:
        log("⚠️ 未安装 pdfplumber，仅使用元数据判断 GitHub，跳过 PDF 正文搜索。", text_widget)
        return False

    try:
        resp = requests.get(pdf_url, timeout=60)
        resp.raise_for_status()
    except Exception as e:
        log(f"⚠️ PDF 下载失败，跳过 GitHub 检查: {pdf_url}，错误: {e}", text_widget)
        return False

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name

        text_parts = []
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)

        full_text = "\n".join(text_parts).lower()
        return "github.com" in full_text
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def download_pdf(pdf_url: str, save_dir: str, filename_hint: str, text_widget: ScrolledText):
    ensure_dir(save_dir)
    try:
        resp = requests.get(pdf_url, timeout=60)
        resp.raise_for_status()
    except Exception as e:
        log(f"⚠️ PDF 下载失败，跳过下载: {pdf_url}，错误: {e}", text_widget)
        return

    safe_name = "".join(c for c in filename_hint if c.isalnum() or c in " _-")[:100]
    if not safe_name:
        safe_name = "paper"
    filename = f"{safe_name}.pdf"
    full_path = os.path.join(save_dir, filename)

    # 避免重名覆盖
    base, ext = os.path.splitext(full_path)
    idx = 1
    while os.path.exists(full_path):
        full_path = f"{base}_{idx}{ext}"
        idx += 1

    with open(full_path, "wb") as f:
        f.write(resp.content)

    log(f"⬇️ 已下载: {full_path}", text_widget)


def run_search(comment_text: str,
               max_results: int,
               title_keywords_str: str,
               title_mode: str,
               abs_keywords_str: str,
               abs_mode: str,
               require_github: bool,
               download_pdfs: bool,
               output_dir: str,
               text_widget: ScrolledText):
    try:
        log("开始检索 arXiv，请稍候...", text_widget)

        # 1. 构造 query（只基于 comment）
        if comment_text.strip():
            query = f'co:"{comment_text.strip()}"'
        else:
            query = "all:time"  # 防止空查询，给一个宽泛条件
            log("⚠️ 未填写 comment 关键字，将使用一个非常宽泛的查询（all:time），后续完全依赖本地过滤。", text_widget)

        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        title_keywords = split_keywords(title_keywords_str)
        abs_keywords = split_keywords(abs_keywords_str)

        records = []

        for idx, result in enumerate(client.results(search), start=1):
            log(f"扫描结果 {idx}: {result.title}", text_widget)

            title = result.title or ""
            summary = result.summary or ""
            comment = result.comment or ""

            if not match_keywords(title, title_keywords, title_mode):
                continue
            if not match_keywords(summary, abs_keywords, abs_mode):
                continue

            # 判断是否需要 GitHub
            has_github = False
            meta_text = " ".join([title, summary, comment, result.pdf_url or ""]).lower()
            if "github.com" in meta_text:
                has_github = True
            elif require_github:
                # 需要 GitHub，但元数据里没有，则去 PDF 里找
                if pdf_contains_github(result.pdf_url, text_widget):
                    has_github = True

            if require_github and not has_github:
                log(f"⚪ 未检测到 GitHub 链接（非开源或未注明），跳过: {title}", text_widget)
                continue

            # 到这里认为是保留论文
            log(f"✅ 命中论文: {title}", text_widget)

            # 如需下载 PDF
            if download_pdfs and (not require_github or has_github):
                download_pdf(result.pdf_url, output_dir, title, text_widget)

            records.append({
                "Title": title,
                "Authors": ", ".join([a.name for a in result.authors]),
                "PDF Link": result.pdf_url,
                "Published Date": result.published.strftime("%Y-%m-%d"),
                "Categories": ", ".join(result.categories),
                "Comments": comment,
                "Summary": summary.replace("\n", " "),
                "Has GitHub": has_github,
            })

        if records:
            df = pd.DataFrame(records)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_comment = "".join(
                c for c in comment_text if c.isalnum() or c in " _-"
            ).strip()[:40] or "comment"
            excel_name = f"Arxiv_Search_Result_{safe_comment}_{len(records)}篇_{timestamp}.xlsx"
            excel_path = os.path.join(output_dir or ".", excel_name)
            ensure_dir(os.path.dirname(excel_path))
            df.to_excel(excel_path, index=False)
            log(f"\n🎉 完成！共保留 {len(records)} 篇论文，已导出为 {excel_path}", text_widget)
        else:
            log("\n⚠️ 没有论文满足过滤条件。", text_widget)

    except Exception as e:
        log(f"\n❌ 发生错误: {e}", text_widget)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg: dict):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def main():
    root = tk.Tk()
    root.title("arxiv 论文批量检索助手")

    # 全局字体变大一些，提升可读性
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=14)
    text_font = tkfont.nametofont("TkTextFont")
    text_font.configure(size=14)
    fixed_font = tkfont.nametofont("TkFixedFont")
    fixed_font.configure(size=14)

    # 窗口布局
    frm = ttk.Frame(root, padding=10)
    frm.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # 使中间几列可随窗口大小伸缩，便于手动拉宽文本框
    frm.columnconfigure(1, weight=1)
    frm.columnconfigure(2, weight=1)
    frm.columnconfigure(3, weight=1)

    # max_results（默认使用最大值 30000）
    ttk.Label(frm, text="max_results（最多 30000）:").grid(row=0, column=0, sticky="w")
    max_results_var = tk.StringVar(value=str(MAX_RESULTS_LIMIT))
    max_results_entry = ttk.Entry(frm, textvariable=max_results_var, width=10)
    max_results_entry.grid(row=0, column=1, sticky="w")

    # comment 关键字（默认 NeurIPS 2025）
    ttk.Label(frm, text="comment 中包含:").grid(row=1, column=0, sticky="w")
    comment_var = tk.StringVar(value="NeurIPS 2025")
    comment_entry = ttk.Entry(frm, textvariable=comment_var, width=40)
    comment_entry.grid(row=1, column=1, columnspan=2, sticky="we")
    ttk.Label(
        frm,
        text="示例：AAAI 2026 或 NeurIPS 2025（顶会名称 + 空格 + 年份）",
        foreground="gray"
    ).grid(row=1, column=3, columnspan=2, sticky="w")

    # 标题关键词 + 逻辑（可拉宽，自动换行）
    ttk.Label(frm, text="标题关键词（逗号分隔）:").grid(row=2, column=0, sticky="nw")
    default_title_kws = (
        "time series, time-series, time series forecasting, time-series forecasting, "
        "time series prediction, time-series prediction"
    )
    title_kw_text = tk.Text(frm, width=70, height=3, wrap="word", font=default_font)
    title_kw_text.insert("1.0", default_title_kws)
    # 占用第 1-2 列，给第 3-4 列留位置放“标题逻辑”标签和下拉框
    title_kw_text.grid(row=2, column=1, columnspan=2, sticky="nsew")

    ttk.Label(frm, text="标题逻辑:").grid(row=2, column=3, sticky="e")
    # 默认使用 OR（更宽松，减少漏检）
    title_mode_var = tk.StringVar(value="OR")
    title_mode_cb = ttk.Combobox(frm, textvariable=title_mode_var, values=["AND", "OR"], width=5, state="readonly")
    title_mode_cb.grid(row=2, column=4, sticky="w")

    # 摘要关键词 + 逻辑（可拉宽，自动换行）
    ttk.Label(frm, text="摘要关键词（逗号分隔）:").grid(row=3, column=0, sticky="nw")
    default_abs_kws = (
        "time series, time-series, time series forecasting, time-series forecasting, "
        "time series prediction, time-series prediction, sequence forecasting, "
        "sequential forecasting, temporal forecasting, spatio-temporal forecasting, "
        "spatiotemporal forecasting, multivariate time series, univariate time series, "
        "time series model, time series analysis"
    )
    abs_kw_text = tk.Text(frm, width=70, height=3, wrap="word", font=default_font)
    abs_kw_text.insert("1.0", default_abs_kws)
    # 同样占用第 1-2 列
    abs_kw_text.grid(row=3, column=1, columnspan=2, sticky="nsew")

    ttk.Label(frm, text="摘要逻辑:").grid(row=3, column=3, sticky="e")
    # 默认使用 OR（更宽松，减少漏检）
    abs_mode_var = tk.StringVar(value="OR")
    abs_mode_cb = ttk.Combobox(frm, textvariable=abs_mode_var, values=["AND", "OR"], width=5, state="readonly")
    abs_mode_cb.grid(row=3, column=4, sticky="w")

    # 标题 / 摘要逻辑说明
    logic_help_title = (
        "标题逻辑说明：\n"
        "  AND：标题中需要同时包含上方所有关键词；\n"
        "  OR：标题中包含任意一个关键词即可。\n"
        "示例：填写 time series, forecasting 且选择 AND，表示标题里既要有 time series 也要有 forecasting。"
    )
    ttk.Label(frm, text=logic_help_title, foreground="gray", justify="left").grid(
        row=4, column=0, columnspan=5, sticky="w", pady=(4, 4)
    )

    logic_help_abs = (
        "摘要逻辑说明：\n"
        "  AND：摘要中需要同时包含上方所有关键词；\n"
        "  OR：摘要中包含任意一个关键词即可。\n"
        "建议：如果关键词较多、想多收一些论文，可以选择 OR。"
    )
    ttk.Label(frm, text=logic_help_abs, foreground="gray", justify="left").grid(
        row=5, column=0, columnspan=5, sticky="w", pady=(0, 6)
    )

    # 选项：是否要求开源、是否下载 PDF
    # 默认：只保留含 GitHub（开源）论文，但不自动下载 PDF
    require_github_var = tk.BooleanVar(value=True)
    download_pdf_var = tk.BooleanVar(value=False)

    cb_github = ttk.Checkbutton(frm, text="只保留含 GitHub（开源）论文", variable=require_github_var)
    cb_github.grid(row=6, column=0, columnspan=3, sticky="w")

    cb_download = ttk.Checkbutton(frm, text="批量下载论文 PDF", variable=download_pdf_var)
    cb_download.grid(row=6, column=3, columnspan=2, sticky="w")

    # 下载 / 结果输出目录
    ttk.Label(frm, text="输出目录:").grid(row=7, column=0, sticky="w")
    out_dir_var = tk.StringVar(value=os.getcwd())
    out_dir_entry = ttk.Entry(frm, textvariable=out_dir_var, width=40)
    out_dir_entry.grid(row=7, column=1, columnspan=3, sticky="we")

    def choose_dir():
        d = filedialog.askdirectory(initialdir=out_dir_var.get() or os.getcwd())
        if d:
            out_dir_var.set(d)

    btn_choose_dir = ttk.Button(frm, text="选择目录", command=choose_dir)
    btn_choose_dir.grid(row=7, column=4, sticky="w")

    # 尝试加载上次配置
    last_cfg = load_config()
    if last_cfg:
        max_results_var.set(str(last_cfg.get("max_results", MAX_RESULTS_LIMIT)))
        comment_var.set(last_cfg.get("comment_text", comment_var.get()))
        # 恢复标题 / 摘要关键词文本
        title_kw_text.delete("1.0", tk.END)
        title_kw_text.insert("1.0", last_cfg.get("title_keywords", default_title_kws))
        abs_kw_text.delete("1.0", tk.END)
        abs_kw_text.insert("1.0", last_cfg.get("abs_keywords", default_abs_kws))
        title_mode_var.set(last_cfg.get("title_mode", title_mode_var.get()))
        abs_mode_var.set(last_cfg.get("abs_mode", abs_mode_var.get()))
        require_github_var.set(bool(last_cfg.get("require_github", False)))
        download_pdf_var.set(bool(last_cfg.get("download_pdfs", False)))
        out_dir_var.set(last_cfg.get("output_dir", out_dir_var.get()))

    # 输出区域
    ttk.Label(frm, text="运行日志:").grid(row=8, column=0, sticky="w", pady=(10, 0))
    log_text = ScrolledText(frm, width=100, height=25)
    log_text.grid(row=9, column=0, columnspan=5, sticky="nsew")
    frm.rowconfigure(9, weight=1)

    def start_search():
        try:
            mr = int(max_results_var.get().strip())
        except ValueError:
            messagebox.showerror("错误", "max_results 必须是整数。")
            return
        if mr <= 0:
            messagebox.showerror("错误", "max_results 必须大于 0。")
            return
        if mr > MAX_RESULTS_LIMIT:
            mr = MAX_RESULTS_LIMIT
            max_results_var.set(str(MAX_RESULTS_LIMIT))
            messagebox.showinfo("提示", f"max_results 已限制为最大值 {MAX_RESULTS_LIMIT}。")

        comment_text = comment_var.get()
        title_kws = title_kw_text.get("1.0", tk.END).strip()
        abs_kws = abs_kw_text.get("1.0", tk.END).strip()
        title_mode = title_mode_var.get()
        abs_mode = abs_mode_var.get()
        require_github = require_github_var.get()
        download_pdfs = download_pdf_var.get()
        out_dir = out_dir_var.get() or os.getcwd()

        # 先保存当前配置
        cfg = {
            "max_results": mr,
            "comment_text": comment_text,
            "title_keywords": title_kws,
            "abs_keywords": abs_kws,
            "title_mode": title_mode,
            "abs_mode": abs_mode,
            "require_github": require_github,
            "download_pdfs": download_pdfs,
            "output_dir": out_dir,
        }
        save_config(cfg)

        log_text.delete("1.0", tk.END)

        def worker():
            run_search(
                comment_text=comment_text,
                max_results=mr,
                title_keywords_str=title_kws,
                title_mode=title_mode,
                abs_keywords_str=abs_kws,
                abs_mode=abs_mode,
                require_github=require_github,
                download_pdfs=download_pdfs,
                output_dir=out_dir,
                text_widget=log_text,
            )

        threading.Thread(target=worker, daemon=True).start()

    btn_start = ttk.Button(frm, text="开始检索", command=start_search)
    btn_start.grid(row=0, column=3, columnspan=2, sticky="e")

    root.mainloop()


if __name__ == "__main__":
    main()
