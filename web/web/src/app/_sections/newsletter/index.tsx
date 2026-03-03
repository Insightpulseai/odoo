import * as React from "react";
import { Section } from "@/common/layout";
import { Input } from "@/common/input";

export function Newsletter() {
  return (
    <Section
      className="bg-neutral-bg2 py-10!"
      container="full"
    >
      <div className="container mx-auto flex flex-col gap-4 px-6 lg:flex-row lg:justify-between">
        <div className="flex flex-1 flex-col items-start gap-1">
          <h5 className="text-xl font-medium lg:text-2xl">Stay up to date</h5>
          <p className="text text-neutral-fg3 lg:text-lg">
            Subscribe to our newsletter for the latest updates and features.
          </p>
        </div>

        <form>
          <Input
            name="email"
            type="email"
            placeholder="Enter your email"
            buttonContent="Subscribe"
          />
        </form>
      </div>
    </Section>
  );
}
