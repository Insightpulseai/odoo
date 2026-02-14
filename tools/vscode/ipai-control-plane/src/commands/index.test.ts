import { describe, it, expect } from "vitest";

describe("command wiring", () => {
  it("loads module without throwing", async () => {
    const mod = await import("./index");
    expect(mod).toBeTruthy();
    expect(mod.registerCommands).toBeDefined();
  });
});
