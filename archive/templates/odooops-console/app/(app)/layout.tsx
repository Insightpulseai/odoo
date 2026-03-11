import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import Link from "next/link";

export default async function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const supabase = createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();

  // Redirect to login if not authenticated
  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-8">
              <Link
                href="/"
                className="text-xl font-semibold text-gray-900 dark:text-white"
              >
                OdooOps Console
              </Link>
              <div className="hidden md:flex space-x-4">
                <Link
                  href="/app/projects"
                  className="text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Projects
                </Link>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {user.email}
              </span>
              <form action="/logout" method="post">
                <button
                  type="submit"
                  className="text-sm text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                >
                  Sign out
                </button>
              </form>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
