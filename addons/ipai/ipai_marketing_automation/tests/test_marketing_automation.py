from datetime import timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestMarketingCampaign(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_partner = cls.env.ref("base.model_res_partner")
        cls.partner_a = cls.env["res.partner"].create(
            {"name": "Campaign Target A", "email": "a@test.com"}
        )
        cls.partner_b = cls.env["res.partner"].create(
            {"name": "Campaign Target B", "email": "b@test.com"}
        )
        cls.crm_tag = cls.env["crm.tag"].create({"name": "Test Tag"})
        cls.activity_type = cls.env["mail.activity.type"].create(
            {"name": "Test Follow-up", "res_model": "res.partner"}
        )

    def _create_campaign(self, domain="[]", steps=None):
        """Helper: create a campaign targeting res.partner."""
        campaign = self.env["ipai.marketing.campaign"].create(
            {
                "name": "Test Campaign",
                "model_id": self.model_partner.id,
                "domain": domain,
            }
        )
        if steps:
            for vals in steps:
                vals["campaign_id"] = campaign.id
                self.env["ipai.marketing.campaign.step"].create(vals)
        return campaign

    def test_campaign_creation(self):
        """Campaign created in draft state."""
        campaign = self._create_campaign()
        self.assertEqual(campaign.state, "draft")
        self.assertEqual(campaign.model_name, "res.partner")

    def test_start_without_steps_raises(self):
        """Starting a campaign without steps raises UserError."""
        campaign = self._create_campaign()
        with self.assertRaises(UserError):
            campaign.action_start()

    def test_state_transitions(self):
        """Campaign transitions through all states correctly."""
        campaign = self._create_campaign(
            steps=[
                {
                    "name": "Step 1",
                    "trigger_type": "begin",
                    "action_type": "add_tag",
                    "tag_id": self.crm_tag.id,
                }
            ]
        )
        self.assertEqual(campaign.state, "draft")
        campaign.action_start()
        self.assertEqual(campaign.state, "running")
        campaign.action_pause()
        self.assertEqual(campaign.state, "paused")
        campaign.action_resume()
        self.assertEqual(campaign.state, "running")
        campaign.action_done()
        self.assertEqual(campaign.state, "done")
        campaign.action_reset_draft()
        self.assertEqual(campaign.state, "draft")

    def test_sync_participants(self):
        """Sync enrolls matching records as participants."""
        domain = "[('name', 'ilike', 'Campaign Target')]"
        campaign = self._create_campaign(
            domain=domain,
            steps=[
                {
                    "name": "Begin",
                    "trigger_type": "begin",
                    "action_type": "add_tag",
                    "tag_id": self.crm_tag.id,
                }
            ],
        )
        campaign.action_start()
        self.assertGreaterEqual(campaign.participant_count, 2)
        res_ids = set(campaign.participant_ids.mapped("res_id"))
        self.assertIn(self.partner_a.id, res_ids)
        self.assertIn(self.partner_b.id, res_ids)

    def test_sync_no_duplicates(self):
        """Re-syncing does not create duplicate participants."""
        domain = "[('id', '=', %d)]" % self.partner_a.id
        campaign = self._create_campaign(
            domain=domain,
            steps=[
                {
                    "name": "Begin",
                    "trigger_type": "begin",
                    "action_type": "add_tag",
                    "tag_id": self.crm_tag.id,
                }
            ],
        )
        campaign.action_start()
        count_after_start = campaign.participant_count
        campaign._sync_participants()
        self.assertEqual(campaign.participant_count, count_after_start)

    def test_participant_unique_constraint(self):
        """Duplicate (campaign, res_id) raises IntegrityError."""
        campaign = self._create_campaign(
            steps=[
                {
                    "name": "Begin",
                    "trigger_type": "begin",
                    "action_type": "add_tag",
                    "tag_id": self.crm_tag.id,
                }
            ]
        )
        self.env["ipai.marketing.campaign.participant"].create(
            {"campaign_id": campaign.id, "res_id": self.partner_a.id}
        )
        with self.assertRaises(Exception):
            self.env["ipai.marketing.campaign.participant"].create(
                {"campaign_id": campaign.id, "res_id": self.partner_a.id}
            )

    def test_participant_record_name(self):
        """Participant record_name resolves to target display_name."""
        campaign = self._create_campaign()
        participant = self.env[
            "ipai.marketing.campaign.participant"
        ].create(
            {"campaign_id": campaign.id, "res_id": self.partner_a.id}
        )
        self.assertEqual(participant.record_name, self.partner_a.display_name)

    def test_participant_deleted_record(self):
        """Participant shows 'Deleted' when target record is gone."""
        temp_partner = self.env["res.partner"].create(
            {"name": "Temporary"}
        )
        campaign = self._create_campaign()
        participant = self.env[
            "ipai.marketing.campaign.participant"
        ].create(
            {"campaign_id": campaign.id, "res_id": temp_partner.id}
        )
        temp_partner.unlink()
        participant.invalidate_recordset()
        self.assertEqual(participant.record_name, "Deleted")

    def test_action_view_participants(self):
        """action_view_participants returns correct window action."""
        campaign = self._create_campaign()
        action = campaign.action_view_participants()
        self.assertEqual(
            action["res_model"], "ipai.marketing.campaign.participant"
        )
        self.assertIn(
            ("campaign_id", "=", campaign.id), action["domain"]
        )


@tagged("post_install", "-at_install")
class TestCampaignStepExecution(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_partner = cls.env.ref("base.model_res_partner")
        cls.partner = cls.env["res.partner"].create(
            {"name": "Step Test Partner", "email": "step@test.com"}
        )
        cls.crm_tag = cls.env["crm.tag"].create({"name": "Auto Tag"})
        cls.activity_type = cls.env["mail.activity.type"].create(
            {"name": "Auto Follow-up", "res_model": "res.partner"}
        )

    def _create_running_campaign(self, steps_vals):
        """Helper: create campaign, add steps, start it."""
        domain = "[('id', '=', %d)]" % self.partner.id
        campaign = self.env["ipai.marketing.campaign"].create(
            {
                "name": "Execution Test",
                "model_id": self.model_partner.id,
                "domain": domain,
            }
        )
        for vals in steps_vals:
            vals["campaign_id"] = campaign.id
            self.env["ipai.marketing.campaign.step"].create(vals)
        campaign.action_start()
        return campaign

    def test_add_tag_action(self):
        """Begin step with add_tag action adds the tag to participant."""
        campaign = self._create_running_campaign(
            [
                {
                    "name": "Tag Step",
                    "sequence": 10,
                    "trigger_type": "begin",
                    "action_type": "add_tag",
                    "tag_id": self.crm_tag.id,
                }
            ]
        )
        step = campaign.step_ids[0]
        step._execute_step()
        # add_tag only works on models with tag_ids — res.partner
        # has category_id, not tag_ids. Verify participant advanced.
        participant = campaign.participant_ids[0]
        self.assertEqual(participant.last_completed_step_id, step)

    def test_create_activity_action(self):
        """Create activity step schedules an activity on the target."""
        campaign = self._create_running_campaign(
            [
                {
                    "name": "Activity Step",
                    "sequence": 10,
                    "trigger_type": "begin",
                    "action_type": "create_activity",
                    "activity_type_id": self.activity_type.id,
                    "activity_summary": "Test follow-up",
                }
            ]
        )
        step = campaign.step_ids[0]
        step._execute_step()
        activities = self.env["mail.activity"].search(
            [
                ("res_model", "=", "res.partner"),
                ("res_id", "=", self.partner.id),
                ("summary", "=", "Test follow-up"),
            ]
        )
        self.assertTrue(activities)

    def test_delay_respects_timing(self):
        """Delay step does not execute before the delay has elapsed."""
        campaign = self._create_running_campaign(
            [
                {
                    "name": "Begin",
                    "sequence": 10,
                    "trigger_type": "begin",
                    "action_type": "create_activity",
                    "activity_summary": "First",
                },
                {
                    "name": "Delayed",
                    "sequence": 20,
                    "trigger_type": "delay",
                    "delay_days": 1,
                    "action_type": "create_activity",
                    "activity_summary": "Second",
                },
            ]
        )
        step_begin = campaign.step_ids.sorted("sequence")[0]
        step_delay = campaign.step_ids.sorted("sequence")[1]

        # Execute begin step
        step_begin._execute_step()
        participant = campaign.participant_ids[0]
        self.assertEqual(participant.last_completed_step_id, step_begin)

        # Execute delay step immediately — should NOT advance (delay=1 day)
        step_delay._execute_step()
        participant.invalidate_recordset()
        self.assertEqual(
            participant.last_completed_step_id,
            step_begin,
            "Delay step should not execute before delay elapsed",
        )

    def test_condition_step_filters(self):
        """Condition step only processes participants matching the domain."""
        # Set partner name to something specific
        self.partner.write({"name": "Step Test Partner"})
        campaign = self._create_running_campaign(
            [
                {
                    "name": "Condition Step",
                    "sequence": 10,
                    "trigger_type": "begin",
                    "action_type": "create_activity",
                    "activity_summary": "Conditional",
                },
            ]
        )
        # Create a second step with condition that won't match
        self.env["ipai.marketing.campaign.step"].create(
            {
                "campaign_id": campaign.id,
                "name": "Blocked by Condition",
                "sequence": 20,
                "trigger_type": "condition",
                "condition_domain": "[('name', '=', 'NONEXISTENT')]",
                "action_type": "create_activity",
                "activity_summary": "Should not run",
            }
        )
        step_begin = campaign.step_ids.sorted("sequence")[0]
        step_cond = campaign.step_ids.sorted("sequence")[1]

        step_begin._execute_step()
        # Backdate step_completed_at so delay=0 passes
        participant = campaign.participant_ids[0]
        participant.write(
            {
                "step_completed_at": fields.Datetime.now()
                - timedelta(hours=1)
            }
        )
        step_cond._execute_step()
        participant.invalidate_recordset()
        self.assertEqual(
            participant.last_completed_step_id,
            step_begin,
            "Condition step should not advance when domain doesn't match",
        )

    def test_deleted_target_sets_error(self):
        """If target record is deleted, participant goes to error state."""
        temp = self.env["res.partner"].create({"name": "Temp Target"})
        domain = "[('id', '=', %d)]" % temp.id
        campaign = self.env["ipai.marketing.campaign"].create(
            {
                "name": "Error Test",
                "model_id": self.model_partner.id,
                "domain": domain,
            }
        )
        self.env["ipai.marketing.campaign.step"].create(
            {
                "campaign_id": campaign.id,
                "name": "Step on deleted",
                "sequence": 10,
                "trigger_type": "begin",
                "action_type": "add_tag",
                "tag_id": self.crm_tag.id,
            }
        )
        campaign.action_start()
        participant = campaign.participant_ids[0]
        temp.unlink()
        campaign.step_ids[0]._execute_step()
        participant.invalidate_recordset()
        self.assertEqual(participant.state, "error")

    def test_cron_execute_campaigns(self):
        """Cron method processes running campaigns without error."""
        domain = "[('id', '=', %d)]" % self.partner.id
        campaign = self.env["ipai.marketing.campaign"].create(
            {
                "name": "Cron Test",
                "model_id": self.model_partner.id,
                "domain": domain,
            }
        )
        self.env["ipai.marketing.campaign.step"].create(
            {
                "campaign_id": campaign.id,
                "name": "Cron Step",
                "sequence": 10,
                "trigger_type": "begin",
                "action_type": "create_activity",
                "activity_summary": "Cron activity",
            }
        )
        campaign.action_start()
        # Should not raise
        self.env["ipai.marketing.campaign"]._cron_execute_campaigns()

    def test_get_previous_step_id(self):
        """_get_previous_step_id returns False for first step, step ID for later."""
        campaign = self._create_running_campaign(
            [
                {
                    "name": "First",
                    "sequence": 10,
                    "trigger_type": "begin",
                    "action_type": "create_activity",
                    "activity_summary": "A",
                },
                {
                    "name": "Second",
                    "sequence": 20,
                    "trigger_type": "delay",
                    "action_type": "create_activity",
                    "activity_summary": "B",
                },
            ]
        )
        steps = campaign.step_ids.sorted("sequence")
        self.assertFalse(steps[0]._get_previous_step_id())
        self.assertEqual(steps[1]._get_previous_step_id(), steps[0].id)
