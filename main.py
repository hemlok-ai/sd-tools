# main.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog


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

        # 各機能のタブを作成（スタブ）
        self.tab_convert = self.add_tab("変換 (WebP/PNG/JPG)")
        self.tab_rename = self.add_tab("連番化")
        self.tab_compare = self.add_tab("画像比較")
        self.tab_meta = self.add_tab("メタ情報")

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def add_tab(self, title: str) -> ttk.Frame:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text=title)
        
        label = ttk.Label(frame, text=f"{title} 機能は準備中...", font=("Meiryo", 12))
        label.pack(pady=50)
        
        btn = ttk.Button(frame, text="テストボタン", command=lambda: messagebox.showinfo("Info", f"{title} が選択されました"))
        btn.pack()
        
        return frame

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ImageToolApp(tk.Tk())
    app.run()