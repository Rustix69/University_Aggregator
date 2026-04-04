import type { Run } from "@/types/run";
import { MOCK_RUN } from "@/data/mockRun";

const USE_MOCK = true; // Toggle to false when connecting real backend

// Simulates the running → completed flow
let mockPhase = 0;

export async function createRun(collegeName: string): Promise<Run> {
  if (USE_MOCK) {
    mockPhase = 0;
    return {
      run_id: MOCK_RUN.run_id,
      college_name: collegeName,
      status: "running",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      finished_at: null,
      result: null,
      error: null,
    };
  }
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ college_name: collegeName }),
  });
  if (!res.ok) throw new Error("Failed to create run");
  return res.json();
}

export async function getRun(runId: string): Promise<Run> {
  if (USE_MOCK) {
    mockPhase++;
    // Simulate: phase 1-2 = running, phase 3+ = completed
    if (mockPhase < 3) {
      return {
        run_id: runId,
        college_name: MOCK_RUN.college_name,
        status: "running",
        created_at: MOCK_RUN.created_at,
        updated_at: new Date().toISOString(),
        finished_at: null,
        result: null,
        error: null,
      };
    }
    return { ...MOCK_RUN };
  }
  const res = await fetch(`${import.meta.env.VITE_API_BASE_URL}/runs/${runId}`);
  if (!res.ok) throw new Error("Failed to fetch run");
  return res.json();
}
