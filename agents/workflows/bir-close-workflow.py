# agents/workflows/bir-close-workflow.py

from agent_framework.workflows import Workflow, Edge
from agent_framework.registry import SkillRegistry

# Initialize registry and agents
# In a real scenario, these would be loaded from agents/registry/skills-index.json
registry = SkillRegistry("agents/registry/skills-index.json")

# Specialized Agents for the Close Sequence
record_agent = registry.get_agent("bir.record")
reconcile_agent = registry.get_agent("bir.reconcile")
close_agent = registry.get_agent("bir.close")
report_agent = registry.get_agent("bir.report")
bir_tax_agent = registry.get_agent("bir.tax")

# BIR Month-End Close Workflow
# Pattern: Record -> Reconcile -> Close -> (Approval Gate) -> Report -> Tax
close_workflow = Workflow(
    name="BIR Month-End Close",
    description="Guided record-to-report sequence for Philippine BIR compliance.",
)

# Nodes: The Agents
close_workflow.add_node("record", record_agent)
close_workflow.add_node("reconcile", reconcile_agent)
close_workflow.add_node("close", close_agent)
close_workflow.add_node("report", report_agent)
close_workflow.add_node("tax", bir_tax_agent)

# Edges: The Flow Transitions
close_workflow.add_edge(Edge("record", "reconcile"))
close_workflow.add_edge(Edge("reconcile", "close"))

# Mandatory Human-in-the-Loop Approval Gate
# The Finance Head (CKVC) must approve the trial balance and close pack
# before generating the final BIR reports.
close_workflow.add_edge(Edge(
    "close", 
    "report", 
    requires_human_approval=True,
    approval_role="Finance Head",
    approval_instructions="Verify the Trial Balance and Accrual Candidates before generating reports.",
))

close_workflow.add_edge(Edge("report", "tax"))

if __name__ == "__main__":
    print(f"Workflow '{close_workflow.name}' initialized.")
    print(f"Sequential nodes: {list(close_workflow.nodes.keys())}")
    print(f"Human Approval Gate present: {any(e.requires_human_approval for e in close_workflow.edges.values())}")
