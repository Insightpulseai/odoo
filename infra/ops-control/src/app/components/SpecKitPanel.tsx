import { useState, useEffect } from "react";
import { supabase } from "../../lib/supabase";
import { toast } from "sonner";

interface SpecDoc {
  id: string;
  slug: string;
  title: string;
  content: string;
  updated_at: string;
}

export function SpecKitPanel() {
  const [docs, setDocs] = useState<SpecDoc[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [draft, setDraft] = useState("");
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDocs();
  }, []);

  async function loadDocs() {
    try {
      const { data, error } = await supabase
        .from("spec_docs")
        .select("*")
        .order("title", { ascending: true });

      if (error) {
        console.error("Error loading spec docs:", error);
        throw error;
      }

      setDocs(data || []);
      if (data && data.length > 0) {
        setActiveId(data[0].id);
        setDraft(data[0].content);
      }
    } catch (error) {
      console.error("Error loading spec docs:", error);
      toast.error("Failed to load spec docs");
    } finally {
      setLoading(false);
    }
  }

  async function saveDoc() {
    if (!activeId) return;

    setSaving(true);
    try {
      const { data, error } = await supabase
        .from("spec_docs")
        .update({ content: draft })
        .eq("id", activeId)
        .select()
        .single();

      if (error) throw error;

      setDocs((prev) => prev.map((d) => (d.id === activeId ? data : d)));
      toast.success("Spec document saved");
    } catch (error) {
      console.error("Error saving spec doc:", error);
      toast.error("Failed to save spec doc");
    } finally {
      setSaving(false);
    }
  }

  const active = docs.find((d) => d.id === activeId);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center">
          <div className="text-lg opacity-70">Loading Spec Kit...</div>
        </div>
      </div>
    );
  }

  if (docs.length === 0) {
    return (
      <div className="flex items-center justify-center p-12">
        <div className="text-center max-w-2xl">
          <div className="text-lg font-semibold mb-3">No Spec Kit Docs Found</div>
          <div className="opacity-70 mb-4">
            The Continue Orchestrator spec kit documents need to be loaded into your Supabase database.
          </div>
          <div className="text-left bg-gray-50 p-4 rounded-lg text-sm space-y-2">
            <div className="font-medium">Setup Instructions:</div>
            <ol className="list-decimal list-inside space-y-1 opacity-70">
              <li>Open your Supabase Dashboard SQL Editor</li>
              <li>Run the migration in <code className="bg-white px-2 py-1 rounded">/supabase/migrations/20250103000000_ops_schema.sql</code></li>
              <li>Run the anonymous access migration in <code className="bg-white px-2 py-1 rounded">/supabase/migrations/20250103000001_enable_anon_access.sql</code></li>
              <li>Refresh this page</li>
            </ol>
            <div className="mt-4 pt-3 border-t">
              <div className="font-medium mb-1">Need help?</div>
              <div className="opacity-70">See <code className="bg-white px-2 py-1 rounded">/SUPABASE_SETUP_GUIDE.md</code> for detailed setup instructions.</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-4 gap-4">
      <div className="col-span-1 border rounded-2xl p-4 h-[calc(100vh-200px)] overflow-y-auto">
        <div className="font-semibold mb-3">Spec Kit Documents</div>
        <div className="space-y-2">
          {docs.map((d) => (
            <button
              key={d.id}
              className={`w-full text-left px-3 py-2 border rounded-xl transition-colors ${
                d.id === activeId ? "bg-blue-50 border-blue-300" : "hover:bg-gray-50"
              }`}
              onClick={() => {
                setActiveId(d.id);
                setDraft(d.content);
              }}
            >
              <div className="text-sm font-medium">{d.title}</div>
              <div className="text-xs opacity-60 mt-1">{d.slug}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="col-span-3 border rounded-2xl p-4 h-[calc(100vh-200px)] flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <div>
            <div className="font-semibold">{active?.title || "—"}</div>
            <div className="text-xs opacity-60">{active?.slug || ""}</div>
          </div>
          <button
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            disabled={!active || saving}
            onClick={saveDoc}
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>

        <textarea
          className="flex-1 w-full border rounded-xl p-4 font-mono text-sm resize-none"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Edit spec document..."
        />
      </div>
    </div>
  );
}