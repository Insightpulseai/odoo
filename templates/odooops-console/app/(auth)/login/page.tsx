import { redirect } from "next/navigation";
import { createSupabaseServerClient } from "@/lib/supabase/server";
import { LoginClient } from "./LoginClient";

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ next?: string }>;
}) {
  const supabase = createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();

  // If already authenticated, redirect to app
  if (user) {
    const params = await searchParams;
    const next = params?.next || "/";
    redirect(next);
  }

  const params = await searchParams;
  const next = params?.next || "/";

  return <LoginClient next={next} />;
}
