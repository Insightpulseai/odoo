'use client';

import { useEffect, useState } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed'; platform: string }>;
}

export default function InstallPrompt() {
  const [installEvent, setInstallEvent] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    const handlePrompt = (event: Event) => {
      event.preventDefault();
      setInstallEvent(event as BeforeInstallPromptEvent);
    };

    window.addEventListener('beforeinstallprompt', handlePrompt);
    return () => window.removeEventListener('beforeinstallprompt', handlePrompt);
  }, []);

  if (!installEvent || dismissed) {
    return null;
  }

  return (
    <div className="glass-panel flex items-center justify-between gap-4 rounded-[28px] px-4 py-3">
      <div>
        <p className="text-sm font-semibold text-ink">Install for one-tap receipt capture</p>
        <p className="text-xs text-slate-500">Pin the app and open the camera flow like a native tool.</p>
      </div>
      <div className="flex gap-2">
        <button
          className="rounded-full border border-black/10 px-3 py-2 text-xs font-semibold text-slate-600"
          onClick={() => setDismissed(true)}
          type="button"
        >
          Later
        </button>
        <button
          className="rounded-full bg-ink px-4 py-2 text-xs font-semibold text-white"
          onClick={async () => {
            await installEvent.prompt();
            await installEvent.userChoice;
            setInstallEvent(null);
          }}
          type="button"
        >
          Install
        </button>
      </div>
    </div>
  );
}
