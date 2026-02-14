import { describe, it, expect, vi } from "vitest";
import { ProjectTreeProvider } from "./ProjectTreeProvider";

describe("ProjectTreeProvider", () => {
  it("creates provider with client", () => {
    const mockClient: any = {
      getProjects: vi.fn().mockResolvedValue([])
    };

    const provider = new ProjectTreeProvider(mockClient);
    expect(provider).toBeDefined();
  });

  it("has required tree provider methods", () => {
    const mockClient: any = {};
    const provider = new ProjectTreeProvider(mockClient);

    expect(provider.getChildren).toBeDefined();
    expect(provider.getTreeItem).toBeDefined();
    expect(provider.refresh).toBeDefined();
  });
});
