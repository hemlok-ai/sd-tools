# main.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
from pathlib import Path

Image.MAX_IMAGE_PIXELS = None

class ImageToolApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ImageTool - 画像処理ツール")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        self.create_widgets()

    def create_widgets(self):
        # タブ管理
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # タブ1: 変換機能
        self.tab_convert = self.create_convert_tab()

        # タブ2〜4: 今後実装（スタブ）
        self.tab_rename = self.add_stub_tab("連番化")
        self.tab_compare = self.add_stub_tab("画像比較")
        self.tab_meta = self.add_stub_tab("メタ情報")

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_convert_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="変換 (WebP/PNG/JPG)")

        # タイトル
        title = ttk.Label(frame, text="画像変換ツール", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 説明
        desc = ttk.Label(
            frame,
            text="WebP/PNGの相互変換や、JPGへの変換（圧縮）ができます。",
            wraplength=700
        )
        desc.pack(pady=5)

        # ファイル選択
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=10, fill=tk.X, padx=20)

        ttk.Label(input_frame, text="入力ファイル:").pack(anchor=tk.W)
        self.entry_input = ttk.Entry(input_frame, state="readonly")
        self.entry_input.pack(fill=tk.X, pady=2)

        btn_select = ttk.Button(input_frame, text="選択", command=self.select_file)
        btn_select.pack(anchor=tk.E, pady=2)

        # 出力形式選択
        format_frame = ttk.Frame(frame)
        format_frame.pack(pady=10, fill=tk.X, padx=20)

        ttk.Label(format_frame, text="出力形式:").pack(anchor=tk.W)
        self.format_var = tk.StringVar(value="jpg")
        formats = [("PNG", "png"), ("WebP", "webp"), ("JPG（圧縮）", "jpg")]
        for text, value in formats:
            rb = ttk.Radiobutton(format_frame, text=text, value=value, variable=self.format_var)
            rb.pack(anchor=tk.W)

        # JPG圧縮品質（条件付き表示）
        quality_frame = ttk.Frame(frame)
        quality_frame.pack(pady=5, fill=tk.X, padx=20)
        ttk.Label(quality_frame, text="JPG品質 (1-95):").pack(anchor=tk.W)
        self.quality_var = tk.IntVar(value=85)
        scale = ttk.Scale(quality_frame, from_=1, to_=95, variable=self.quality_var, orient=tk.HORIZONTAL)
        scale.pack(fill=tk.X)
        self.quality_label = ttk.Label(quality_frame, text=f"{self.quality_var.get()}")
        self.quality_var.trace("w", lambda *args: self.quality_label.config(text=str(self.quality_var.get())))
        self.quality_label.pack()

        # 変換ボタン
        convert_btn = ttk.Button(frame, text="変換を実行", command=self.convert_image)
        convert_btn.pack(pady=20)

        return frame

    def add_stub_tab(self, title: str):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        label = ttk.Label(frame, text=f"{title} 機能は準備中...", font=("Meiryo", 12))
        label.pack(pady=50)
        return frame

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="画像を選択",
            filetypes=[
                ("Image files", "*.png *.webp *.jpg *.jpeg *.bmp *.tiff"),
                ("PNG", "*.png"),
                ("WebP", "*.webp"),
                ("JPEG", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.entry_input.config(state="normal")
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, file_path)
            self.entry_input.config(state="readonly")
            self.status_var.set(f"選択済み: {Path(file_path).name}")

    def convert_image(self):
        input_path_str = self.entry_input.get()
        if not input_path_str:
            messagebox.showwarning("警告", "画像ファイルが選択されていません。")
            return

        input_path = Path(input_path_str)
        if not input_path.exists():
            messagebox.showerror("エラー", "ファイルが存在しません。")
            return

        output_format = self.format_var.get()

        # 拡張子とPillowフォーマット名のマッピング
        ext_map = {"png": ".png", "webp": ".webp", "jpg": ".jpg"}
        format_map = {"png": "PNG", "webp": "WEBP", "jpg": "JPEG"}  # ← "JPG" → "JPEG"

        default_ext = ext_map[output_format]

        output_path = filedialog.asksaveasfilename(
            title="保存先を選択",
            initialfile=f"converted_{input_path.stem}{default_ext}",
            defaultextension=default_ext,
            filetypes=[(f"{output_format.upper()} files", f"*{default_ext}")]
        )

        if not output_path:
            return  # キャンセルされた

        output_path = Path(output_path)

        try:
            self.status_var.set("画像を読み込んでいます...")
            self.root.update_idletasks()  # GUI更新

            with Image.open(input_path) as img:
                original_mode = img.mode
                original_size = img.size
                self.status_var.set(f"読み込み完了: {original_size}, {original_mode}")

                # JPGはRGB必須（透過対応）
                if output_format == "jpg":
                    if img.mode in ("RGBA", "LA", "P"):
                        self.status_var.set("カラーモードをRGBに変換中...")
                        img = img.convert("RGB")

                save_kwargs = {}
                if output_format in ("webp", "jpg"):
                    save_kwargs["quality"] = self.quality_var.get()
                    if output_format == "jpg":
                        save_kwargs["optimize"] = True

                self.status_var.set("保存中...")
                self.root.update_idletasks()

                img.save(output_path, format=format_map[output_format], **save_kwargs)

            messagebox.showinfo("成功", f"変換完了！\n保存先: {output_path}")
            self.status_var.set(f"変換完了: {output_path.name}")

        except Exception as e:
            error_msg = str(e)
            if "decompression bomb" in error_msg.lower():
                messagebox.showerror("エラー", "画像が大きすぎるため、処理できません。\n"
                                           "巨大な画像は別ツールで処理してください。")
            else:
                messagebox.showerror("変換エラー", f"エラーが発生しました:\n{error_msg}")
            self.status_var.set("変換失敗")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageToolApp(tk.Tk())
    app.run()