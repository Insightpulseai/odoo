import NextForm from "next/form";
import { Section } from "@/common/layout";
import { FormLayout } from "@/app/_components/form-layout";
import { Button } from "@/common/button";
import { ArrowRightIcon } from "@radix-ui/react-icons";
import { LabeledInput, LabeledTextarea, LabeledWrapper } from "@/app/_components/labeled-input";
import { Select } from "@/app/_components/select";

type FormField = {
  id: string;
  name: string;
  label: string;
  type: string;
  required?: boolean;
  placeholder?: string;
  options?: string[];
};

type FormProps = {
  title: string;
  subtitle?: React.ReactNode;
  ctaLabel?: string;
  ctaIntent?: "primary" | "secondary";
  fields?: FormField[];
};

const defaultFields: FormField[] = [
  { id: "name", name: "name", label: "Name", type: "text", required: true, placeholder: "Your name" },
  { id: "email", name: "email", label: "Email", type: "email", required: true, placeholder: "you@example.com" },
  { id: "message", name: "message", label: "Message", type: "textarea", required: false, placeholder: "How can we help?" },
];

export function Form({
  title = "Get in touch",
  subtitle,
  ctaLabel = "Submit",
  ctaIntent = "primary",
  fields = defaultFields,
}: FormProps) {
  return (
    <Section>
      <FormLayout
        subtitle={subtitle}
        title={title}
      >
        <NextForm
          className="flex flex-col gap-3"
          action=""
        >
          {fields.map((field) => {
            if (field.type === "textarea") {
              return (
                <LabeledTextarea key={field.id} rows={8} className="max-h-64 min-h-16" label={field.label} id={field.id} name={field.name} required={field.required} placeholder={field.placeholder} />
              );
            } else if (field.type === "select" || field.type === "radio") {
              return (
                <LabeledWrapper key={field.id} label={field.label} id={field.id}>
                  <Select id={field.id} name={field.name} required={field.required}>
                    {(field.options ?? []).map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </Select>
                </LabeledWrapper>
              );
            } else {
              return <LabeledInput key={field.id} label={field.label} id={field.id} name={field.name} type={field.type} required={field.required} placeholder={field.placeholder} />;
            }
          })}
          <div className="mt-3 flex items-center justify-between">
            <Button
              icon={<ArrowRightIcon className="size-5" />}
              iconSide="right"
              intent={ctaIntent}
              type="submit"
            >
              {ctaLabel}
            </Button>
          </div>
        </NextForm>
      </FormLayout>
    </Section>
  );
}
