import unittest
from smartflow.utils.utilities import Utilities

class TestConditionEvaluation(unittest.TestCase):
    def setUp(self):
        self.context = {
            'workflow.status': 'active',
            'workflow.count': '5',
            'workflow.name': 'TestWorkflow',
            'My_Action.result': 'success',
            'workflow.empty': None
        }

    def test_basic_comparisons(self):
        # Test equality
        self.assertTrue(Utilities.evaluate_condition("workflow.status == 'active'", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.status == 'inactive'", self.context))
        
        # Test inequality
        self.assertTrue(Utilities.evaluate_condition("workflow.status != 'inactive'", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.status != 'active'", self.context))

    def test_numeric_comparisons(self):
        # Test greater than
        self.assertTrue(Utilities.evaluate_condition("workflow.count > 3", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.count > 7", self.context))
        
        # Test less than
        self.assertTrue(Utilities.evaluate_condition("workflow.count < 10", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.count < 3", self.context))

    def test_none_checks(self):
        # Test is None
        self.assertTrue(Utilities.evaluate_condition("workflow.empty is None", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.status is None", self.context))
        
        # Test is not None
        self.assertTrue(Utilities.evaluate_condition("workflow.status is not None", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.empty is not None", self.context))

    def test_case_insensitivity(self):
        # Test case insensitive string comparison
        self.assertTrue(Utilities.evaluate_condition("workflow.status == 'ACTIVE'", self.context))
        self.assertTrue(Utilities.evaluate_condition("workflow.name == 'testworkflow'", self.context))
        
        # Test case insensitive key matching
        self.assertTrue(Utilities.evaluate_condition("WORKFLOW.STATUS == 'active'", self.context))
        self.assertTrue(Utilities.evaluate_condition("Workflow.Status == 'active'", self.context))
        self.assertTrue(Utilities.evaluate_condition("my_action.result == 'success'", self.context))
        self.assertTrue(Utilities.evaluate_condition("My_Action.Result == 'success'", self.context))

    def test_and_conditions(self):
        # Test multiple conditions with AND
        self.assertTrue(Utilities.evaluate_condition(
            "workflow.status == 'active' and workflow.count > 3", 
            self.context
        ))
        self.assertFalse(Utilities.evaluate_condition(
            "workflow.status == 'active' and workflow.count > 7", 
            self.context
        ))
        # Test three conditions with AND
        self.assertTrue(Utilities.evaluate_condition(
            "workflow.status == 'active' and workflow.count > 3 and My_Action.result == 'success'", 
            self.context
        ))

    def test_or_conditions(self):
        # Test multiple conditions with OR
        self.assertTrue(Utilities.evaluate_condition(
            "workflow.status == 'inactive' or workflow.count > 3", 
            self.context
        ))
        self.assertTrue(Utilities.evaluate_condition(
            "workflow.status == 'active' or workflow.count > 7", 
            self.context
        ))
        self.assertFalse(Utilities.evaluate_condition(
            "workflow.status == 'inactive' or workflow.count > 7", 
            self.context
        ))
        # Test three conditions with OR
        self.assertTrue(Utilities.evaluate_condition(
            "workflow.status == 'inactive' or workflow.count > 3 or My_Action.result == 'failed'", 
            self.context
        ))

    def test_missing_context_values(self):
        # Test conditions with missing context values
        self.assertFalse(Utilities.evaluate_condition("workflow.missing == 'value'", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.missing is not None", self.context))
        self.assertTrue(Utilities.evaluate_condition("workflow.missing is None", self.context))

    def test_invalid_inputs(self):
        # Test None condition
        self.assertTrue(Utilities.evaluate_condition(None, self.context))
        
        # Test empty condition
        self.assertTrue(Utilities.evaluate_condition("", self.context))
        
        # Test malformed conditions
        self.assertFalse(Utilities.evaluate_condition("workflow.status ==", self.context))  # Missing right side
        self.assertFalse(Utilities.evaluate_condition("== 'active'", self.context))  # Missing left side
        self.assertFalse(Utilities.evaluate_condition("workflow.status", self.context))  # No operator
        self.assertFalse(Utilities.evaluate_condition("workflow.status ===", self.context))  # Invalid operator
        self.assertFalse(Utilities.evaluate_condition("workflow.status == 'active' and", self.context))  # Incomplete AND
        self.assertFalse(Utilities.evaluate_condition("workflow.status == 'active' or", self.context))  # Incomplete OR
        
        # Test invalid operators
        self.assertFalse(Utilities.evaluate_condition("workflow.status === 'active'", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.status => 'active'", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.status =< 'active'", self.context))
        
        # Test invalid None checks
        self.assertFalse(Utilities.evaluate_condition("workflow.status is", self.context))
        self.assertFalse(Utilities.evaluate_condition("workflow.status is not", self.context))
        
        # Test invalid string quotes
        self.assertFalse(Utilities.evaluate_condition("workflow.status == active", self.context))  # Missing quotes
        self.assertFalse(Utilities.evaluate_condition("workflow.status == 'active", self.context))  # Unclosed quote
        self.assertFalse(Utilities.evaluate_condition("workflow.status == active'", self.context))  # Unopened quote

if __name__ == '__main__':
    unittest.main()
