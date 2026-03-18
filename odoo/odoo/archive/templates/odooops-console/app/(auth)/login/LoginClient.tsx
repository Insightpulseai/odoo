"use client";

import { loginAction } from "./server-actions";
import { toast } from "sonner";

export function LoginClient({ next }: { next: string }) {
  async function handleSubmit(formData: FormData) {
    try {
      await loginAction(formData);
    } catch (error) {
      toast.error("Failed to sign in. Please check your credentials.");
    }
  }

  return (
    <main className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Sign In</h1>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          OdooOps Console uses Supabase Auth.
        </p>
      </div>

      <form action={handleSubmit} className="space-y-4">
        <input type="hidden" name="next" value={next} />

        <div className="space-y-2">
          <label htmlFor="email" className="block text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            autoComplete="email"
            placeholder="you@company.com"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            autoComplete="current-password"
            placeholder="••••••••"
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <button
          type="submit"
          className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          Sign In
        </button>
      </form>
    </main>
  );
}
