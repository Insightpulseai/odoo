'use client';

import { useMsal } from '@/lib/auth/MsalProvider';

export default function SignInBar() {
  const { enabled, ready, account, signIn, signOut } = useMsal();

  if (!ready) return null;

  if (!enabled) {
    return (
      <div className="rounded-full border border-dashed border-black/10 bg-white/60 px-4 py-2 text-xs text-slate-500">
        Single sign-on not configured. Set NEXT_PUBLIC_ENTRA_CLIENT_ID + TENANT_ID to enable.
      </div>
    );
  }

  if (!account) {
    return (
      <button
        type="button"
        onClick={() => void signIn()}
        className="rounded-full bg-ink px-4 py-2 text-xs font-semibold text-white"
      >
        Sign in with Microsoft
      </button>
    );
  }

  return (
    <div className="flex items-center gap-3 rounded-full bg-white/80 px-4 py-2 text-xs text-slate-600">
      <span className="font-semibold text-ink">{account.name ?? account.username}</span>
      <button
        type="button"
        onClick={() => void signOut()}
        className="rounded-full border border-black/10 px-3 py-1 text-[11px] font-semibold text-slate-600"
      >
        Sign out
      </button>
    </div>
  );
}
