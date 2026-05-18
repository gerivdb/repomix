"""
Dependency Resolver for WorkflowVerse
Resolves dependencies between workflow steps and determines execution order.
"""

from typing import Dict, List, Set, Tuple, Optional
from .workflow_models import WorkflowDefinition, WorkflowExecutionPlan


class DependencyResolver:
    """Resolves workflow step dependencies and creates execution plans"""
    
    def __init__(self):
        self.workflow_definition: Optional[WorkflowDefinition] = None
    
    def resolve_dependencies(self, workflow: WorkflowDefinition) -> WorkflowExecutionPlan:
        """
        Resolve dependencies and create an execution plan
        
        Args:
            workflow: The workflow definition to resolve
            
        Returns:
            WorkflowExecutionPlan: Execution plan with resolved dependencies
        """
        self.workflow_definition = workflow
        
        # Build adjacency list and in-degree count for topological sort
        adjacency: Dict[str, List[str]] = {}
        in_degree: Dict[str, int] = {}
        
        # Initialize for all steps
        for step_name in workflow.steps:
            adjacency[step_name] = []
            in_degree[step_name] = 0
        
        # Process dependencies
        for step_name, step in workflow.steps.items():
            # Handle depends_on
            for dep in step.depends_on:
                if dep not in adjacency:
                    # Handle case where dependency refers to another step's output
                    adjacency[dep] = []
                    in_degree[dep] = 0
                adjacency[dep].append(step_name)
                in_degree[step_name] = in_degree.get(step_name, 0) + 1
            
            # Handle input dependency (if input references another step's output)
            if step.input:
                # Find which step produces this input
                producer_step = self._find_producer_step(workflow, step.input)
                if producer_step and producer_step != step_name:
                    if producer_step not in adjacency:
                        adjacency[producer_step] = []
                        in_degree[producer_step] = 0
                    adjacency[producer_step].append(step_name)
                    in_degree[step_name] = in_degree.get(step_name, 0) + 1
        
        # Topological sort (Kahn's algorithm)
        queue: List[str] = [step for step in in_degree if in_degree[step] == 0]
        execution_order: List[str] = []
        
        while queue:
            # Process all ready steps (could be parallelized)
            current_level = queue.copy()
            queue.clear()
            
            for step_name in current_level:
                execution_order.append(step_name)
                
                # Decrease in-degree for neighbors
                for neighbor in adjacency[step_name]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(workflow.steps):
            # There's a cycle - find it for better error message
            visited = set()
            rec_stack = set()
            cycle = self._find_cycle(workflow.steps, adjacency)
            raise ValueError(f"Circular dependency detected in workflow: {cycle}")
        
        # Create execution plan
        return WorkflowExecutionPlan(
            workflow=workflow,
            execution_order=execution_order,
            step_dependencies=self._build_step_dependencies(workflow),
            ready_steps=[]  # Will be populated during execution
        )
    
    def _find_producer_step(self, workflow: WorkflowDefinition, input_name: str) -> Optional[str]:
        """Find which step produces a given input/output name"""
        for step_name, step in workflow.steps.items():
            if step.output == input_name:
                return step_name
        return None
    
    def _build_step_dependencies(self, workflow: WorkflowDefinition) -> Dict[str, List[str]]:
        """Build a clear dependency map for each step"""
        dependencies: Dict[str, List[str]] = {}
        
        for step_name, step in workflow.steps.items():
            deps = []
            
            # Add depends_on
            deps.extend(step.depends_on)
            
            # Add input dependency
            if step.input:
                producer = self._find_producer_step(workflow, step.input)
                if producer and producer not in deps:
                    deps.append(producer)
            
            dependencies[step_name] = deps
        
        return dependencies
    
    def _find_cycle(self, steps: Dict[str, any], adjacency: Dict[str, List[str]]) -> List[str]:
        """Find a cycle in the dependency graph for error reporting"""
        visited = set()
        rec_stack = set()
        parent: Dict[str, Optional[str]] = {}
        cycle_start: Optional[str] = None
        
        def dfs(node: str) -> bool:
            nonlocal cycle_start
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    parent[neighbor] = node
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = neighbor
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step in steps:
            if step not in visited:
                parent[step] = None
                if dfs(step):
                    # Reconstruct cycle
                    cycle = [cycle_start]
                    current = parent[cycle_start]
                    while current is not None and current != cycle_start:
                        cycle.append(current)
                        current = parent[current]
                    cycle.append(cycle_start)
                    return list(reversed(cycle))
        
        return ["unknown_cycle"]