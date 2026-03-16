import { Command } from "commander";
import { writeFile } from "node:fs/promises";

const program = new Command();
program
  .name("platformkit")
  .description("Platform Kit CLI")
  .version("0.1.0");

program
  .command("introspect")
  .description("Run platform inventory (local/dev mode stub)")
  .option("--out <path>", "output path", "platform-kit/reports/inventory.json")
  .action(async (opts) => {
    // Stub: wired later to call Supabase Edge Function or direct DB introspection
    const payload = {
      ok: true,
      mode: "stub",
      generated_at: new Date().toISOString(),
      out: opts.out
    };
    await writeFile(opts.out, JSON.stringify(payload, null, 2));
    console.log(JSON.stringify(payload, null, 2));
  });

program.parse(process.argv);
