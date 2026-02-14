import { tokens } from "@ipai/design-tokens";
import { useState, useRef, useEffect } from "react";

export interface DropdownProps {
  trigger: React.ReactNode;
  children: React.ReactNode;
  align?: "left" | "right";
}

export function Dropdown({ trigger, children, align = "left" }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative" ref={dropdownRef}>
      <div onClick={() => setOpen(!open)}>{trigger}</div>
      {open && (
        <div
          className={`absolute top-full mt-2 w-56 rounded-lg shadow-lg ${
            align === "right" ? "right-0" : "left-0"
          }`}
          style={{
            backgroundColor: tokens.color.surface,
            border: `1px solid ${tokens.color.border}`,
            boxShadow: tokens.shadow.lg,
          }}
        >
          {children}
        </div>
      )}
    </div>
  );
}

export function DropdownItem({
  children,
  onClick,
}: {
  children: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      className="w-full text-left px-4 py-2 hover:bg-opacity-50 transition-colors"
      style={{
        color: tokens.color.text.primary,
      }}
      onClick={onClick}
    >
      {children}
    </button>
  );
}
