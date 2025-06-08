from smartflow.action_registry import register_action
from smartflow.action_handler import ActionHandler
from typing import Dict

@register_action("hello_world")
class HelloWorldAction(ActionHandler):
    """A simple action that says hello to a specified name."""
    
    required_fields = ["user_name"]
    
    def execute(self, context: Dict[str, str] = None) -> Dict[str, str]:
        """Execute the hello world action."""
        
        action_context = {}
        
        user_name = context["user_name"]
        
        # do some work here
        greeting = f"Hello, {user_name}!"
        print(greeting)

        # add to the context
        action_context["greeting"] = greeting

        # add success indicator to the context
        action_context["result"] = "success"
        
        return action_context
