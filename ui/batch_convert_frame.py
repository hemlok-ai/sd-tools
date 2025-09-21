# ui/batch_convert_frame.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from core.batch_converter import batch_convert


class BatchConvertFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.add(self, text="一括変換")
        self.status_var = None
        self.setup_ui()

    def set_status(self, status_var):
        self.status_var = status_var

    def setup_ui(self):
        title = ttk.Label(self, text="フォルダ内の画像を一括変換", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 入力フォルダ
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(input_frame, text="入力フォルダ:").pack(anchor=tk.W)
        self.entry_input = ttk.Entry(input_frame, state="readonly")
        self.entry_input.pack(fill=tk.X, pady=2)
        ttk.Button(input_frame, text="選択", command=self.select_input).pack(anchor=tk.E)

        # 出力フォルダ
        output_frame = ttk.Frame(self)
        output_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(output_frame, text="出力フォルダ:").pack(anchor=tk.W)
        self.entry_output = ttk.Entry(output_frame, state="readonly")
        self.entry_output.pack(fill=tk.X, pady=2)
        ttk.Button(output_frame, text="選択", command=self.select_output).pack(anchor=tk.E)

        # 出力形式
        fmt_frame = ttk.Frame(self)
        fmt_frame.pack(pady=10, padx=20, fill=tk.X)
        ttk.Label(fmt_frame, text="出力形式:").pack(anchor=tk.W)
        self.fmt_var = tk.StringVar(value="jpg")
        for txt, val in [("PNG", "png"), ("WebP", "webp"), ("JPG", "jpg")]:
            rb = ttk.Radiobutton(fmt_frame, text=txt, value=val, variable=self.fmt_var)
            rb.pack(anchor=tk.W)

        # 品質
        q_frame = ttk.Frame(self)
        q_frame.pack(pady=5, padx=20, fill=tk.X)
        ttk.Label(q_frame, text="品質 (1-95):").pack(anchor=tk.W)
        self.quality = tk.IntVar(value=85)
        scale = ttk.Scale(q_frame, from_=1, to_=95, variable=self.quality, orient=tk.HORIZONTAL)
        scale.pack(fill=tk.X)
        ttk.Label(q_frame, textvariable=self.quality).pack(anchor=tk.W)

        # 実行ボタン
        ttk.Button(self, text="一括変換", command=self.start_batch).pack(pady=20)

    def select_input(self):
        path = filedialog.askdirectory(title="入力フォルダを選択")
        if path:
            self.entry_input.config(state="normal")
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, path)
            self.entry_input.config(state="readonly")

    def select_output(self):
        path = filedialog.askdirectory(title="出力フォルダを選択")
        if path:
            self.entry_output.config(state="normal")
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, path)
            self.entry_output.config(state="readonly")

    def start_batch(self):
        input_path = self.entry_input.get()
        output_path = self.entry_output.get()
        output_format = self.fmt_var.get()

        if not input_path or not output_path:
            messagebox.showwarning("警告", "入力・出力フォルダを両方選択してください。")
            return

        input_dir = Path(input_path)
        output_dir = Path(output_path)

        if not input_dir.exists():
            messagebox.showerror("エラー", "入力フォルダが存在しません。")
            return

        # JPG変換時の透過警告（サンプルチェック）
        if output_format == "jpg":
            supported_exts = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
            sample_files = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_exts and f.is_file()]
            if sample_files:
                try:
                    from PIL import Image
                    with Image.open(sample_files[0]) as img:
                        if img.mode in ("RGBA", "LA", "P"):
                            if not messagebox.askyesno("確認", "JPGは透過非対応です。\n一部の画像に透過がありますが、続けますか？"):
                                return
                except Exception:
                    pass

        # 変換実行
        try:
            results = batch_convert(input_dir, output_dir, output_format, self.quality.get())
            msg = f"完了: {results['success']} / {results['total']} 成功"
            if results["failed"]:
                msg += f"\n\n失敗: {len(results['failed'])}件\n" + "\n".join(results["failed"][:10])
                if len(results["failed"]) > 10:
                    msg += f"\n...他{len(results['failed']) - 10}件"
            messagebox.showinfo("結果", msg)

            if self.status_var:
                self.status_var.set(f"一括変換完了: {results['success']}/{results['total']}")

        except Exception as e:
            messagebox.showerror("エラー", f"処理中に例外: {e}")