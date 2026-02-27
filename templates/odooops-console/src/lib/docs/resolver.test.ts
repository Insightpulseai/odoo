import fs from "fs";
import path from "path";
import { getDocPage } from "./loader";

// Mocks
jest.mock("fs");
jest.mock("path", () => {
  const actual = jest.requireActual("path");
  return {
    ...actual,
    resolve: jest.fn((...args) => actual.join(...args)), // Simplified resolve for testing
  };
});

describe("Docs Resolver Precedence", () => {
  const MOCK_CWD = "/mock/app";
  const MOCK_REPO_ROOT = "/mock";

  beforeAll(() => {
    jest.spyOn(process, "cwd").mockReturnValue(MOCK_CWD);
    // Mock paths in loader.ts will derive from this CWD
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it("should prefer OVERRIDE over deployed and upstream", async () => {
    // Setup: File exists in all 3 layers
    (fs.existsSync as jest.Mock).mockImplementation((p) => {
      if (p.includes("upstream_overrides/foo.md")) return true;
      if (p.includes("stack/foo.md")) return true;
      if (p.includes("upstream/foo.md")) return true;
      return false;
    });
    (fs.readFileSync as jest.Mock).mockReturnValue(
      "---\ntitle: Override\n---\nContent",
    );

    const result = await getDocPage(["foo"]);

    expect(result).not.toBeNull();
    expect(result?.meta.layer).toBe("override");
    expect(result?.title).toBe("Override");
  });

  it("should prefer DEPLOYED over upstream if override is missing", async () => {
    // Setup: File exists in deployed and upstream, not override
    (fs.existsSync as jest.Mock).mockImplementation((p) => {
      if (p.includes("upstream_overrides/foo.md")) return false;
      if (p.includes("stack/foo.md")) return true;
      if (p.includes("upstream/foo.md")) return true;
      return false;
    });
    (fs.readFileSync as jest.Mock).mockReturnValue(
      "---\ntitle: Deployed\n---\nContent",
    );

    const result = await getDocPage(["foo"]);

    expect(result).not.toBeNull();
    expect(result?.meta.layer).toBe("deployed");
    expect(result?.title).toBe("Deployed");
  });

  it("should fallback to UPSTREAM (RST) if others are missing", async () => {
    // Setup: File exists only in upstream as RST
    (fs.existsSync as jest.Mock).mockImplementation((p) => {
      // Create a simplified check that matches the loader logic
      if (p.includes("upstream_overrides")) return false;
      if (p.includes("stack")) return false;
      // Loader checks: MD -> RST -> Index MD -> Index RST
      if (p.endsWith("content/foo.md")) return false;
      if (p.endsWith("content/foo.rst")) return true;
      return false;
    });

    (fs.readFileSync as jest.Mock).mockImplementation(
      () => "RST Title\n=========\nContent",
    );

    const result = await getDocPage(["foo"]);

    expect(result).not.toBeNull();
    expect(result?.meta.layer).toBe("upstream");
  });

  it("should return null if not found anywhere", async () => {
    (fs.existsSync as jest.Mock).mockReturnValue(false);

    const result = await getDocPage(["missing"]);

    expect(result).toBeNull();
  });
});
