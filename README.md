## Agent Resource Guard - Proactive Cost Control for Agentic AI

**The Problem:** Agentic AI systems, especially those deployed in cloud environments, can exhibit "runaway" resource consumption. This often leads to unexpected and significant cloud bills for developers, as agents might continuously retry failed tasks, enter infinite loops, or simply over-provision resources without proper oversight or authorization. This problem affects anyone deploying agents where resource usage directly translates to cost, from individual developers to large organizations.

**Why this project shape/stack was chosen:**
This prototype is a lightweight **Python package** designed as a **decorator-based resource guard**. Python is the dominant language in the agentic AI ecosystem, making a Python package a natural fit for integration. The decorator pattern allows for non-invasive integration into existing agent code, wrapping specific functions (e.g., tool calls, LLM invocations) that are known resource consumers.

The core idea is to introduce a "budget" that an agent's actions consume. When the budget is depleted, subsequent guarded actions are blocked, preventing further unauthorized spending. This is a **pure orchestration/config** solution; it does not involve LLMs directly in its core logic. The "cost" of an action is determined by a simple configuration, not by an LLM's output.

**Setup and Usage (Zero API Keys):**

1.  **Install:**
    ```bash
    pip install .
    ```
    (Or simply copy the files into your project for this prototype.)

2.  **Define your guarded functions and budget:**

    ```python
    # my_agent_app.py
    from agent_resource_guard import ResourceGuard

    # Initialize a guard with a budget of 100 units.
    # Each 'expensive_tool_call' costs 20 units, 'cheap_llm_call' costs 5 units.
    resource_guard = ResourceGuard(initial_budget=100, costs={
        "expensive_tool_call": 20,
        "cheap_llm_call": 5,
        "default": 1 # Default cost for any guarded function not explicitly listed
    })

    @resource_guard.guard_resource("expensive_tool_call")
    def call_external_api(query: str):
        """Simulates an expensive API call."""
        print(f"Calling expensive external API with: {query}")
        # In a real scenario, this would involve network I/O, cloud service calls, etc.
        return f"Result for {query} from expensive API"

    @resource_guard.guard_resource("cheap_llm_call")
    def invoke_llm_for_summary(text: str):
        """Simulates a cheaper LLM invocation."""
        print(f"Invoking LLM for summary of: {text[:20]}...")
        # In a real scenario, this would be an LLM API call
        return f"Summary of {text[:20]}..."

    @resource_guard.guard_resource() # Uses default cost
    def perform_local_computation(data: list):
        """Simulates a local computation with a default cost."""
        print(f"Performing local computation on {len(data)} items.")
        return sum(data)

    def run_agent_workflow():
        print(f"\n--- Starting Agent Workflow (Budget: {resource_guard.current_budget}) ---")
        
        # First call: expensive (cost 20)
        print(call_external_api("fetch user data"))
        print(f"Budget remaining: {resource_guard.current_budget}")

        # Second call: cheap (cost 5)
        print(invoke_llm_for_summary("This is a long document that needs summarization."))
        print(f"Budget remaining: {resource_guard.current_budget}")
        
        # Third call: default (cost 1)
        print(perform_local_computation([1, 2, 3, 4, 5]))
        print(f"Budget remaining: {resource_guard.current_budget}")

        # Multiple expensive calls to deplete budget
        for i in range(5):
            print(f"\nAttempting expensive call {i+1}...")
            try:
                print(call_external_api(f"analyze batch {i+1}"))
            except RuntimeError as e:
                print(f"Guard blocked: {e}")
            print(f"Budget remaining: {resource_guard.current_budget}")
        
        print(f"\n--- Agent Workflow Finished (Final Budget: {resource_guard.current_budget}) ---")

    if __name__ == "__main__":
        run_agent_workflow()
    ```

3.  **Run the example:**
    ```bash
    python my_agent_app.py
    ```

    You will observe the budget decreasing with each guarded call. Once the budget is exhausted, subsequent guarded calls will raise a `RuntimeError`, effectively preventing unauthorized resource consumption.

**Optional Real-LLM Adapter:**
This project specifically does *not* include any LLM API integration. The problem it addresses (unauthorized resource consumption) is a general infrastructure concern, and the "cost" of an operation is an abstract unit defined by the developer, not a direct measure of LLM tokens or API calls. While LLM calls are *examples* of resource-consuming operations, the guard itself is LLM-agnostic. No API keys are needed or supported.
