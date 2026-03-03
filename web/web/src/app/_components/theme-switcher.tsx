"use client";

import * as React from "react";
import { useTheme } from "next-themes";
import { Half2Icon, MoonIcon, SunIcon } from "@radix-ui/react-icons";
import clsx from "clsx";
import { Button } from "@/common/button";

export function ThemeSwitcher() {
  const { theme, setTheme } = useTheme();
  const [selectedTheme, setSelectedTheme] = React.useState<string>();

  React.useEffect(() => {
    setSelectedTheme(theme);
  }, [theme]);

  return (
    <div className="flex gap-0.5 rounded-full border border-neutral-stroke1 bg-neutral-bg1 p-1 text-center">
      <SwitchButton selectedTheme={selectedTheme} setTheme={setTheme} theme="light">
        <SunIcon color="currentColor" height={16} width={16} />
      </SwitchButton>
      <SwitchButton selectedTheme={selectedTheme} setTheme={setTheme} theme="system">
        <Half2Icon color="currentColor" height={16} width={16} />
      </SwitchButton>
      <SwitchButton selectedTheme={selectedTheme} setTheme={setTheme} theme="dark">
        <MoonIcon color="currentColor" height={16} width={16} />
      </SwitchButton>
    </div>
  );
}

function SwitchButton({
  selectedTheme,
  theme,
  setTheme,
  children,
}: {
  selectedTheme?: string;
  theme: string;
  setTheme: (theme: string) => void;
  children?: React.ReactNode;
}) {
  return (
    <Button
      unstyled
      aria-label={`${theme} theme`}
      className={clsx(
        "flex! size-6! items-center justify-center rounded-full p-[3px]! text-neutral-fg2",
        "data-[selected='true']:bg-neutral-bg3 data-[selected='true']:text-neutral-fg1",
        "hover:bg-neutral-bg2 hover:text-neutral-fg1",
      )}
      data-selected={selectedTheme === theme}
      onClick={() => setTheme(theme)}
    >
      {children}
    </Button>
  );
}
