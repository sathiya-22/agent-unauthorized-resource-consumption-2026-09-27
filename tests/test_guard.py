import pytest
from agent_resource_guard import ResourceGuard

def test_initial_budget_and_current_budget():
    guard = ResourceGuard(initial_budget=100)
    assert guard.current_budget == 100

def test_negative_initial_budget_raises_error():
    with pytest.raises(ValueError, match="Initial budget cannot be negative."):
        ResourceGuard(initial_budget=-10)

def test_guard_with_default_cost():
    guard = ResourceGuard(initial_budget=5)

    @guard.guard_resource()
    def my_action():
        return "performed"

    assert my_action() == "performed"
    assert guard.current_budget == 4 # Default cost is 1

def test_guard_with_custom_resource_name_and_cost():
    guard = ResourceGuard(initial_budget=10, costs={"expensive_op": 5})

    @guard.guard_resource("expensive_op")
    def expensive_action():
        return "expensive_performed"

    assert expensive_action() == "expensive_performed"
    assert guard.current_budget == 5

def test_guard_blocks_when_budget_insufficient():
    guard = ResourceGuard(initial_budget=4, costs={"expensive_op": 5})

    @guard.guard_resource("expensive_op")
    def expensive_action():
        return "expensive_performed"

    with pytest.raises(RuntimeError, match="Insufficient budget"):
        expensive_action()
    assert guard.current_budget == 4 # Budget should not change if blocked

def test_guard_blocks_after_depletion():
    guard = ResourceGuard(initial_budget=10, costs={"op": 3})

    @guard.guard_resource("op")
    def action():
        return "performed"

    action() # 10 - 3 = 7
    action() # 7 - 3 = 4
    action() # 4 - 3 = 1

    assert guard.current_budget == 1

    with pytest.raises(RuntimeError, match="Insufficient budget"):
        action() # Should be blocked
    assert guard.current_budget == 1 # Budget remains 1

def test_multiple_guarded_functions_with_different_costs():
    guard = ResourceGuard(initial_budget=20, costs={"cheap": 2, "medium": 5, "expensive": 10})

    @guard.guard_resource("cheap")
    def cheap_func(): return "cheap"

    @guard.guard_resource("medium")
    def medium_func(): return "medium"

    @guard.guard_resource("expensive")
    def expensive_func(): return "expensive"

    cheap_func() # 20 - 2 = 18
    medium_func() # 18 - 5 = 13
    expensive_func() # 13 - 10 = 3
    assert guard.current_budget == 3

    with pytest.raises(RuntimeError):
        medium_func() # 3 - 5 = insufficient
    assert guard.current_budget == 3

def test_reset_budget():
    guard = ResourceGuard(initial_budget=10)

    @guard.guard_resource()
    def action(): pass

    action()
    assert guard.current_budget == 9

    guard.reset_budget(50)
    assert guard.current_budget == 50

    with pytest.raises(ValueError, match="New budget cannot be negative."):
        guard.reset_budget(-5)

def test_add_budget():
    guard = ResourceGuard(initial_budget=10)

    @guard.guard_resource()
    def action(): pass

    action()
    assert guard.current_budget == 9

    guard.add_budget(20)
    assert guard.current_budget == 29

    with pytest.raises(ValueError, match="Cannot add a negative amount to the budget."):
        guard.add_budget(-5)

def test_function_qualname_as_resource_name():
    guard = ResourceGuard(initial_budget=10, costs={"test_function_qualname_as_resource_name.<locals>.nested_func": 3})

    @guard.guard_resource() # Will use 'test_function_qualname_as_resource_name.<locals>.nested_func' as resource_name
    def nested_func():
        return "nested"

    nested_func()
    assert guard.current_budget == 7

def test_default_cost_when_not_specified_and_resource_name_not_in_costs():
    guard = ResourceGuard(initial_budget=3, costs={"specific_op": 2}) # No 'default' specified

    @guard.guard_resource("unlisted_op") # Will use default cost of 1.0
    def unlisted_op_func():
        return "unlisted"

    unlisted_op_func()
    assert guard.current_budget == 2

    unlisted_op_func()
    assert guard.current_budget == 1

    with pytest.raises(RuntimeError):
        unlisted_op_func()
    assert guard.current_budget == 1

def test_zero_budget_blocks_any_cost_greater_than_zero():
    guard = ResourceGuard(initial_budget=0, costs={"op": 0.1})

    @guard.guard_resource("op")
    def action(): pass

    with pytest.raises(RuntimeError, match="Insufficient budget"):
        action()
    assert guard.current_budget == 0

def test_zero_cost_operations_never_deplete_budget():
    guard = ResourceGuard(initial_budget=10, costs={"free_op": 0})

    @guard.guard_resource("free_op")
    def free_action(): return "free"

    for _ in range(100):
        free_action()
    assert guard.current_budget == 10
