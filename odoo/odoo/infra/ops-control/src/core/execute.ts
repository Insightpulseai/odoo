import { RunbookPlan, RunEvent, Integration } from "./types";

export async function* executeRunbook(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  const now = Date.now();
  
  yield {
    ts: new Date(now).toISOString(),
    level: "info",
    source: "System",
    message: `Starting ${plan.kind} execution...`,
  };

  yield {
    ts: new Date(now + 1000).toISOString(),
    level: "info",
    source: "System",
    message: `Validated inputs: ${plan.inputs.map(i => `${i.key}=${i.value}`).join(", ")}`,
  };

  // Connect to integrations
  for (const integration of plan.integrations) {
    yield {
      ts: new Date(Date.now()).toISOString(),
      level: "info",
      source: integration,
      message: `Connecting to ${integration}...`,
    };
    
    await new Promise(resolve => setTimeout(resolve, 500));
    
    yield {
      ts: new Date(Date.now()).toISOString(),
      level: "success",
      source: integration,
      message: `✓ ${integration} connection established`,
    };
  }

  // Kind-specific execution
  if (plan.kind === "deploy") {
    yield* executeDeploy(plan);
  } else if (plan.kind === "healthcheck") {
    yield* executeHealthcheck(plan);
  } else if (plan.kind === "spec") {
    yield* executeSpec(plan);
  } else if (plan.kind === "incident") {
    yield* executeIncident(plan);
  } else if (plan.kind === "schema_sync") {
    yield* executeSchemaSync(plan);
  }

  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "System",
    message: `${plan.kind} completed successfully`,
  };
}

async function* executeDeploy(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Vercel",
    message: "Building application...",
  };

  await new Promise(resolve => setTimeout(resolve, 3000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "Vercel",
    message: "✓ Build completed (3.2s)",
  };

  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Supabase",
    message: "Running database migrations...",
  };

  await new Promise(resolve => setTimeout(resolve, 2000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "Supabase",
    message: "✓ Migrations applied successfully (2 new migrations)",
  };

  await new Promise(resolve => setTimeout(resolve, 1500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Vercel",
    message: "Deploying to production...",
  };

  await new Promise(resolve => setTimeout(resolve, 2500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "Vercel",
    message: "✓ Deployment successful",
    data: {
      url: "https://app-xyz123.vercel.app",
      commit: "a3f4e21",
      duration: "8.7s",
    },
  };
}

async function* executeHealthcheck(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "System",
    message: "Running health checks...",
  };

  const services = [
    { name: "API Gateway", status: "healthy", latency: 45, source: "Vercel" as Integration },
    { name: "Database", status: "healthy", latency: 12, source: "Supabase" as Integration },
    { name: "Storage", status: "degraded", latency: 210, source: "Supabase" as Integration },
    { name: "Compute", status: "healthy", latency: 35, source: "DigitalOcean" as Integration },
  ];

  for (const service of services) {
    await new Promise(resolve => setTimeout(resolve, 500));
    const level = service.status === "healthy" ? "success" : "warn";
    
    yield {
      ts: new Date(Date.now()).toISOString(),
      level,
      source: service.source,
      message: `${service.status === "healthy" ? "✓" : "⚠"} ${service.name}: ${service.status} (${service.latency}ms)`,
      data: service,
    };
  }

  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "warn",
    source: "System",
    message: "Storage service showing elevated latency. Recommend investigation.",
  };
}

async function* executeSpec(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "System",
    message: "Analyzing requirements...",
  };

  const files = ["constitution.md", "prd.md", "plan.md", "tasks.md"];
  
  for (const file of files) {
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
    
    yield {
      ts: new Date(Date.now()).toISOString(),
      level: "success",
      source: "System",
      message: `✓ Generated spec/${file}`,
    };
  }

  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "GitHub",
    message: "Creating pull request...",
  };

  await new Promise(resolve => setTimeout(resolve, 1500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "GitHub",
    message: "✓ PR created: #847 'Add spec for User Dashboard'",
    data: {
      pr_url: "https://github.com/org/repo/pull/847",
      branch: "spec/user-dashboard",
    },
  };
}

async function* executeIncident(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "System",
    message: "Analyzing error logs...",
  };

  await new Promise(resolve => setTimeout(resolve, 2000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "warn",
    source: "Vercel",
    message: "Found 127 occurrences in the last hour",
  };

  await new Promise(resolve => setTimeout(resolve, 1500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "System",
    message: "Root cause identified: Database connection pool exhaustion",
  };

  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "System",
    message: "Generating fix proposal...",
  };

  await new Promise(resolve => setTimeout(resolve, 2000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "System",
    message: "✓ Fix proposal ready: Increase connection pool size + add connection retry logic",
  };

  await new Promise(resolve => setTimeout(resolve, 1500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "GitHub",
    message: "✓ PR created: #848 'Fix: Increase DB connection pool size'",
    data: {
      pr_url: "https://github.com/org/repo/pull/848",
    },
  };
}

async function* executeSchemaSync(plan: RunbookPlan): AsyncGenerator<RunEvent> {
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Supabase",
    message: "Comparing schemas...",
  };

  await new Promise(resolve => setTimeout(resolve, 2000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "info",
    source: "Supabase",
    message: "Found 3 differences: 2 new tables, 1 modified column",
  };

  await new Promise(resolve => setTimeout(resolve, 1500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "System",
    message: "✓ Generated ERD diagram (DBML format)",
  };

  await new Promise(resolve => setTimeout(resolve, 1000));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "success",
    source: "System",
    message: "✓ Migration files generated (dry-run mode)",
  };

  await new Promise(resolve => setTimeout(resolve, 500));
  
  yield {
    ts: new Date(Date.now()).toISOString(),
    level: "warn",
    source: "System",
    message: "Review migrations before applying to production",
  };
}
