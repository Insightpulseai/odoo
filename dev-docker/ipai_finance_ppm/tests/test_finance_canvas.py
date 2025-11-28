from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import json


class TestFinanceCanvas(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestFinanceCanvas, cls).setUpClass()
        # Create a test user to own the canvas
        cls.user = cls.env.ref('base.user_admin')

        # Create a sample Canvas
        cls.canvas = cls.env['finance.ppm.canvas'].create({
            'name': 'Test Financial Dashboard',
            'user_id': cls.user.id,
            'layout_columns': '4',
        })

        # Create some dummy tasks for data visualization testing
        cls.Task = cls.env['finance.ppm.task']
        cls.Task.create({'name': 'Task A', 'state': 'draft'})
        cls.Task.create({'name': 'Task B', 'state': 'done'})
        cls.Task.create({'name': 'Task C', 'state': 'done'})

    def test_governance_limits(self):
        """Test that the 10-widget limit is enforced"""
        # Create a fresh canvas for this test
        canvas = self.env['finance.ppm.canvas'].create({
            'name': 'Widget Limit Test Canvas',
            'layout_columns': '4',
        })

        # 1. Create 10 widgets (allowed)
        for i in range(10):
            self.env['finance.ppm.widget'].create({
                'name': f'Widget {i}',
                'canvas_id': canvas.id,
                'widget_type': 'chart',
                'target_object': 'finance.ppm.task'
            })

        # 2. Try to create the 11th widget (should fail)
        with self.assertRaises(ValidationError):
            self.env['finance.ppm.widget'].create({
                'name': 'Widget 11 (Illegal)',
                'canvas_id': canvas.id,
                'widget_type': 'chart',
                'target_object': 'finance.ppm.task'
            })

    def test_table_limit(self):
        """Test that the 7-table limit is enforced"""
        # Create a fresh canvas for this test
        canvas = self.env['finance.ppm.canvas'].create({
            'name': 'Table Limit Test Canvas',
            'layout_columns': '4',
        })

        # 1. Create 7 table widgets
        for i in range(7):
            self.env['finance.ppm.widget'].create({
                'name': f'Table {i}',
                'canvas_id': canvas.id,
                'widget_type': 'table',
                'target_object': 'finance.ppm.task'
            })

        # 2. Try to create the 8th table
        with self.assertRaises(ValidationError):
            self.env['finance.ppm.widget'].create({
                'name': 'Table 8 (Illegal)',
                'canvas_id': canvas.id,
                'widget_type': 'table',
                'target_object': 'finance.ppm.task'
            })

    def test_echarts_json_generation(self):
        """Test that data fetching and JSON generation works for Charts"""
        # 1. Setup a Pie Chart grouping by State
        group_field = self.env['ir.model.fields'].search([
            ('model', '=', 'finance.ppm.task'),
            ('name', '=', 'state')
        ], limit=1)

        if not group_field:
            self.skipTest("State field not found on finance.ppm.task")

        # Create a fresh canvas for this test
        canvas = self.env['finance.ppm.canvas'].create({
            'name': 'ECharts Test Canvas',
            'layout_columns': '4',
        })

        widget = self.env['finance.ppm.widget'].create({
            'name': 'Task Status Pie',
            'canvas_id': canvas.id,
            'widget_type': 'chart',
            'chart_type': 'pie',
            'target_object': 'finance.ppm.task',
            'group_by_field': group_field.id,
            'operation_type': 'count'
        })

        # 2. Trigger computation
        widget._compute_echarts_json()

        # 3. Verify JSON output
        self.assertTrue(widget.echarts_config, "JSON config should not be empty")
        data = json.loads(widget.echarts_config)

        # Check title
        self.assertEqual(data['title']['text'], 'Task Status Pie')

        # Check that series data exists
        self.assertIn('series', data)
        self.assertTrue(len(data['series']) > 0)

    def test_fetch_widget_data_empty(self):
        """Test graceful handling of widgets with no configuration"""
        # Create a fresh canvas for this test
        canvas = self.env['finance.ppm.canvas'].create({
            'name': 'Empty Widget Test Canvas',
            'layout_columns': '4',
        })

        widget = self.env['finance.ppm.widget'].create({
            'name': 'Empty Widget',
            'canvas_id': canvas.id,
            'target_object': 'finance.ppm.task',
            'widget_type': 'chart',
        })

        labels, values = widget._fetch_widget_data()
        self.assertEqual(labels, [], "Labels should be empty when no group_by is set")
        self.assertEqual(values, [], "Values should be empty when no group_by is set")

    def test_widget_counts_computed(self):
        """Test that widget counts are computed correctly."""
        # Create a fresh canvas for this test
        canvas = self.env['finance.ppm.canvas'].create({
            'name': 'Count Test Canvas',
            'layout_columns': '4',
        })

        self.assertEqual(canvas.widget_count, 0)
        self.assertEqual(canvas.table_count, 0)

        self.env['finance.ppm.widget'].create({
            'name': 'Chart 1',
            'canvas_id': canvas.id,
            'target_object': 'finance.ppm.task',
            'widget_type': 'chart',
            'chart_type': 'pie'
        })
        self.env['finance.ppm.widget'].create({
            'name': 'Table 1',
            'canvas_id': canvas.id,
            'target_object': 'finance.ppm.task',
            'widget_type': 'table'
        })

        canvas.invalidate_recordset()
        self.assertEqual(canvas.widget_count, 2)
        self.assertEqual(canvas.table_count, 1)


class TestFinancePPMTask(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestFinancePPMTask, cls).setUpClass()
        # Create a finance team member
        cls.team_member = cls.env['finance.team'].create({
            'code': 'TEST',
            'name': 'Test User',
            'email': 'test@example.com'
        })

    def test_task_creation(self):
        """Test basic task creation"""
        task = self.env['finance.ppm.task'].create({
            'name': 'Test Task',
            'state': 'draft',
            'role_id': self.team_member.id,
        })
        self.assertEqual(task.state, 'draft')
        self.assertEqual(task.complete_name, 'Test Task')

    def test_task_hierarchy(self):
        """Test hierarchical task structure"""
        parent = self.env['finance.ppm.task'].create({
            'name': 'Parent Phase',
            'logframe_level': 'phase',
        })
        child = self.env['finance.ppm.task'].create({
            'name': 'Child Task',
            'parent_id': parent.id,
        })
        self.assertEqual(child.complete_name, 'Parent Phase / Child Task')

    def test_task_workflow(self):
        """Test task state transitions"""
        task = self.env['finance.ppm.task'].create({
            'name': 'Workflow Test Task',
            'state': 'draft',
        })

        # Start task
        task.action_start_task()
        self.assertEqual(task.state, 'in_progress')

        # Submit for review
        task.action_review_task()
        self.assertEqual(task.state, 'review')

        # Submit for approval
        task.action_approve_task()
        self.assertEqual(task.state, 'approval')

        # Complete task
        task.action_complete_task()
        self.assertEqual(task.state, 'done')

    def test_recursion_check(self):
        """Test that recursive task hierarchy is prevented"""
        task = self.env['finance.ppm.task'].create({
            'name': 'Self Reference Test',
        })

        with self.assertRaises(ValidationError):
            task.parent_id = task.id
