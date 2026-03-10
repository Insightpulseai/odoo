import { describe, it, expect } from "vitest";
import { route, listCapabilities } from "../src/router.js";

describe("agent-router", () => {
  it("lists capabilities (taxonomy must exist)", async () => {
    const caps = await listCapabilities();
    expect(Array.isArray(caps)).toBe(true);
  });

  it("routes deterministically for a given capability", async () => {
    const res1 = await route({
      capability: "odoo_implementation",
      goal: "Implement modules",
    });
    const res2 = await route({
      capability: "odoo_implementation",
      goal: "Implement modules",
    });
    expect(res1.primary_agent).toBe(res2.primary_agent);
    expect(res1.capability).toBe("odoo_implementation");
  });
});
