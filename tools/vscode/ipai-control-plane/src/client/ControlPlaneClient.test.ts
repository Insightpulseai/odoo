import { describe, it, expect } from "vitest";
import { ControlPlaneClient } from "./ControlPlaneClient";

describe("ControlPlaneClient", () => {
  it("creates client with base URL", () => {
    const client = new ControlPlaneClient("http://localhost:9876");
    expect(client).toBeDefined();
  });

  it("has required methods", () => {
    const client = new ControlPlaneClient("http://localhost:9876");
    expect(client.healthCheck).toBeDefined();
    expect(client.getProjects).toBeDefined();
    expect(client.getEnvironments).toBeDefined();
    expect(client.validateManifest).toBeDefined();
    expect(client.validateXml).toBeDefined();
    expect(client.validateSecurity).toBeDefined();
  });
});
