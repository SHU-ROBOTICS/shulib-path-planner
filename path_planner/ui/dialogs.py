"""
Dialog boxes for the path planner.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional


class ExportDialog(tk.Toplevel):
    """
    Dialog for exporting paths to C++ code.
    """
    
    def __init__(self, parent, code: str, path_name: str):
        super().__init__(parent)
        
        self.title(f"Export: {path_name}")
        self.geometry("800x600")
        self.transient(parent)
        
        self.code = code
        self.result: Optional[str] = None
        
        self._create_widgets()
        
        # Make modal
        self.grab_set()
        self.focus_set()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Instructions
        ttk.Label(
            self, 
            text="Copy this code to your autonomous file, or save to a file:"
        ).pack(padx=10, pady=5)
        
        # Code display
        code_frame = ttk.Frame(self)
        code_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.code_text = tk.Text(
            code_frame,
            wrap=tk.NONE,
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="#ffffff",
            font=("Consolas", 10)
        )
        self.code_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbars
        y_scroll = ttk.Scrollbar(code_frame, orient=tk.VERTICAL, command=self.code_text.yview)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.code_text.config(yscrollcommand=y_scroll.set)
        
        x_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.code_text.xview)
        x_scroll.pack(fill=tk.X, padx=10)
        self.code_text.config(xscrollcommand=x_scroll.set)
        
        # Insert code
        self.code_text.insert("1.0", self.code)
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Copy to Clipboard", command=self._copy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save to File", command=self._save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=5)
    
    def _copy(self) -> None:
        """Copy code to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.code)
        self.update()
        messagebox.showinfo("Copied", "Code copied to clipboard!")
    
    def _save(self) -> None:
        """Save code to file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".hpp",
            filetypes=[
                ("C++ Header", "*.hpp"),
                ("C++ Source", "*.cpp"),
                ("All Files", "*.*")
            ],
            title="Save Generated Code"
        )
        
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.code)
                messagebox.showinfo("Saved", f"Code saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save:\n{e}")


class AboutDialog(tk.Toplevel):
    """
    About dialog with app information.
    """
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("About shulib Path Planner")
        self.geometry("400x300")
        self.resizable(False, False)
        self.transient(parent)
        
        self._create_widgets()
        
        self.grab_set()
        self.focus_set()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        # Title
        ttk.Label(
            self,
            text="shulib Path Planner",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # Version
        ttk.Label(
            self,
            text="Version 1.0.0"
        ).pack()
        
        # Description
        ttk.Label(
            self,
            text="Visual autonomous path planning tool\nfor VEX V5 Robotics",
            justify=tk.CENTER
        ).pack(pady=10)
        
        # Credits
        ttk.Label(
            self,
            text="Seton Hall University VEX Robotics Team",
            foreground="gray"
        ).pack(pady=10)
        
        # Close button
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=20)


class SeasonSelectDialog(tk.Toplevel):
    """
    Dialog for selecting a season when creating a new project.
    """
    
    def __init__(self, parent, seasons: list[str]):
        super().__init__(parent)
        
        self.title("Select Season")
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
        
        self.seasons = seasons
        self.result: Optional[str] = None
        
        self._create_widgets()
        
        self.grab_set()
        self.focus_set()
        self.wait_window()
    
    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        ttk.Label(self, text="Select season for new project:").pack(pady=10)
        
        self.season_var = tk.StringVar()
        if self.seasons:
            self.season_var.set(self.seasons[0])
        
        season_combo = ttk.Combobox(
            self,
            textvariable=self.season_var,
            values=self.seasons,
            state="readonly",
            width=25
        )
        season_combo.pack(pady=10)
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Create", command=self._ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
    
    def _ok(self) -> None:
        """Confirm selection."""
        self.result = self.season_var.get()
        self.destroy()
    
    def _cancel(self) -> None:
        """Cancel dialog."""
        self.result = None
        self.destroy()


def ask_save_changes(parent) -> Optional[bool]:
    """
    Ask user if they want to save changes.
    
    Returns:
        True = save, False = don't save, None = cancel
    """
    result = messagebox.askyesnocancel(
        "Unsaved Changes",
        "Do you want to save changes before continuing?",
        parent=parent
    )
    return result


def show_error(parent, title: str, message: str) -> None:
    """Show an error dialog."""
    messagebox.showerror(title, message, parent=parent)


def show_info(parent, title: str, message: str) -> None:
    """Show an info dialog."""
    messagebox.showinfo(title, message, parent=parent)