"""SSOT AI Manifest integrity tests.

Validates cross-references between ssot/ai/*.yaml manifests.
Run with: python -m pytest tests/ssot/test_ai_manifests.py -v
"""

import os
import unittest

import yaml

SSOT_AI_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "ssot", "ai"
)


def _load(filename):
    path = os.path.join(SSOT_AI_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


class TestAIManifestIntegrity(unittest.TestCase):
    """Verify IDs resolve across SSOT AI YAML manifests."""

    @classmethod
    def setUpClass(cls):
        cls.agents_data = _load("agents.yaml")
        cls.models_data = _load("models.yaml")
        cls.topics_data = _load("topics.yaml")
        cls.tools_data = _load("tools.yaml")
        cls.policies_data = _load("policies.yaml")
        cls.sources_data = _load("sources.yaml")
        cls.prompts_data = _load("prompts.yaml")

    def test_all_manifests_exist(self):
        """All 7 SSOT AI manifests must exist."""
        for name, data in [
            ("agents.yaml", self.agents_data),
            ("models.yaml", self.models_data),
            ("topics.yaml", self.topics_data),
            ("tools.yaml", self.tools_data),
            ("policies.yaml", self.policies_data),
            ("sources.yaml", self.sources_data),
            ("prompts.yaml", self.prompts_data),
        ]:
            self.assertIsNotNone(data, f"{name} must exist and be valid YAML")

    def test_physical_agent_has_model_reference(self):
        """Physical agents must reference a valid model_id."""
        model_ids = {m["id"] for m in self.models_data["models"]}
        for agent in self.agents_data["physical_agents"]:
            self.assertIn(
                agent["model_id"],
                model_ids,
                f"Physical agent '{agent['id']}' references unknown model "
                f"'{agent['model_id']}'",
            )

    def test_physical_agent_has_knowledge_source(self):
        """Physical agents with knowledge_source_id must reference valid source."""
        source_ids = {s["id"] for s in self.sources_data["sources"]}
        for agent in self.agents_data["physical_agents"]:
            ks = agent.get("knowledge_source_id")
            if ks:
                self.assertIn(
                    ks,
                    source_ids,
                    f"Physical agent '{agent['id']}' references unknown "
                    f"source '{ks}'",
                )

    def test_logical_agents_map_to_physical(self):
        """Logical agents must reference a valid physical_agent_id."""
        physical_ids = {a["id"] for a in self.agents_data["physical_agents"]}
        for la in self.agents_data["logical_agents"]:
            self.assertIn(
                la["physical_agent_id"],
                physical_ids,
                f"Logical agent '{la['id']}' references unknown physical "
                f"agent '{la['physical_agent_id']}'",
            )

    def test_logical_agents_listed_in_physical(self):
        """Logical agent IDs must appear in their physical agent's list."""
        for pa in self.agents_data["physical_agents"]:
            declared = set(pa.get("logical_agents", []))
            for la in self.agents_data["logical_agents"]:
                if la["physical_agent_id"] == pa["id"]:
                    self.assertIn(
                        la["id"],
                        declared,
                        f"Logical agent '{la['id']}' maps to '{pa['id']}' "
                        f"but is not in its logical_agents list",
                    )

    def test_logical_agent_topic_ids_valid(self):
        """Logical agent topic_ids must reference valid topics."""
        topic_ids = {t["id"] for t in self.topics_data["topics"]}
        for la in self.agents_data["logical_agents"]:
            for tid in la.get("topic_ids", []):
                self.assertIn(
                    tid,
                    topic_ids,
                    f"Logical agent '{la['id']}' references unknown "
                    f"topic '{tid}'",
                )

    def test_logical_agent_policy_ids_valid(self):
        """Logical agent policy_ids must reference valid policies."""
        policy_ids = {p["id"] for p in self.policies_data["policies"]}
        for la in self.agents_data["logical_agents"]:
            for pid in la.get("policy_ids", []):
                self.assertIn(
                    pid,
                    policy_ids,
                    f"Logical agent '{la['id']}' references unknown "
                    f"policy '{pid}'",
                )

    def test_logical_agent_tool_ids_valid(self):
        """Logical agent tool_ids must reference valid tools (if any)."""
        tool_ids = set()
        tools_list = self.tools_data.get("tools") or []
        for t in tools_list:
            tool_ids.add(t["id"])
        for la in self.agents_data["logical_agents"]:
            for tid in la.get("tool_ids", []):
                self.assertIn(
                    tid,
                    tool_ids,
                    f"Logical agent '{la['id']}' references unknown "
                    f"tool '{tid}'",
                )

    def test_foundry_memory_default_false(self):
        """Physical agents must have memory_default: false."""
        for agent in self.agents_data["physical_agents"]:
            self.assertFalse(
                agent.get("memory_default", True),
                f"Physical agent '{agent['id']}' must have "
                f"memory_default: false",
            )

    def test_instructions_artifact_exists(self):
        """Physical agents must reference an existing instructions artifact."""
        for agent in self.agents_data["physical_agents"]:
            artifact = agent.get("instructions_artifact")
            if artifact:
                # Path is relative to repo root
                repo_root = os.path.join(SSOT_AI_DIR, "..", "..")
                full_path = os.path.join(repo_root, artifact)
                self.assertTrue(
                    os.path.exists(full_path),
                    f"Instructions artifact '{artifact}' does not exist",
                )

    def test_prompts_reference_valid_artifact(self):
        """Prompt entries with parent must reference a valid prompt ID."""
        prompt_ids = {p["id"] for p in self.prompts_data["prompts"]}
        for p in self.prompts_data["prompts"]:
            parent = p.get("parent")
            if parent:
                self.assertIn(
                    parent,
                    prompt_ids,
                    f"Prompt '{p['id']}' references unknown parent '{parent}'",
                )

    def test_exactly_one_physical_agent(self):
        """There must be exactly one physical Foundry agent."""
        self.assertEqual(
            len(self.agents_data["physical_agents"]),
            1,
            "Expected exactly one physical Foundry agent",
        )

    def test_no_orphaned_policy_references(self):
        """All policies must be referenced by at least one logical agent."""
        referenced = set()
        for la in self.agents_data["logical_agents"]:
            referenced.update(la.get("policy_ids", []))
        all_policies = {p["id"] for p in self.policies_data["policies"]}
        # memory-off-default is a foundry-level policy, not agent-level
        foundry_level = {"memory-off-default"}
        orphaned = all_policies - referenced - foundry_level
        self.assertEqual(
            orphaned,
            set(),
            f"Orphaned policies not referenced by any agent: {orphaned}",
        )


if __name__ == "__main__":
    unittest.main()
