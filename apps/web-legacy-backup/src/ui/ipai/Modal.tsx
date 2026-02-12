import { tokens } from "@ipai/design-tokens";
import { Card } from "./Card";
import { useEffect } from "react";

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  title?: string;
}

export function Modal({ open, onClose, children, title }: ModalProps) {
  useEffect(() => {
    if (open) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: tokens.color.overlay }}
      onClick={onClose}
    >
      <Card
        variant="elevated"
        className="w-full max-w-lg"
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <div
            className="border-b px-6 py-4"
            style={{ borderColor: tokens.color.border }}
          >
            <h2 className="text-xl font-extrabold" style={{ color: tokens.color.primary }}>
              {title}
            </h2>
          </div>
        )}
        <div className="p-6">{children}</div>
      </Card>
    </div>
  );
}
