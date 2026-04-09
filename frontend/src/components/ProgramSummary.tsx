import type { ProgramResult, RunResult } from "@/types/run";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ProgramSummaryProps {
  result: RunResult;
  programs: ProgramResult[];
  selectedProgramIndex: number;
  onProgramChange: (index: number) => void;
}

export function ProgramSummary({
  result,
  programs,
  selectedProgramIndex,
  onProgramChange,
}: ProgramSummaryProps) {
  const selectedProgram = programs[selectedProgramIndex];
  const selectedDiscovery = selectedProgram?.discovery ?? result.discovery;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Program Summary</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 text-sm">
        {programs.length > 0 && (
          <div className="space-y-1">
            <label htmlFor="program-selector" className="text-muted-foreground text-xs">
              Scraped Programs
            </label>
            <select
              id="program-selector"
              value={selectedProgramIndex}
              onChange={(e) => onProgramChange(Number(e.target.value))}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            >
              {programs.map((program, index) => (
                <option key={`${program.program_url}-${index}`} value={index}>
                  {program.program_name}
                </option>
              ))}
            </select>
          </div>
        )}
        <div className="flex justify-between">
          <span className="text-muted-foreground">Program</span>
          <span className="font-medium text-right max-w-[60%]">{selectedDiscovery.program_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Type</span>
          <span>{selectedDiscovery.program_type || "—"}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Institution</span>
          <span>{result.college_name}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-muted-foreground">Valid Certificate</span>
          <span>{selectedDiscovery.is_valid_certificate || "—"}</span>
        </div>
      </CardContent>
    </Card>
  );
}
