# main.py
"""
ImageTool - 画像処理ツール（メインエントリ）
"""
import tkinter as tk
from ui.single_convert_frame import SingleConvertFrame
from ui.batch_convert_frame import BatchConvertFrame
from ui.rename_frame import RenameFrame
from ui.compare_frame import CompareFrame


class ImageToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ImageTool - 画像処理ツール")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)

        self.create_widgets()

    def create_widgets(self):
        notebook = tk.ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 各機能をフレームとして追加
        SingleConvertFrame(notebook).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        BatchConvertFrame(notebook).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        RenameFrame(notebook).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        CompareFrame(notebook).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ステータスバー
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 各フレームにステータスバーを共有
        for frame in notebook.winfo_children():
            if hasattr(frame, 'set_status'):
                frame.set_status(self.status_var)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageToolApp(root)
    root.mainloop()