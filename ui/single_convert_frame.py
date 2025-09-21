# ui/single_convert_frame.py
import tkinter as tk
from tkinter import Image, ttk, messagebox, filedialog
from pathlib import Path
from core.converter import convert_image


class SingleConvertFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.add(self, text="個別変換")
        self.status_var = None
        self.setup_ui()

    def set_status(self, status_var):
        self.status_var = status_var

    def setup_ui(self):
        title = ttk.Label(self, text="単一ファイル変換", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 入力
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(input_frame, text="ファイル:").pack(anchor=tk.W)
        self.entry = ttk.Entry(input_frame, state="readonly")
        self.entry.pack(fill=tk.X, pady=2)
        ttk.Button(input_frame, text="選択", command=self.select_file).pack(anchor=tk.E)

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
        ttk.Label(q_frame, text="品質:").pack(anchor=tk.W)
        self.quality = tk.IntVar(value=85)
        ttk.Scale(q_frame, from_=1, to_=95, variable=self.quality, orient=tk.HORIZONTAL).pack(fill=tk.X)
        ttk.Label(q_frame, textvariable=self.quality).pack()

        # 実行
        ttk.Button(self, text="変換", command=self.convert).pack(pady=20)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.webp *.jpeg *.bmp *.tiff")])
        if path:
            self.entry.config(state="normal")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, path)
            self.entry.config(state="readonly")

    def convert(self):
        input_path_str = self.entry.get()
        if not input_path_str:
            messagebox.showwarning("警告", "ファイル未選択")
            return

        input_path = Path(input_path_str)
        output_format = self.fmt_var.get()

        # JPGで透過あり → 警告
        try:
            with Image.open(input_path) as img:
                if output_format == "jpg" and img.mode in ("RGBA", "LA", "P"):
                    if not messagebox.askyesno("確認", "JPGは透過非対応です。よろしいですか？"):
                        return
        except Exception:
            pass

        output_path = filedialog.asksaveasfilename(
            defaultextension=f".{output_format}",
            filetypes=[(f"{output_format.upper()}", f"*.{output_format}")]
        )
        if not output_path:
            return

        try:
            convert_image(input_path, Path(output_path), output_format, self.quality.get())
            messagebox.showinfo("成功", "変換完了！")
            if self.status_var:
                self.status_var.set(f"変換完了: {Path(output_path).name}")
        except Exception as e:
            messagebox.showerror("エラー", f"失敗: {e}")