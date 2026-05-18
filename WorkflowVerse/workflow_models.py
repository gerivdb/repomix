"""
Workflow Models for WorkflowVerse
Defines data structures for workflow definitions, steps, execution plans, and results.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime


class WorkflowStepStatus(Enum):
    """Status of a workflow step execution"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    COMPENSATED = "compensated"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Definition of a workflow step"""
    name: str
    verse: str  # e.g., "WatchVerse.ScraperVerse"
    action: str  # e.g., "scrape_concerts"
    params: Dict[str, Any] = field(default_factory=dict)
    input: Optional[str] = None  # Name of output from previous step
    depends_on: List[str] = field(default_factory=list)  # Step names this step depends on
    condition: Optional[str] = None  # Condition expression (simplified)
    output: Optional[str] = None  # Name of this step's output
    rollback: Optional[str] = None  # Step name to call for rollback (compensation)
    
    # Runtime fields
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None


@dataclass
class WorkflowDefinition:
    """Complete workflow definition"""
    name: str
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    on_error: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # step_name -> {compensate, alert}
    on_success: Dict[str, Dict[str, Any]] = field(default_factory=dict)  # step_name -> {notify, link}
    
    def get_step(self, step_name: str) -> Optional[WorkflowStep]:
        return self.steps.get(step_name)


@dataclass
class WorkflowExecutionPlan:
    """Execution plan with resolved dependencies and execution order"""
    workflow: WorkflowDefinition
    execution_order: List[str]  # Step names in order to execute
    step_dependencies: Dict[str, List[str]]  # step -> list of dependencies
    ready_steps: List[str]  # Steps ready to execute (dependencies met)


@dataclass
class WorkflowExecutionResult:
    """Result of workflow execution"""
    workflow_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    success: bool = False
    step_results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    compensated_steps: List[str] = field(default_factory=list)
    
    def add_step_result(self, step_name: str, result: Any):
        self.step_results[step_name] = result
    
    def add_error(self, error: str):
        self.errors.append(error)
    
    def add_compensated_step(self, step_name: str):
        self.compensated_steps.append(step_name)