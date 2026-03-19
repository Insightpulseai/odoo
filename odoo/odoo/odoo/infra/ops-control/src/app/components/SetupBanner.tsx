import { useState } from "react";
import { supabase, isSupabaseConfigured } from "../../lib/supabase";
import { toast } from "sonner";

export function SetupBanner() {
  const [testing, setTesting] = useState(false);
  const [testResults, setTestResults] = useState<{
    templates: number;
    specs: number;
    runs: number;
  } | null>(null);

  const runConnectionTest = async () => {
    setTesting(true);
    setTestResults(null);
    
    try {
      // Test templates
      const { data: templates, error: templatesError } = await supabase
        .from("run_templates")
        .select("count");
      
      if (templatesError) throw new Error(`Templates: ${templatesError.message}`);

      // Test spec docs
      const { data: specs, error: specsError } = await supabase
        .from("spec_docs")
        .select("count");
      
      if (specsError) throw new Error(`Spec Docs: ${specsError.message}`);

      // Test runs
      const { data: runs, error: runsError } = await supabase
        .from("runs")
        .select("count");
      
      if (runsError) throw new Error(`Runs: ${runsError.message}`);

      const results = {
        templates: templates?.length || 0,
        specs: specs?.length || 0,
        runs: runs?.length || 0,
      };

      setTestResults(results);
      
      if (results.templates === 0 || results.specs === 0) {
        toast.warning("Database tables exist but no seed data found. Run the migrations!");
      } else {
        toast.success("✅ Database connection successful!");
      }
    } catch (error) {
      console.error("Connection test failed:", error);
      toast.error(error instanceof Error ? error.message : "Connection test failed");
    } finally {
      setTesting(false);
    }
  };

  if (!isSupabaseConfigured) {
    return null;
  }

  return (
    <div className="bg-blue-50 border-b border-blue-200 px-6 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="text-sm">
            <span className="font-medium">Ops Control Room</span>
            <span className="opacity-70 ml-2">
              {testResults ? (
                <>
                  • {testResults.templates} templates • {testResults.specs} spec docs • {testResults.runs} runs
                </>
              ) : (
                "• Test database connection to verify setup"
              )}
            </span>
          </div>
        </div>
        <button
          onClick={runConnectionTest}
          disabled={testing}
          className="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {testing ? "Testing..." : "Test Connection"}
        </button>
      </div>
      
      {testResults && (testResults.templates === 0 || testResults.specs === 0) && (
        <div className="mt-3 text-xs bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="font-medium text-yellow-900 mb-1">⚠️ Setup Required</div>
          <div className="text-yellow-800">
            Database tables exist but are missing seed data. 
            Run the migrations in Supabase SQL Editor:
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li><code className="bg-yellow-100 px-1 rounded">/supabase/migrations/20250103000000_ops_schema.sql</code></li>
              <li><code className="bg-yellow-100 px-1 rounded">/supabase/migrations/20250103000001_enable_anon_access.sql</code></li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
