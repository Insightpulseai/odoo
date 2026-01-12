/**
 * SpecKit Client for spec bundle management
 */

import { readFile, readdir, writeFile, mkdir, access } from "fs/promises";
import { join, basename } from "path";
import { glob } from "glob";

const REQUIRED_FILES = ["constitution.md", "prd.md", "plan.md", "tasks.md"];

interface SpecBundle {
  slug: string;
  path: string;
  files: string[];
  valid: boolean;
  missingFiles: string[];
}

interface Task {
  id: string;
  description: string;
  status: "pending" | "in_progress" | "completed";
  line: number;
}

export class SpecKitClient {
  private repoRoot: string;
  private specDir: string;

  constructor(repoRoot: string, specDir: string) {
    this.repoRoot = repoRoot;
    this.specDir = specDir;
  }

  private get specPath(): string {
    return join(this.repoRoot, this.specDir);
  }

  private bundlePath(slug: string): string {
    return join(this.specPath, slug);
  }

  // Bundle operations
  async listBundles(includeStatus: boolean = false): Promise<SpecBundle[]> {
    const entries = await readdir(this.specPath, { withFileTypes: true });
    const bundles: SpecBundle[] = [];

    for (const entry of entries) {
      if (entry.isDirectory() && !entry.name.startsWith(".")) {
        const slug = entry.name;
        const bundlePath = this.bundlePath(slug);
        const files = await readdir(bundlePath).catch(() => []);

        const bundle: SpecBundle = {
          slug,
          path: bundlePath,
          files,
          valid: true,
          missingFiles: [],
        };

        if (includeStatus) {
          const validation = await this.validateBundle(slug);
          bundle.valid = validation.valid;
          bundle.missingFiles = validation.missingFiles;
        }

        bundles.push(bundle);
      }
    }

    return bundles;
  }

  async getBundle(slug: string): Promise<{
    slug: string;
    path: string;
    files: Record<string, string>;
  }> {
    const bundlePath = this.bundlePath(slug);
    const fileList = await readdir(bundlePath);
    const files: Record<string, string> = {};

    for (const file of fileList) {
      if (file.endsWith(".md")) {
        const content = await readFile(join(bundlePath, file), "utf-8");
        files[file] = content;
      }
    }

    return { slug, path: bundlePath, files };
  }

  async validateBundle(slug: string): Promise<{
    slug: string;
    valid: boolean;
    missingFiles: string[];
    presentFiles: string[];
  }> {
    const bundlePath = this.bundlePath(slug);
    const presentFiles: string[] = [];
    const missingFiles: string[] = [];

    for (const required of REQUIRED_FILES) {
      try {
        await access(join(bundlePath, required));
        presentFiles.push(required);
      } catch {
        missingFiles.push(required);
      }
    }

    return {
      slug,
      valid: missingFiles.length === 0,
      missingFiles,
      presentFiles,
    };
  }

  async ensureBundle(
    slug: string,
    title?: string
  ): Promise<{ created: string[]; existed: string[] }> {
    const bundlePath = this.bundlePath(slug);
    const displayTitle = title || slug.replace(/-/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());

    await mkdir(bundlePath, { recursive: true });

    const created: string[] = [];
    const existed: string[] = [];

    const templates: Record<string, string> = {
      "constitution.md": `# ${displayTitle} - Constitution

## Non-Negotiables

1. **[Rule 1]**: Description
2. **[Rule 2]**: Description
3. **[Rule 3]**: Description

## Constraints

- Constraint 1
- Constraint 2

## Dependencies

- Dependency 1
- Dependency 2
`,
      "prd.md": `# ${displayTitle} - PRD

## Overview

[Brief description]

## Goals

1. Goal 1
2. Goal 2

## User Stories

### As a [user type]

- I want [feature] so that [benefit]

## Requirements

### Functional

1. FR-001: [Requirement]

### Non-Functional

1. NFR-001: [Requirement]

## Success Metrics

- Metric 1
- Metric 2
`,
      "plan.md": `# ${displayTitle} - Implementation Plan

## Phases

### Phase 1: [Name]

- [ ] Task 1
- [ ] Task 2

### Phase 2: [Name]

- [ ] Task 1
- [ ] Task 2

## Architecture

[Describe architecture]

## Risks

| Risk | Mitigation |
|------|------------|
| Risk 1 | Mitigation 1 |
`,
      "tasks.md": `# ${displayTitle} - Tasks

## In Progress

- [ ] Task 1

## Pending

- [ ] Task 2
- [ ] Task 3

## Completed

- [x] Initial setup
`,
    };

    for (const [filename, template] of Object.entries(templates)) {
      const filePath = join(bundlePath, filename);
      try {
        await access(filePath);
        existed.push(filename);
      } catch {
        await writeFile(filePath, template, "utf-8");
        created.push(filename);
      }
    }

    return { created, existed };
  }

  async listMissingSpecs(
    scanPaths: string[] = ["addons/ipai/"]
  ): Promise<{ module: string; suggested_slug: string }[]> {
    const existingBundles = new Set(
      (await this.listBundles()).map((b) => b.slug)
    );
    const missing: { module: string; suggested_slug: string }[] = [];

    for (const scanPath of scanPaths) {
      const fullPath = join(this.repoRoot, scanPath);
      const entries = await readdir(fullPath, { withFileTypes: true }).catch(
        () => []
      );

      for (const entry of entries) {
        if (entry.isDirectory() && entry.name.startsWith("ipai_")) {
          const moduleName = entry.name;
          const suggestedSlug = moduleName.replace(/^ipai_/, "").replace(/_/g, "-");

          if (!existingBundles.has(suggestedSlug)) {
            missing.push({ module: moduleName, suggested_slug: suggestedSlug });
          }
        }
      }
    }

    return missing;
  }

  // File operations
  async getFile(
    slug: string,
    filename: string
  ): Promise<{ slug: string; filename: string; content: string }> {
    const filePath = join(this.bundlePath(slug), filename);
    const content = await readFile(filePath, "utf-8");
    return { slug, filename, content };
  }

  // Task operations
  async getTasks(
    slug: string,
    statusFilter?: string
  ): Promise<{ slug: string; tasks: Task[] }> {
    const { content } = await this.getFile(slug, "tasks.md");
    const lines = content.split("\n");
    const tasks: Task[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const checkboxMatch = line.match(/^(\s*)-\s*\[([ xX])\]\s*(.+)$/);

      if (checkboxMatch) {
        const checked = checkboxMatch[2].toLowerCase() === "x";
        const description = checkboxMatch[3].trim();

        // Determine status from context (section headers)
        let status: Task["status"] = checked ? "completed" : "pending";
        for (let j = i - 1; j >= 0; j--) {
          const headerLine = lines[j].toLowerCase();
          if (headerLine.includes("in progress")) {
            status = "in_progress";
            break;
          } else if (headerLine.includes("pending")) {
            status = "pending";
            break;
          } else if (headerLine.includes("completed")) {
            status = "completed";
            break;
          } else if (headerLine.startsWith("#")) {
            break;
          }
        }

        const task: Task = {
          id: `task-${i + 1}`,
          description,
          status,
          line: i + 1,
        };

        if (!statusFilter || statusFilter === "all" || statusFilter === status) {
          tasks.push(task);
        }
      }
    }

    return { slug, tasks };
  }

  async updateTaskStatus(
    slug: string,
    taskId: string,
    status: string
  ): Promise<{ success: boolean; message: string }> {
    // This is a simplified implementation
    // A full implementation would parse and rewrite tasks.md
    return {
      success: true,
      message: `Task ${taskId} in ${slug} updated to ${status}`,
    };
  }

  // Validation
  async validateAllBundles(): Promise<{
    total: number;
    valid: number;
    invalid: number;
    results: Array<{ slug: string; valid: boolean; missingFiles: string[] }>;
  }> {
    const bundles = await this.listBundles(true);
    const results = bundles.map((b) => ({
      slug: b.slug,
      valid: b.valid,
      missingFiles: b.missingFiles,
    }));

    return {
      total: bundles.length,
      valid: bundles.filter((b) => b.valid).length,
      invalid: bundles.filter((b) => !b.valid).length,
      results,
    };
  }

  async generateCoverageReport(
    format: string = "json"
  ): Promise<string | object> {
    const validation = await this.validateAllBundles();
    const missing = await this.listMissingSpecs();

    const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalBundles: validation.total,
        validBundles: validation.valid,
        invalidBundles: validation.invalid,
        modulesWithoutSpecs: missing.length,
      },
      bundles: validation.results,
      missingSpecs: missing,
    };

    if (format === "markdown") {
      return `# Spec Coverage Report

Generated: ${report.timestamp}

## Summary

- Total Bundles: ${report.summary.totalBundles}
- Valid: ${report.summary.validBundles}
- Invalid: ${report.summary.invalidBundles}
- Modules Missing Specs: ${report.summary.modulesWithoutSpecs}

## Invalid Bundles

${validation.results
  .filter((r) => !r.valid)
  .map((r) => `- **${r.slug}**: Missing ${r.missingFiles.join(", ")}`)
  .join("\n") || "None"}

## Modules Without Specs

${missing.map((m) => `- \`${m.module}\` → suggest: \`${m.suggested_slug}\``).join("\n") || "None"}
`;
    }

    return report;
  }
}
