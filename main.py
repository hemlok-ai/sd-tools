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
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        self.create_widgets()

    def create_widgets(self):
        # タブ管理
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # タブ追加
        self.tab_convert = self.create_single_convert_tab()      # 個別変換
        self.tab_batch = self.create_batch_convert_tab()         # 一括変換
        self.tab_rename = self.create_rename_tab()               # 連番化
        self.tab_compare = self.add_stub_tab("画像比較")          # 未実装
        self.tab_meta = self.add_stub_tab("メタ情報")             # 未実装

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_stub_tab(self, title: str):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        label = ttk.Label(frame, text=f"{title} 機能は準備中...", font=("Meiryo", 12))
        label.pack(pady=50)
        return frame

    # ========================================
    # タブ1: 個別変換（1ファイル）
    # ========================================
    def create_single_convert_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="個別変換")

        title = ttk.Label(frame, text="単一ファイルの変換", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 入力ファイル
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(input_frame, text="入力ファイル:").pack(anchor=tk.W)
        self.entry_single_input = ttk.Entry(input_frame, state="readonly")
        self.entry_single_input.pack(fill=tk.X, pady=2)
        btn_select = ttk.Button(input_frame, text="選択", command=self.select_single_file)
        btn_select.pack(anchor=tk.E, pady=2)

        # 出力形式
        format_frame = ttk.Frame(frame)
        format_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(format_frame, text="出力形式:").pack(anchor=tk.W)
        self.single_format_var = tk.StringVar(value="jpg")
        formats = [("PNG", "png"), ("WebP", "webp"), ("JPG（圧縮）", "jpg")]
        for text, value in formats:
            rb = ttk.Radiobutton(format_frame, text=text, value=value, variable=self.single_format_var)
            rb.pack(anchor=tk.W)

        # JPG品質
        quality_frame = ttk.Frame(frame)
        quality_frame.pack(pady=5, fill=tk.X, padx=20)
        ttk.Label(quality_frame, text="JPG品質 (1-95):").pack(anchor=tk.W)
        self.single_quality_var = tk.IntVar(value=85)
        scale = ttk.Scale(quality_frame, from_=1, to_=95, variable=self.single_quality_var, orient=tk.HORIZONTAL)
        scale.pack(fill=tk.X)
        self.quality_label_single = ttk.Label(quality_frame, text=str(self.single_quality_var.get()))
        self.single_quality_var.trace("w", lambda *args: self.quality_label_single.config(
            text=str(self.single_quality_var.get())))
        self.quality_label_single.pack()

        # 実行ボタン
        convert_btn = ttk.Button(frame, text="変換を実行", command=self.convert_single_image)
        convert_btn.pack(pady=20)

        return frame

    def select_single_file(self):
        path = filedialog.askopenfilename(
            filetypes=[
                ("Images", "*.png *.webp *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        if path:
            self.entry_single_input.config(state="normal")
            self.entry_single_input.delete(0, tk.END)
            self.entry_single_input.insert(0, path)
            self.entry_single_input.config(state="readonly")
            self.status_var.set(f"選択: {Path(path).name}")

    def convert_single_image(self):
        input_path_str = self.entry_single_input.get()
        if not input_path_str:
            messagebox.showwarning("警告", "ファイルが選択されていません。")
            return

        input_path = Path(input_path_str)
        if not input_path.exists():
            messagebox.showerror("エラー", "ファイルが存在しません。")
            return

        output_format = self.single_format_var.get()

        # JPG変換時は警告（透過消失）
        if output_format == "jpg":
            with Image.open(input_path) as img:
                if img.mode in ("RGBA", "LA", "P"):
                    confirmed = messagebox.askyesno(
                        "確認",
                        "JPGは透過をサポートしていません。\n"
                        "変換すると透過部分が白または黒になります。\n\n"
                        "本当に変換しますか？"
                    )
                    if not confirmed:
                        self.status_var.set("変換キャンセル")
                        return

        # フォーマットマッピング
        ext_map = {"png": ".png", "webp": ".webp", "jpg": ".jpg"}
        format_map = {"png": "PNG", "webp": "WEBP", "jpg": "JPEG"}

        output_path = filedialog.asksaveasfilename(
            title="保存先を選択",
            initialfile=f"converted_{input_path.stem}{ext_map[output_format]}",
            defaultextension=ext_map[output_format],
            filetypes=[(f"{output_format.upper()} files", f"*{ext_map[output_format]}")]
        )
        if not output_path:
            return

        output_path = Path(output_path)
        self._save_image(input_path, output_path, output_format, format_map)

    # ========================================
    # タブ2: 一括変換（フォルダ内すべて）
    # ========================================
    def create_batch_convert_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="一括変換")

        title = ttk.Label(frame, text="フォルダ内の画像を一括変換", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 入力フォルダ
        input_frame = ttk.Frame(frame)
        input_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(input_frame, text="入力フォルダ:").pack(anchor=tk.W)
        self.entry_batch_input = ttk.Entry(input_frame, state="readonly")
        self.entry_batch_input.pack(fill=tk.X, pady=2)
        btn_in = ttk.Button(input_frame, text="選択", command=self.select_batch_input)
        btn_in.pack(anchor=tk.E, pady=2)

        # 出力フォルダ
        output_frame = ttk.Frame(frame)
        output_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(output_frame, text="出力フォルダ:").pack(anchor=tk.W)
        self.entry_batch_output = ttk.Entry(output_frame, state="readonly")
        self.entry_batch_output.pack(fill=tk.X, pady=2)
        btn_out = ttk.Button(output_frame, text="選択", command=self.select_batch_output)
        btn_out.pack(anchor=tk.E, pady=2)

        # 出力形式
        fmt_frame = ttk.Frame(frame)
        fmt_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(fmt_frame, text="出力形式:").pack(anchor=tk.W)
        self.batch_format_var = tk.StringVar(value="jpg")
        formats = [("PNG", "png"), ("WebP", "webp"), ("JPG", "jpg")]
        for text, value in formats:
            rb = ttk.Radiobutton(fmt_frame, text=text, value=value, variable=self.batch_format_var)
            rb.pack(anchor=tk.W)

        # 品質
        q_frame = ttk.Frame(frame)
        q_frame.pack(pady=5, fill=tk.X, padx=20)
        ttk.Label(q_frame, text="品質 (1-95):").pack(anchor=tk.W)
        self.batch_quality_var = tk.IntVar(value=85)
        scale = ttk.Scale(q_frame, from_=1, to_=95, variable=self.batch_quality_var, orient=tk.HORIZONTAL)
        scale.pack(fill=tk.X)
        ttk.Label(q_frame, textvariable=self.batch_quality_var).pack(anchor=tk.W)

        # 実行ボタン
        convert_btn = ttk.Button(frame, text="一括変換を実行", command=self.convert_batch_images)
        convert_btn.pack(pady=20)

        return frame

    def select_batch_input(self):
        path = filedialog.askdirectory(title="入力フォルダを選択")
        if path:
            self.entry_batch_input.config(state="normal")
            self.entry_batch_input.delete(0, tk.END)
            self.entry_batch_input.insert(0, path)
            self.entry_batch_input.config(state="readonly")

    def select_batch_output(self):
        path = filedialog.askdirectory(title="出力フォルダを選択")
        if path:
            self.entry_batch_output.config(state="normal")
            self.entry_batch_output.delete(0, tk.END)
            self.entry_batch_output.insert(0, path)
            self.entry_batch_output.config(state="readonly")

    def convert_batch_images(self):
        input_dir_str = self.entry_batch_input.get()
        output_dir_str = self.entry_batch_output.get()
        output_format = self.batch_format_var.get()

        if not input_dir_str or not output_dir_str:
            messagebox.showwarning("警告", "入力または出力フォルダが未設定です。")
            return

        input_dir = Path(input_dir_str)
        output_dir = Path(output_dir_str)

        if not input_dir.exists():
            messagebox.showerror("エラー", "入力フォルダが存在しません。")
            return

        output_dir.mkdir(exist_ok=True)

        # 拡張子フィルタ
        supported_exts = {".png", ".webp", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}
        image_files = [f for f in input_dir.iterdir() if f.suffix.lower() in supported_exts and f.is_file()]

        if not image_files:
            messagebox.showinfo("情報", "対応する画像ファイルが見つかりません。")
            return

        # JPG変換で透過があるかチェック（サンプル1枚だけ確認）
        check_file = image_files[0]
        if output_format == "jpg":
            try:
                with Image.open(check_file) as img:
                    if img.mode in ("RGBA", "LA", "P"):
                        confirmed = messagebox.askyesno(
                            "確認",
                            f"JPGは透過をサポートしません。\n"
                            f"選択された画像（例: {check_file.name}）の透過が失われます。\n\n"
                            "本当に一括変換しますか？"
                        )
                        if not confirmed:
                            self.status_var.set("一括変換キャンセル")
                            return
            except Exception:
                pass  # 続行

        # フォーマットマッピング
        ext_map = {"png": ".png", "webp": ".webp", "jpg": ".jpg"}
        format_map = {"png": "PNG", "webp": "WEBP", "jpg": "JPEG"}

        success_count = 0
        fail_list = []

        self.status_var.set("一括変換中...")
        self.root.update_idletasks()

        for img_file in image_files:
            try:
                output_path = output_dir / f"{img_file.stem}_converted{ext_map[output_format]}"
                self._save_image(img_file, output_path, output_format, format_map)
                success_count += 1
            except Exception as e:
                fail_list.append(f"{img_file.name}: {str(e)}")

        self.status_var.set(f"一括変換完了: {success_count}/{len(image_files)} 成功")
        msg = f"成功: {success_count}\n失敗: {len(fail_list)}"
        if fail_list:
            msg += "\n\n失敗リスト:\n" + "\n".join(fail_list[:10])
            if len(fail_list) > 10:
                msg += f"\n...他{len(fail_list)-10}件"
        messagebox.showinfo("結果", msg)

    # ========================================
    # タブ3: 連番化（頭文字対応）
    # ========================================
    def create_rename_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="連番化")

        title = ttk.Label(frame, text="フォルダ内の画像を連番リネーム", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 対象フォルダ
        dir_frame = ttk.Frame(frame)
        dir_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(dir_frame, text="対象フォルダ:").pack(anchor=tk.W)
        self.entry_rename_dir = ttk.Entry(dir_frame, state="readonly")
        self.entry_rename_dir.pack(fill=tk.X, pady=2)
        btn_dir = ttk.Button(dir_frame, text="選択", command=self.select_rename_dir)
        btn_dir.pack(anchor=tk.E, pady=2)

        # 頭文字
        prefix_frame = ttk.Frame(frame)
        prefix_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(prefix_frame, text="頭文字（オプション）:").pack(anchor=tk.W)
        self.prefix_var = tk.StringVar()
        entry_prefix = ttk.Entry(prefix_frame, textvariable=self.prefix_var)
        entry_prefix.pack(fill=tk.X)

        # 拡張子フィルタ
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(filter_frame, text="対象拡張子:").pack(anchor=tk.W)
        self.filter_var = tk.StringVar(value=".png,.webp,.jpg,jpeg")
        entry_filter = ttk.Entry(filter_frame, textvariable=self.filter_var)
        entry_filter.pack(fill=tk.X)
        ttk.Label(filter_frame, text="カンマ区切り（例: .png,.jpg）", foreground="gray").pack(anchor=tk.W)

        # 実行ボタン
        rename_btn = ttk.Button(frame, text="連番化を実行", command=self.rename_sequentially)
        rename_btn.pack(pady=20)

        return frame

    def select_rename_dir(self):
        path = filedialog.askdirectory(title="リネーム対象フォルダを選択")
        if path:
            self.entry_rename_dir.config(state="normal")
            self.entry_rename_dir.delete(0, tk.END)
            self.entry_rename_dir.insert(0, path)
            self.entry_rename_dir.config(state="readonly")

    def rename_sequentially(self):
        dir_str = self.entry_rename_dir.get()
        if not dir_str:
            messagebox.showwarning("警告", "フォルダが選択されていません。")
            return

        target_dir = Path(dir_str)
        if not target_dir.exists():
            messagebox.showerror("エラー", "フォルダが存在しません。")
            return

        prefix = self.prefix_var.get().strip()
        if prefix and not prefix.replace("_", "").isalnum():
            messagebox.showwarning("警告", "頭文字は英数字とアンダースコアのみ使用可。")
            return

        # 拡張子リスト
        raw_exts = [e.strip().lower() for e in self.filter_var.get().split(",") if e.strip()]
        valid_exts = {f".{e}" if not e.startswith('.') else e for e in raw_exts}

        files = [f for f in target_dir.iterdir() if f.suffix.lower() in valid_exts and f.is_file()]
        files.sort(key=lambda x: x.name)

        if not files:
            messagebox.showinfo("情報", "対象ファイルがありません。")
            return

        # 確認ダイアログ
        confirmed = messagebox.askyesno(
            "確認",
            f"{len(files)}個のファイルを連番リネームします。\n"
            f"例: {prefix}001{files[0].suffix}\n\n"
            "よろしいですか？"
        )
        if not confirmed:
            return

        # リネーム実行
        renamed_count = 0
        fail_list = []
        for i, file in enumerate(files, 1):
            new_name = f"{prefix}{i:03d}{file.suffix}"
            new_path = file.parent / new_name
            try:
                file.rename(new_path)
                renamed_count += 1
            except Exception as e:
                fail_list.append(f"{file.name} → {new_name}: {str(e)}")

        self.status_var.set(f"リネーム完了: {renamed_count}/{len(files)}")
        msg = f"成功: {renamed_count}"
        if fail_list:
            msg += f"\n失敗: {len(fail_list)}\n\n" + "\n".join(fail_list[:10])
        messagebox.showinfo("結果", msg)

    # ========================================
    # 共通関数: 画像保存
    # ========================================
    def _save_image(self, input_path: Path, output_path: Path, output_format: str, format_map: dict):
        """共通の保存処理"""
        with Image.open(input_path) as img:
            if output_format == "jpg" and img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGB")

            save_kwargs = {}
            if output_format in ("webp", "jpg"):
                quality_key = "quality" if output_format == "webp" else "quality"
                save_kwargs[quality_key] = self._get_quality(output_format)
                if output_format == "jpg":
                    save_kwargs["optimize"] = True

            img.save(output_path, format=format_map[output_format], **save_kwargs)

    def _get_quality(self, fmt: str) -> int:
        if fmt == "jpg":
            return getattr(self, "single_quality_var", None) and self.single_quality_var.get() \
                or self.batch_quality_var.get()
        elif fmt == "webp":
            return getattr(self, "single_quality_var", None) and self.single_quality_var.get() \
                or self.batch_quality_var.get()
        return 85

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageToolApp(tk.Tk())
    app.run()