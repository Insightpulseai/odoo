import { describe, it, expect } from "vitest";

describe("operations commands", () => {
  it("loads module without throwing", async () => {
    const mod = await import("./operations");
    expect(mod).toBeTruthy();
    expect(mod.installModulesCommand).toBeDefined();
  });
});
