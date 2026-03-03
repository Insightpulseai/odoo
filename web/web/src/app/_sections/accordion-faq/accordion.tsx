"use client";
import * as AccordionPrimitive from "@radix-ui/react-accordion";
import { MinusCircledIcon, PlusCircledIcon } from "@radix-ui/react-icons";
import * as React from "react";

type FaqItem = {
  title: string;
  answer: string;
};

export function Accordion({
  items,
}: {
  items: FaqItem[];
}) {
  const [activeItems, setActiveItems] = React.useState<string[]>([]);

  return (
    <AccordionPrimitive.Root
      className="flex w-full flex-col items-stretch gap-2 lg:gap-8"
      type="multiple"
      value={activeItems}
      onValueChange={(activeItems) => setActiveItems(activeItems)}
    >
      {items.map((item) => (
        <AccordionItem
          key={item.title}
          title={item.title}
          answer={item.answer}
          isActive={activeItems.includes(item.title)}
        />
      ))}
    </AccordionPrimitive.Root>
  );
}

function AccordionItem({
  title,
  answer,
  isActive,
}: FaqItem & { isActive: boolean }) {
  return (
    <AccordionPrimitive.Item key={title} className="flex flex-col" value={title}>
      <AccordionPrimitive.Header>
        <AccordionPrimitive.Trigger
          className="ring-brand-foreground flex w-full items-start gap-3 rounded-md py-2 text-lg leading-relaxed font-medium tracking-tighter outline-hidden focus-visible:ring-3"
        >
          {isActive ? (
            <MinusCircledIcon className="my-1.5 size-4 shrink-0" />
          ) : (
            <PlusCircledIcon className="my-1.5 size-4 shrink-0" />
          )}

          <span className="text-start">{title}</span>
        </AccordionPrimitive.Trigger>
      </AccordionPrimitive.Header>
      <AccordionPrimitive.Content className="text-neutral-fg3 data-[state=closed]:animate-slideUp data-[state=open]:animate-slideDown transform overflow-hidden pl-7 leading-relaxed tracking-tight">
        <div>{answer}</div>
      </AccordionPrimitive.Content>
    </AccordionPrimitive.Item>
  );
}
