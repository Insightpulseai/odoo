import { CopyButton } from "./copy-button";
import { FileIcon } from "@radix-ui/react-icons";
import s from "./code-snippet.module.scss";

export type CodeSnippetFragment = {
  _id: string;
  _title?: string;
  code: {
    code: string;
    language: string;
  };
};

export function CodeSnippet({ code, _id, _title = "Untitled" }: CodeSnippetFragment) {
  return (
    <div className={s["code-snippet"]}>
      <div>
        <header className={s.header}>
          <div className="flex items-center">
            <span className="mr-2 size-4">
              <FileIcon />
            </span>
            <span className="text-neutral-fg2">{_title}</span>
          </div>
          <CopyButton code={code.code} />
        </header>
        <div className={s.content}>
          <pre><code>{code.code}</code></pre>
        </div>
      </div>
    </div>
  );
}
