interface RunbookTemplate {
  id: string;
  slug: string;
  title: string;
  description: string;
  template_yaml: string;
}

interface RunbookTemplateCardProps {
  template: RunbookTemplate;
  onRun: (templateId: string) => void;
  onEdit: (template: RunbookTemplate) => void;
}

export function RunbookTemplateCard({ template, onRun, onEdit }: RunbookTemplateCardProps) {
  return (
    <div className="p-4 border rounded-2xl shadow-sm bg-white hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="font-semibold text-lg mb-1">{template.title}</div>
          <div className="text-sm opacity-70 mb-2">{template.description}</div>
          <div className="text-xs opacity-60 font-mono bg-gray-50 px-2 py-1 rounded inline-block">
            slug: {template.slug}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="px-4 py-2 border rounded-lg hover:bg-gray-50 transition-colors"
            onClick={() => onEdit(template)}
          >
            Edit
          </button>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            onClick={() => onRun(template.id)}
          >
            Run
          </button>
        </div>
      </div>
    </div>
  );
}
