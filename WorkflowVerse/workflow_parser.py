"""
Workflow Parser for WorkflowVerse
Parses the WorkflowVerse DSL into workflow definitions.
"""

import re
from typing import Dict, List, Optional, Any
from .workflow_models import WorkflowDefinition, WorkflowStep


class WorkflowParser:
    """Parses WorkflowVerse DSL into workflow definitions"""
    
    def __init__(self):
        self.workflow_definition: Optional[WorkflowDefinition] = None
        self.current_step: Optional[WorkflowStep] = None
        self.on_error_handlers: Dict[str, Dict[str, Any]] = {}
        self.on_success_handlers: Dict[str, Dict[str, Any]] = {}
    
    def parse(self, dsl_content: str) -> WorkflowDefinition:
        """
        Parse WorkflowVerse DSL content into a WorkflowDefinition
        
        Args:
            dsl_content: The DSL content to parse
            
        Returns:
            WorkflowDefinition: Parsed workflow definition
        """
        self.workflow_definition = WorkflowDefinition(name="unnamed_workflow")
        self.on_error_handlers = {}
        self.on_success_handlers = {}
        
        lines = dsl_content.strip().split('\n')
        workflow_name_found = False
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # WORKFLOW declaration
            workflow_match = re.match(r'^WORKFLOW\s+(\w+):', line)
            if workflow_match:
                workflow_name = workflow_match.group(1)
                self.workflow_definition.name = workflow_name
                workflow_name_found = True
                continue
            
            # STEP definition
            step_match = re.match(r'^STEP\s+(\w+):', line)
            if step_match:
                if self.current_step:
                    # If no output was specified, default to step name + ".output"
                    if self.current_step.output is None:
                        self.current_step.output = self.current_step.name + ".output"
                    # Save previous step
                    self.workflow_definition.steps[self.current_step.name] = self.current_step
                
                step_name = step_match.group(1)
                self.current_step = WorkflowStep(
                    name=step_name,
                    verse="",  # Will be filled in next lines
                    action=""  # Will be filled in next lines
                )
                continue
            
            # Step attributes
            if self.current_step:
                verse_match = re.match(r'^VERSE:\s*(.+)', line)
                if verse_match:
                    self.current_step.verse = verse_match.group(1).strip()
                    continue
                
                action_match = re.match(r'^ACTION:\s*(.+)', line)
                if action_match:
                    self.current_step.action = action_match.group(1).strip()
                    continue
                
                params_match = re.match(r'^PARAMS:\s*(.+)', line)
                if params_match:
                    # Simple params parsing - in reality this would be more robust
                    params_str = params_match.group(1).strip()
                    if params_str.startswith('{') and params_str.endswith('}'):
                        # Very basic JSON-like parsing for demo
                        try:
                            # This is simplified - real implementation would use proper JSON parser
                            params_content = params_str[1:-1].strip()
                            if params_content:
                                params = {}
                                # Handle simple key: value pairs
                                for pair in params_content.split(','):
                                    if ':' in pair:
                                        key, value = pair.split(':', 1)
                                        key = key.strip().strip('"\'')
                                        value = value.strip().strip('"\'')
                                        # Try to convert numbers
                                        try:
                                            if '.' in value:
                                                value = float(value)
                                            else:
                                                value = int(value)
                                        except ValueError:
                                            pass  # Keep as string
                                        params[key] = value
                                self.current_step.params = params
                        except Exception:
                            # If parsing fails, keep as empty dict
                            self.current_step.params = {}
                    continue
                
                input_match = re.match(r'^INPUT:\s*(.+)', line)
                if input_match:
                    self.current_step.input = input_match.group(1).strip()
                    continue
                
                depends_match = re.match(r'^DEPENDS:\s*(.+)', line)
                if depends_match:
                    deps_str = depends_match.group(1).strip()
                    if deps_str:
                        self.current_step.depends_on = [dep.strip() for dep in deps_str.split(',')]
                    continue
                
                condition_match = re.match(r'^CONDITION:\s*(.+)', line)
                if condition_match:
                    self.current_step.condition = condition_match.group(1).strip()
                    continue
                
                output_match = re.match(r'^OUTPUT:\s*(.+)', line)
                if output_match:
                    self.current_step.output = output_match.group(1).strip()
                    continue
                
                rollback_match = re.match(r'^ROLLBACK:\s*(.+)', line)
                if rollback_match:
                    self.current_step.rollback = rollback_match.group(1).strip()
                    continue
            
            # ON ERROR handling
            on_error_match = re.match(r'^ON ERROR\s+(\w+):', line)
            if on_error_match:
                step_name = on_error_match.group(1)
                self.on_error_handlers[step_name] = {}
                continue
            
            if self.current_step and line.startswith('COMPENSATE:'):
                compensate_value = line.split(':', 1)[1].strip()
                if self.current_step.name in self.on_error_handlers:
                    self.on_error_handlers[self.current_step.name]['compensate'] = compensate_value
                continue
            
            if self.current_step and line.startswith('ALERT:'):
                alert_value = line.split(':', 1)[1].strip()
                if self.current_step.name in self.on_error_handlers:
                    self.on_error_handlers[self.current_step.name]['alert'] = alert_value
                continue
            
            # ON SUCCESS handling
            on_success_match = re.match(r'^ON SUCCESS\s+(\w+):', line)
            if on_success_match:
                step_name = on_success_match.group(1)
                self.on_success_handlers[step_name] = {}
                continue
            
            if self.current_step and line.startswith('NOTIFY:'):
                notify_value = line.split(':', 1)[1].strip()
                if self.current_step.name in self.on_success_handlers:
                    self.on_success_handlers[self.current_step.name]['notify'] = notify_value
                continue
            
            if self.current_step and line.startswith('LINK:'):
                link_value = line.split(':', 1)[1].strip()
                if self.current_step.name in self.on_success_handlers:
                    self.on_success_handlers[self.current_step.name]['link'] = link_value
                continue
        
        # Don't forget the last step
        if self.current_step:
            # If no output was specified, default to step name + ".output"
            if self.current_step.output is None:
                self.current_step.output = self.current_step.name + ".output"
            self.workflow_definition.steps[self.current_step.name] = self.current_step
        
        # Apply error and success handlers to workflow definition
        self.workflow_definition.on_error = self.on_error_handlers
        self.workflow_definition.on_success = self.on_success_handlers
        
        if not workflow_name_found:
            raise ValueError("No WORKFLOW declaration found in DSL")
        
        return self.workflow_definition