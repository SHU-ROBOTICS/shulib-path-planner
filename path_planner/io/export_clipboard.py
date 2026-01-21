"""
Clipboard operations for exporting code.
"""

import tkinter as tk
from typing import Optional


def copy_to_clipboard(text: str, root: Optional[tk.Tk] = None) -> bool:
    """
    Copy text to system clipboard.
    
    Args:
        text: Text to copy
        root: Tkinter root window (creates temporary one if None)
    
    Returns:
        True if successful
    """
    try:
        if root is None:
            root = tk.Tk()
            root.withdraw()
            cleanup = True
        else:
            cleanup = False
        
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        
        if cleanup:
            root.destroy()
        
        return True
    
    except Exception as e:
        print(f"Clipboard error: {e}")
        return False


def get_from_clipboard(root: Optional[tk.Tk] = None) -> Optional[str]:
    """
    Get text from system clipboard.
    
    Args:
        root: Tkinter root window
    
    Returns:
        Clipboard text, or None if empty/error
    """
    try:
        if root is None:
            root = tk.Tk()
            root.withdraw()
            cleanup = True
        else:
            cleanup = False
        
        text = root.clipboard_get()
        
        if cleanup:
            root.destroy()
        
        return text
    
    except tk.TclError:
        return None
    except Exception as e:
        print(f"Clipboard error: {e}")
        return None