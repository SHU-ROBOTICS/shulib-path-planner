"""
Undo/Redo system for the path planner.

Uses a simple command pattern with state snapshots.
"""

import copy
from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class UndoState:
    """A snapshot of application state."""
    description: str
    state: Any  # Deep copy of the state


class UndoManager:
    """
    Manages undo/redo operations.
    
    Uses state snapshots rather than command objects for simplicity.
    """
    
    def __init__(self, max_history: int = 50):
        """
        Initialize the undo manager.
        
        Args:
            max_history: Maximum number of undo states to keep
        """
        self.max_history = max_history
        self.undo_stack: list[UndoState] = []
        self.redo_stack: list[UndoState] = []
        self._on_change_callbacks: list[Callable[[], None]] = []
    
    def save_state(self, state: Any, description: str = "Edit") -> None:
        """
        Save a state snapshot for undo.
        
        Args:
            state: The current state (will be deep copied)
            description: Human-readable description of the action
        """
        # Deep copy to avoid reference issues
        snapshot = UndoState(description=description, state=copy.deepcopy(state))
        self.undo_stack.append(snapshot)
        
        # Clear redo stack (new action invalidates redo history)
        self.redo_stack.clear()
        
        # Limit history size
        while len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        
        self._notify_change()
    
    def undo(self) -> Optional[Any]:
        """
        Undo the last action.
        
        Returns:
            The previous state, or None if nothing to undo
        """
        if not self.can_undo():
            return None
        
        # Pop from undo stack
        current = self.undo_stack.pop()
        
        # Push to redo stack
        self.redo_stack.append(current)
        
        self._notify_change()
        
        # Return the state to restore (one before current)
        if self.undo_stack:
            return copy.deepcopy(self.undo_stack[-1].state)
        return None
    
    def redo(self) -> Optional[Any]:
        """
        Redo the last undone action.
        
        Returns:
            The state to restore, or None if nothing to redo
        """
        if not self.can_redo():
            return None
        
        # Pop from redo stack
        state = self.redo_stack.pop()
        
        # Push back to undo stack
        self.undo_stack.append(state)
        
        self._notify_change()
        
        return copy.deepcopy(state.state)
    
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self.undo_stack) > 1  # Need at least 2 (current + previous)
    
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self.redo_stack) > 0
    
    def get_undo_description(self) -> Optional[str]:
        """Get description of action that would be undone."""
        if self.can_undo():
            return self.undo_stack[-1].description
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """Get description of action that would be redone."""
        if self.can_redo():
            return self.redo_stack[-1].description
        return None
    
    def clear(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._notify_change()
    
    def on_change(self, callback: Callable[[], None]) -> None:
        """
        Register a callback for when undo/redo state changes.
        
        Args:
            callback: Function to call when state changes
        """
        self._on_change_callbacks.append(callback)
    
    def _notify_change(self) -> None:
        """Notify all registered callbacks."""
        for callback in self._on_change_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Undo callback error: {e}")
    
    @property
    def undo_count(self) -> int:
        """Number of available undo operations."""
        return max(0, len(self.undo_stack) - 1)
    
    @property
    def redo_count(self) -> int:
        """Number of available redo operations."""
        return len(self.redo_stack)


class BatchUndoContext:
    """
    Context manager for batching multiple changes into one undo.
    
    Usage:
        with BatchUndoContext(undo_manager, state, "Batch edit"):
            # Make multiple changes
            pass
        # Single undo state saved after all changes
    """
    
    def __init__(self, manager: UndoManager, get_state: Callable[[], Any], description: str):
        """
        Initialize batch context.
        
        Args:
            manager: The UndoManager
            get_state: Function that returns current state
            description: Description for this batch of changes
        """
        self.manager = manager
        self.get_state = get_state
        self.description = description
        self.initial_state = None
    
    def __enter__(self):
        # Save state before changes
        self.initial_state = copy.deepcopy(self.get_state())
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Only save if no exception
        if exc_type is None:
            self.manager.save_state(self.get_state(), self.description)
        return False