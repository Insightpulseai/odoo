import { Section } from "@/common/layout";

export type FreeformText = {
  body: React.ReactNode;
};

export function FreeformText({ body }: FreeformText) {
  return (
    <Section>
      <div className="prose prose-zinc max-w-prose text-start font-normal text-md w-full leading-relaxed">
        {body}
      </div>
    </Section>
  );
}
