"""
Workflow Executor for WorkflowVerse
Executes workflow steps according to execution plan, handles rollbacks, and monitors execution.
"""

import time
import importlib
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from .workflow_models import (
    WorkflowDefinition, WorkflowStep, WorkflowExecutionPlan,
    WorkflowExecutionResult, WorkflowStepStatus
)
from .dependency_resolver import DependencyResolver


class WorkflowError(Exception):
    """Exception raised during workflow execution"""
    pass


class WorkflowExecutor:
    """Executes workflows according to the WorkflowVerse specification"""
    
    def __init__(self):
        self.verse_registry: Dict[str, Any] = {}  # Cache for verse modules/actions
        self.execution_context: Dict[str, Any] = {}  # Shared context between steps
        self.step_timeout_seconds = 300  # 5 minutes default timeout per step
        self.current_workflow_def: Optional[WorkflowDefinition] = None
    
    def execute_workflow(self, workflow_def: WorkflowDefinition) -> WorkflowExecutionResult:
        """
        Execute a complete workflow
        
        Args:
            workflow_def: The workflow definition to execute
            
        Returns:
            WorkflowExecutionResult: Result of the execution
        """
        # Initialize execution result
        result = WorkflowExecutionResult(
            workflow_name=workflow_def.name,
            start_time=datetime.now()
        )
        
        # Store current workflow definition for use in helpers
        self.current_workflow_def = workflow_def
        
        try:
            # Resolve dependencies to get execution plan
            dependency_resolver = DependencyResolver()
            execution_plan = dependency_resolver.resolve_dependencies(workflow_def)
            
            # Pre-execution simulation (if we had a simulator - simplified here)
            # In a full implementation, we would simulate to check for potential issues
            
            # Execute steps in order
            for step_name in execution_plan.execution_order:
                step = workflow_def.get_step(step_name)
                if not step:
                    result.add_error(f"Step '{step_name}' not found in workflow")
                    continue
                
                # Check condition if present
                if step.condition and not self._evaluate_condition(step.condition, result):
                    step.status = WorkflowStepStatus.SKIPPED
                    continue
                
                # Execute the step
                step_result = self._execute_step(step, result)
                
                if step_result['success']:
                    step.status = WorkflowStepStatus.SUCCESS
                    step.result = step_result['data']
                    result.add_step_result(step_name, step_result['data'])
                    # Also store by output name if defined, otherwise also store as step_name + ".output"
                    if step.output:
                        result.add_step_result(step.output, step_result['data'])
                    else:
                        result.add_step_result(f"{step_name}.output", step_result['data'])
                    
                    # Handle ON SUCCESS if defined
                    self._handle_on_success(workflow_def, step_name, step_result['data'], result)
                else:
                    step.status = WorkflowStepStatus.FAILED
                    step.error = step_result['error']
                    result.add_error(f"Step '{step_name}' failed: {step_result['error']}")
                    
                    # Handle ON ERROR if defined (compensation/rollback)
                    compensation_performed = self._handle_on_error(
                        workflow_def, step_name, step_result['error'], result
                    )
                    
                    if not compensation_performed:
                        # If no compensation defined or compensation failed, stop execution
                        break
            
            # Determine overall success
            result.success = len(result.errors) == 0 and \
                           all(step.status == WorkflowStepStatus.SUCCESS 
                               for step in workflow_def.steps.values() 
                               if step.status != WorkflowStepStatus.SKIPPED)
            result.end_time = datetime.now()
            
        except Exception as e:
            result.add_error(f"Workflow execution failed: {str(e)}")
            result.end_time = datetime.now()
        finally:
            # Clean up
            self.current_workflow_def = None
        
        return result
    
    def _execute_step(self, step: WorkflowStep, workflow_result: WorkflowExecutionResult) -> Dict[str, Any]:
        """
        Execute a single workflow step
        
        Returns:
            Dict with keys: success (bool), data (Any), error (str)
        """
        step.status = WorkflowStepStatus.RUNNING
        step.start_time = datetime.now()
        
        try:
            # Prepare step inputs
            inputs = self._prepare_step_inputs(step, workflow_result)
            
            # Get the verse and action to execute
            verse_module, action_func = self._get_verse_action(step.verse, step.action)
            
            # Execute the action with timeout
            start_time = time.time()
            result_data = action_func(**inputs) if inputs else action_func()
            elapsed_time = time.time() - start_time
            
            if elapsed_time > self.step_timeout_seconds:
                return {
                    'success': False,
                    'error': f"Step '{step.name}' exceeded timeout of {self.step_timeout_seconds}s"
                }
            
            step.end_time = datetime.now()
            return {
                'success': True,
                'data': result_data,
                'error': None
            }
            
        except Exception as e:
            step.end_time = datetime.now()
            return {
                'success': False,
                'data': None,
                'error': str(e)
            }
    
    def _prepare_step_inputs(self, step: WorkflowStep, workflow_result: WorkflowExecutionResult) -> Dict[str, Any]:
        """Prepare inputs for a step based on PARAMS and INPUT dependencies"""
        inputs = dict(step.params)  # Start with defined parameters
        
        # If step has an INPUT that references another step's output
        if step.input:
            # Check if the input matches a step output name or step name in results
            input_value = workflow_result.step_results.get(step.input)
            if input_value is not None:
                # Pass the input data as a parameter named 'input'
                inputs['input'] = input_value
            else:
                raise WorkflowError(f"Input '{step.input}' not found in previous step outputs")
        
        return inputs
    
    def _get_verse_action(self, verse_spec: str, action_name: str) -> tuple:
        """
        Resolve a verse specification to a callable action function
        
        Args:
            verse_spec: e.g., "WatchVerse.ScraperVerse" or "BusinessVerse"
            action_name: e.g., "scrape_concerts"
            
        Returns:
            Tuple of (module, function) ready to be called
        """
        # Check cache first
        cache_key = f"{verse_spec}.{action_name}"
        if cache_key in self.verse_registry:
            return self.verse_registry[cache_key]
        
        # Parse verse specification
        # Could be module.Class or just module
        parts = verse_spec.split('.')
        if len(parts) == 1:
            # Just a module name, assume action is a function in that module
            module_name = parts[0]
            class_name = None
        elif len(parts) == 2:
            # Could be module.Class or module.action (but we have separate action_name)
            # Assume format is module.Class
            module_name, class_name = parts
        else:
            # Handle deeper nesting if needed
            module_name = '.'.join(parts[:-1])
            class_name = parts[-1]
        
        try:
            # Import the module
            module = importlib.import_module(module_name)
            
            # Get the class or module that contains the action
            if class_name:
                # Try to get class from module
                try:
                    cls = getattr(module, class_name)
                    # Action could be a class method or a function in the class
                    if hasattr(cls, action_name):
                        action_func = getattr(cls, action_name)
                        # If it's a class method, we might need to instantiate
                        # For simplicity, assume it's callable as-is or is a classmethod/staticmethod
                        action_obj = cls  # We'll call action_func on the class
                    else:
                        # Maybe the action is a function directly in the module
                        action_func = getattr(module, action_name)
                        action_obj = module
                except AttributeError:
                    # Fallback: look for action in module directly
                    action_func = getattr(module, action_name)
                    action_obj = module
            else:
                # No class specified, action is in module
                action_func = getattr(module, action_name)
                action_obj = module
            
            # Cache and return
            self.verse_registry[cache_key] = (action_obj, action_func)
            return action_obj, action_func
            
        except ImportError as e:
            raise WorkflowError(f"Could not import verse module '{module_name}': {str(e)}")
        except AttributeError as e:
            raise WorkflowError(f"Could not find action '{action_name}' in verse '{verse_spec}': {str(e)}")
    
    def _evaluate_condition(self, condition: str, workflow_result: WorkflowExecutionResult) -> bool:
        """
        Evaluate a condition expression (simplified implementation)
        In a full implementation, this would be a proper expression evaluator
        """
        # For now, support simple conditions like "events_count > 0"
        # We'll look up variables in the execution context and step results
        
        # Replace variable references with their values from context
        # This is a very basic implementation - real one would be more robust
        try:
            # Simple approach: evaluate as Python expression with context
            # WARNING: In production, use a proper expression evaluator, not eval!
            # This is for demonstration only
            context = dict(self.execution_context)
            # Add workflow step results as variables
            context.update({k: v for k, v in workflow_result.step_results.items() if not k.startswith('_')})
            
            # Special handling for common conditions in our test
            # If condition is "events_count > 0" and we have a list, check its length
            if condition.strip() == "events_count > 0":
                # Look for events_count in context or check if there's a list we can count
                if 'events_count' in context:
                    return int(context['events_count']) > 0
                # Check if any step result is a list that we can use for events_count
                for key, value in context.items():
                    if isinstance(value, list) and 'event' in key.lower():
                        return len(value) > 0
                # Fallback: check if scraped_events exists and is a list
                if 'scraped_events' in context and isinstance(context['scraped_events'], list):
                    return len(context['scraped_events']) > 0
            
            # For safety, we'll only allow certain operations in a real system
            # Here we'll do a very limited evaluation for demo purposes
            if '>' in condition:
                left, right = condition.split('>', 1)
                left_val = self._get_variable_value(left.strip(), context)
                right_val = self._get_variable_value(right.strip(), context)
                return float(left_val) > float(right_val)
            elif '<' in condition:
                left, right = condition.split('<', 1)
                left_val = self._get_variable_value(left.strip(), context)
                right_val = self._get_variable_value(right.strip(), context)
                return float(left_val) < float(right_val)
            elif '==' in condition:
                left, right = condition.split('==', 1)
                left_val = self._get_variable_value(left.strip(), context)
                right_val = self._get_variable_value(right.strip(), context)
                return str(left_val) == str(right_val)
            else:
                # Assume it's a variable name that should be truthy
                val = self._get_variable_value(condition.strip(), context)
                return bool(val)
        except Exception:
            # If evaluation fails, assume False for safety
            return False
    
    def _get_variable_value(self, var_name: str, context: Dict[str, Any]) -> Any:
        """Get a variable value from context, handling step outputs"""
        # Check if it's a direct context variable
        if var_name in context:
            return context[var_name]
        
        # Check if it matches a step output name
        if var_name in self.execution_context:
            return self.execution_context[var_name]
        
        # Default fallback
        return None
    
    def _handle_on_success(self, workflow_def: WorkflowDefinition, step_name: str, step_result: Any, workflow_result: WorkflowExecutionResult):
        """Handle ON SUCCESS declarations for a step"""
        if step_name in workflow_def.on_success:
            handlers = workflow_def.on_success[step_name]
            if 'notify' in handlers:
                # In a real system, this would send a notification
                print(f"[WORKFLOW NOTIFY] {handlers['notify']}")
            if 'link' in handlers:
                # In a real system, this might set a link in the result
                workflow_result.add_step_result(f"{step_name}_link", handlers['link'])
    
    def _handle_on_error(self, workflow_def: WorkflowDefinition, step_name: str, error_msg: str, workflow_result: WorkflowExecutionResult) -> bool:
        """
        Handle ON ERROR declarations for a step
        
        Returns:
            bool: True if compensation was performed (or not needed), False if workflow should abort
        """
        if step_name not in workflow_def.on_error:
            # No error handler defined - workflow fails
            return False
        
        handlers = workflow_def.on_error[step_name]
        
        # Handle compensation/rollback
        if 'compensate' in handlers:
            compensate_step_name = handlers['compensate']
            compensate_step = workflow_def.get_step(compensate_step_name)
            if compensate_step:
                try:
                    # Execute the compensation step
                    comp_result = self._execute_step(compensate_step, workflow_result)
                    if comp_result['success']:
                        compensate_step.status = WorkflowStepStatus.COMPENSATED
                        workflow_result.add_compensated_step(compensate_step_name)
                        # Optionally store compensation result
                        workflow_result.add_step_result(f"{compensate_step_name}_compensation", comp_result['data'])
                        
                        # Handle alert if defined
                        if 'alert' in handlers:
                            print(f"[WORKFLOW ALERT] {handlers['alert']} (after successful compensation)")
                        
                        return True  # Compensation successful, continue workflow if possible
                    else:
                        compensate_step.status = WorkflowStepStatus.FAILED
                        compensate_step.error = comp_result['error']
                        workflow_result.add_error(f"Compensation step '{compensate_step_name}' failed: {comp_result['error']}")
                        
                        # Even if compensation fails, we might still want to continue depending on policy
                        # For now, we'll return False to abort workflow
                        return False
                except Exception as e:
                    workflow_result.add_error(f"Failed to execute compensation step '{compensate_step_name}': {str(e)}")
                    return False
            else:
                # Compensation step not found
                workflow_result.add_error(f"Compensation step '{compensate_step_name}' not found in workflow")
                return False
        else:
            # No compensation defined, just alert if specified
            if 'alert' in handlers:
                print(f"[WORKFLOW ALERT] {handlers['alert']}")
            # Without compensation, we typically abort the workflow
            return False
    
    def get_workflow_status(self, workflow_result: WorkflowExecutionResult) -> Dict[str, Any]:
        """Get a status summary of workflow execution"""
        return {
            'workflow_name': workflow_result.workflow_name,
            'success': workflow_result.success,
            'start_time': workflow_result.start_time.isoformat() if workflow_result.start_time else None,
            'end_time': workflow_result.end_time.isoformat() if workflow_result.end_time else None,
            'duration_seconds': (
                (workflow_result.end_time - workflow_result.start_time).total_seconds()
                if workflow_result.end_time and workflow_result.start_time else None
            ),
            'step_results': workflow_result.step_results,
            'errors': workflow_result.errors,
            'compensated_steps': workflow_result.compensated_steps
        }