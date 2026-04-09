import { useState, useEffect, useCallback } from "react";
import type { Run } from "@/types/run";
import { createRun, getRun } from "@/lib/api";
import { SearchBar } from "@/components/SearchBar";
import { RunStatusPanel } from "@/components/RunStatusPanel";
import { ProgramSummary } from "@/components/ProgramSummary";
import { DiscoveryLinks } from "@/components/DiscoveryLinks";
import { FieldsTable } from "@/components/FieldsTable";
import { CsvPaths } from "@/components/CsvPaths";
import { EmptyState } from "@/components/EmptyState";
import { ErrorState } from "@/components/ErrorState";

export default function Index() {
  const [run, setRun] = useState<Run | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedProgramIndex, setSelectedProgramIndex] = useState(0);

  const isTerminal = run && (run.status === "completed" || run.status === "failed" || run.status === "invalid_program");

  // Polling
  useEffect(() => {
    if (!run || isTerminal) return;
    const interval = setInterval(async () => {
      try {
        const updated = await getRun(run.run_id);
        setRun(updated);
      } catch (e) {
        console.error("Polling error:", e);
      }
    },5000);
    return () => clearInterval(interval);
  }, [run, isTerminal]);

  const handleSearch = useCallback(async (collegeName: string) => {
    setIsSubmitting(true);
    try {
      const newRun = await createRun(collegeName);
      setRun(newRun);
    } catch (e) {
      console.error("Error creating run:", e);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  const isCompleted = run?.status === "completed" && run.result;
  const isFailed = run?.status === "failed" || run?.status === "invalid_program";
  const programs = run?.result?.programs ?? [];
  const selectedProgram =
    programs.length > 0
      ? programs[Math.min(selectedProgramIndex, programs.length - 1)]
      : null;

  useEffect(() => {
    setSelectedProgramIndex(0);
  }, [run?.run_id]);

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b px-6 py-4">
        <h1 className="text-xl font-semibold">University Aggregator</h1>
      </header>

      <main className="flex-1 max-w-5xl mx-auto w-full px-4 py-8 space-y-6">
        {/* Search */}
        <div className="flex justify-center">
          <SearchBar onSearch={handleSearch} isLoading={isSubmitting || (!!run && !isTerminal)} />
        </div>

        {/* Empty state */}
        {!run && <EmptyState />}

        {/* Status */}
        {run && <RunStatusPanel run={run} />}

        {/* Error/Invalid */}
        {isFailed && run && <ErrorState run={run} />}

        {/* Results */}
        {isCompleted && run.result && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <ProgramSummary
                result={run.result}
                programs={programs}
                selectedProgramIndex={selectedProgramIndex}
                onProgramChange={setSelectedProgramIndex}
              />
              <DiscoveryLinks discovery={selectedProgram?.discovery ?? run.result.discovery} />
            </div>

            

            <div>
              <h2 className="text-lg font-semibold mb-3">Extracted Fields</h2>
              <FieldsTable fields={selectedProgram?.fields ?? run.result.fields} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
