# ui/rename_frame.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from core.renamer import sequential_rename


class RenameFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        parent.add(self, text="連番化")
        self.status_var = None
        self.setup_ui()

    def set_status(self, status_var):
        self.status_var = status_var

    def setup_ui(self):
        title = ttk.Label(self, text="画像を連番リネーム", font=("Meiryo", 14, "bold"))
        title.pack(pady=10)

        # 対象フォルダ
        dir_frame = ttk.Frame(self)
        dir_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(dir_frame, text="フォルダ:").pack(anchor=tk.W)
        self.entry_dir = ttk.Entry(dir_frame, state="readonly")
        self.entry_dir.pack(fill=tk.X, pady=2)
        ttk.Button(dir_frame, text="選択", command=self.select_dir).pack(anchor=tk.E)

        # 頭文字
        prefix_frame = ttk.Frame(self)
        prefix_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(prefix_frame, text="頭文字（オプション）:").pack(anchor=tk.W)
        self.prefix_var = tk.StringVar()
        ttk.Entry(prefix_frame, textvariable=self.prefix_var).pack(fill=tk.X)

        # ソート基準
        sort_frame = ttk.Frame(self)
        sort_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(sort_frame, text="ソート基準:").pack(anchor=tk.W)
        self.sort_var = tk.StringVar(value="name")
        sorts = [
            ("ファイル名", "name"),
            ("サイズ順", "size"),
            ("更新日時", "date"),
            ("ランダム", "random")
        ]
        for text, val in sorts:
            rb = ttk.Radiobutton(sort_frame, text=text, value=val, variable=self.sort_var)
            rb.pack(anchor=tk.W)

        # 拡張子フィルタ
        filter_frame = ttk.Frame(self)
        filter_frame.pack(pady=10, fill=tk.X, padx=20)
        ttk.Label(filter_frame, text="拡張子（カンマ区切り）:").pack(anchor=tk.W)
        self.filter_var = tk.StringVar(value=".png,.jpg,.webp,jpeg")
        ttk.Entry(filter_frame, textvariable=self.filter_var).pack(fill=tk.X)
        ttk.Label(filter_frame, text=".png,.webp のように指定", foreground="gray").pack(anchor=tk.W)

        # 実行ボタン
        ttk.Button(self, text="連番化実行", command=self.rename).pack(pady=20)

    def select_dir(self):
        path = filedialog.askdirectory(title="リネーム対象フォルダ")
        if path:
            self.entry_dir.config(state="normal")
            self.entry_dir.delete(0, tk.END)
            self.entry_dir.insert(0, path)
            self.entry_dir.config(state="readonly")

    def rename(self):
        dir_path = self.entry_dir.get()
        if not dir_path:
            messagebox.showwarning("警告", "フォルダ未選択")
            return

        target_dir = Path(dir_path)
        if not target_dir.is_dir():
            messagebox.showerror("エラー", "フォルダが存在しません")
            return

        prefix = self.prefix_var.get().strip()
        if prefix and not prefix.replace("_", "").isalnum():
            messagebox.showwarning("警告", "頭文字は英数字と_のみ")
            return

        # 拡張子解析
        raw_exts = [e.strip().lower() for e in self.filter_var.get().split(",") if e.strip()]
        valid_exts = {f".{e}" if not e.startswith(".") else e for e in raw_exts}

        files = [f for f in target_dir.iterdir() if f.is_file() and f.suffix.lower() in valid_exts]
        if not files:
            messagebox.showinfo("情報", "対象ファイルがありません")
            return

        # 確認ダイアログ
        sort_name = {"name": "名前", "size": "サイズ", "date": "更新日時", "random": "ランダム"}[self.sort_var.get()]
        confirmed = messagebox.askyesno(
            "確認",
            f"{len(files)}件を{sort_name}順に「{prefix}001～」とリネームします\nよろしいですか？"
        )
        if not confirmed:
            return

        # 実行
        try:
            generator = sequential_rename(files, prefix, self.sort_var.get())
            renamed_count = 0
            fail_list = []

            for old_path, new_path in generator:
                try:
                    old_path.rename(new_path)
                    renamed_count += 1
                except Exception as e:
                    fail_list.append(f"{old_path.name}: {e}")

            msg = f"成功: {renamed_count}"
            if fail_list:
                msg += f"\n失敗: {len(fail_list)}\n\n" + "\n".join(fail_list[:10])
            messagebox.showinfo("結果", msg)

            if self.status_var:
                self.status_var.set(f"リネーム完了: {renamed_count}/{len(files)}")

        except Exception as e:
            messagebox.showerror("エラー", f"予期しないエラー: {e}")