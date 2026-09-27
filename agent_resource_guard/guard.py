import functools
import threading
from typing import Callable, Dict, Any, Optional

class ResourceGuard:
    """
    A resource guard to prevent agentic AI systems from consuming resources
    beyond a predefined budget.

    This class provides a decorator to wrap functions that consume resources,
    decrementing a budget before allowing execution. If the budget is insufficient,
    the function call is blocked.
    """

    def __init__(self, initial_budget: float, costs: Optional[Dict[str, float]] = None):
        """
        Initializes the ResourceGuard with a total budget and specific costs for operations.

        Args:
            initial_budget: The total resource budget available.
            costs: A dictionary mapping resource names (strings) to their associated cost (float).
                   If a guarded function's name is not found, a 'default' cost is used.
                   If 'default' is not specified, it defaults to 1.0.
        """
        if initial_budget < 0:
            raise ValueError("Initial budget cannot be negative.")
        self._budget = initial_budget
        self._costs = costs if costs is not None else {}
        self._lock = threading.Lock() # Ensure thread-safe budget modifications

    @property
    def current_budget(self) -> float:
        """Returns the current remaining budget."""
        with self._lock:
            return self._budget

    def _get_cost(self, resource_name: str) -> float:
        """Determines the cost for a given resource name."""
        return self._costs.get(resource_name, self._costs.get("default", 1.0))

    def guard_resource(self, resource_name: Optional[str] = None):
        """
        Decorator to guard a function, consuming budget before execution.

        Args:
            resource_name: The name of the resource being consumed. If None,
                           the function's qualified name will be used.
                           This name is used to look up its cost in the `costs` dictionary.
        """
        def decorator(func: Callable) -> Callable:
            actual_resource_name = resource_name if resource_name is not None else func.__qualname__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                cost = self._get_cost(actual_resource_name)

                with self._lock:
                    if self._budget < cost:
                        raise RuntimeError(
                            f"ResourceGuard: Insufficient budget to perform '{actual_resource_name}'. "
                            f"Required: {cost}, Available: {self._budget}"
                        )
                    self._budget -= cost
                    # print(f"[DEBUG] Consumed {cost} for '{actual_resource_name}'. Budget left: {self._budget}") # For debugging

                return func(*args, **kwargs)
            return wrapper
        return decorator

    def reset_budget(self, new_budget: float):
        """Resets the budget to a new value."""
        if new_budget < 0:
            raise ValueError("New budget cannot be negative.")
        with self._lock:
            self._budget = new_budget

    def add_budget(self, amount: float):
        """Adds an amount to the current budget."""
        if amount < 0:
            raise ValueError("Cannot add a negative amount to the budget.")
        with self._lock:
            self._budget += amount
