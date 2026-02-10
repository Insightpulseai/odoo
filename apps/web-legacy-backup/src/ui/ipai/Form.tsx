import { tokens } from "@ipai/design-tokens";
import { forwardRef } from "react";

export const Form = forwardRef<
  HTMLFormElement,
  React.FormHTMLAttributes<HTMLFormElement>
>(({ className, ...props }, ref) => (
  <form ref={ref} className={`space-y-6 ${className}`} {...props} />
));

Form.displayName = "Form";

export const FormField = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={`space-y-2 ${className}`} {...props} />
));

FormField.displayName = "FormField";

export const FormLabel = forwardRef<
  HTMLLabelElement,
  React.LabelHTMLAttributes<HTMLLabelElement>
>(({ className, ...props }, ref) => (
  <label
    ref={ref}
    className={`text-sm font-medium ${className}`}
    style={{ color: tokens.color.text.primary }}
    {...props}
  />
));

FormLabel.displayName = "FormLabel";

export const FormInput = forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={`w-full h-12 px-4 rounded-lg transition-all focus:outline-none focus:ring-2 ${className}`}
    style={{
      border: `1px solid ${tokens.color.border}`,
      backgroundColor: tokens.color.surface,
      color: tokens.color.text.primary,
    }}
    {...props}
  />
));

FormInput.displayName = "FormInput";

export const FormMessage = forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement> & { type?: "error" | "info" }
>(({ className, type = "error", ...props }, ref) => (
  <p
    ref={ref}
    className={`text-sm ${className}`}
    style={{
      color: type === "error" ? tokens.color.semantic.error : tokens.color.text.secondary,
    }}
    {...props}
  />
));

FormMessage.displayName = "FormMessage";
