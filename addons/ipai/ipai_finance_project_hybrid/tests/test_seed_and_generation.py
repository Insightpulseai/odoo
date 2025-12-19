# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase

class TestFinanceProjectHybrid(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Seed = self.env["ipai.finance.seed.service"]
        self.Project = self.env["project.project"]
        self.Directory = self.env["ipai.finance.directory"]
        self.Template = self.env["ipai.finance.task.template"]
        self.Schedule = self.env["ipai.bir.schedule.line"]

    def test_seed_bundle_loads(self):
        bundle = self.Seed._load_bundle_json()
        self.assertIn("directory", bundle)
        self.assertIn("bir_schedule", bundle)
        self.assertIn("task_templates", bundle)

        # force seed into empty DB (TransactionCase DB is isolated)
        self.Seed.seed_bundle(bundle, strict=True)
        self.assertGreaterEqual(self.Directory.search_count([]), 1)
        self.assertGreaterEqual(self.Template.search_count([]), 1)
        self.assertGreaterEqual(self.Schedule.search_count([]), 1)

    def test_generate_im_projects_and_tasks(self):
        # seed first
        self.Seed.seed_bundle(self.Seed._load_bundle_json(), strict=False)

        root = self.Project.create({"name": "Finance Framework Root"})
        wiz = self.env["ipai.generate.im.projects.wizard"].create({"project_id": root.id})
        action = wiz.action_generate()
        self.assertEqual(action["res_model"], "project.project")

        im_children = self.Project.search([("ipai_root_project_id", "=", root.id), ("ipai_is_im_project", "=", True)])
        self.assertEqual(len(im_children), 2)

        im1 = im_children.filtered(lambda p: p.ipai_im_code == "IM1")
        im2 = im_children.filtered(lambda p: p.ipai_im_code == "IM2")
        self.assertEqual(len(im1), 1)
        self.assertEqual(len(im2), 1)

        # tasks created
        t1 = self.env["project.task"].search_count([("project_id", "=", im1.id)])
        t2 = self.env["project.task"].search_count([("project_id", "=", im2.id)])
        self.assertGreater(t1, 0)
        self.assertGreater(t2, 0)
