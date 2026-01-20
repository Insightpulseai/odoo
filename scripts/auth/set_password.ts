/**
 * Set Password for Supabase User
 *
 * Admin script to set/reset a password for a Supabase Auth user.
 * Use this for confirmed users who need a password set.
 *
 * Usage:
 *   npx ts-node scripts/auth/set_password.ts
 *
 * Required environment variables:
 *   SUPABASE_URL
 *   SUPABASE_SERVICE_ROLE_KEY
 *   TARGET_EMAIL (or pass as first argument)
 *   SUPABASE_TEMP_PASSWORD (optional, will prompt if not set)
 */

import "dotenv/config";
import { createClient } from "@supabase/supabase-js";
import * as readline from "readline";

const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

async function prompt(question: string): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  return new Promise((resolve) => {
    rl.question(question, (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function main() {
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    console.error("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
    process.exit(1);
  }

  // Get target email
  let email = process.env.TARGET_EMAIL || process.argv[2];
  if (!email) {
    email = await prompt("Enter email address: ");
  }

  if (!email) {
    console.error("Error: Email address required");
    process.exit(1);
  }

  // Get password
  let password = process.env.SUPABASE_TEMP_PASSWORD;
  if (!password) {
    password = await prompt("Enter new password (min 8 chars): ");
  }

  if (!password || password.length < 8) {
    console.error("Error: Password must be at least 8 characters");
    process.exit(1);
  }

  // Create admin client
  const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
    auth: {
      autoRefreshToken: false,
      persistSession: false,
    },
  });

  console.log(`Looking up user: ${email}`);

  try {
    // List users to find target
    const { data: usersData, error: listError } = await supabase.auth.admin.listUsers({
      page: 1,
      perPage: 100,
    });

    if (listError) {
      console.error("Error listing users:", listError.message);
      process.exit(1);
    }

    const targetUser = usersData?.users.find((u) => u.email === email);

    if (!targetUser) {
      console.error(`User not found: ${email}`);
      process.exit(1);
    }

    console.log(`Found user: id=${targetUser.id}`);
    console.log(`  Email confirmed: ${targetUser.email_confirmed_at ? "Yes" : "No"}`);
    console.log(`  Last sign in: ${targetUser.last_sign_in_at || "Never"}`);

    // Confirm email if not confirmed
    if (!targetUser.email_confirmed_at) {
      console.log("Confirming email...");
      const { error: confirmError } = await supabase.auth.admin.updateUserById(targetUser.id, {
        email_confirm: true,
      });

      if (confirmError) {
        console.error("Error confirming email:", confirmError.message);
        process.exit(1);
      }
      console.log("Email confirmed.");
    }

    // Set password
    console.log("Setting password...");
    const { error: updateError } = await supabase.auth.admin.updateUserById(targetUser.id, {
      password: password,
    });

    if (updateError) {
      console.error("Error setting password:", updateError.message);
      process.exit(1);
    }

    console.log(`\nSuccess! Password updated for ${email}`);
    console.log("\nUser can now sign in with:");
    console.log(`  Email: ${email}`);
    console.log(`  Password: [the password you provided]`);
  } catch (err) {
    console.error("Unexpected error:", err);
    process.exit(1);
  }
}

main();
