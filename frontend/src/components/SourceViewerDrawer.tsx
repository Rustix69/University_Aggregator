import { useState } from "react";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { ExternalLink, Copy, Check } from "lucide-react";

interface SourceViewerDrawerProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  url: string;
  quote: string;
  fieldLabel: string;
}

export function SourceViewerDrawer({ open, onOpenChange, url, quote, fieldLabel }: SourceViewerDrawerProps) {
  const [iframeFailed, setIframeFailed] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(quote);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-xl overflow-y-auto">
        <SheetHeader>
          <SheetTitle>Source: {fieldLabel}</SheetTitle>
          <SheetDescription className="break-all text-xs">{url}</SheetDescription>
        </SheetHeader>

        <div className="mt-4 space-y-4">
          {/* Iframe or fallback */}
          <div className="border rounded-md overflow-hidden" style={{ height: 350 }}>
            {!iframeFailed ? (
              <iframe
                src={url}
                title="Source viewer"
                className="w-full h-full"
                sandbox="allow-same-origin"
                onError={() => setIframeFailed(true)}
                onLoad={(e) => {
                  try {
                    // Access check - will throw if blocked
                    const frame = e.currentTarget;
                    if (!frame.contentDocument && !frame.contentWindow) {
                      setIframeFailed(true);
                    }
                  } catch {
                    setIframeFailed(true);
                  }
                }}
              />
            ) : (
              <div className="flex flex-col items-center justify-center h-full gap-3 text-muted-foreground">
                <p className="text-sm">This page cannot be embedded (blocked by the source site).</p>
                <Button variant="outline" size="sm" asChild>
                  <a href={url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="h-4 w-4 mr-1" />
                    Open in new tab
                  </a>
                </Button>
              </div>
            )}
          </div>

          {/* Evidence quote */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium">Evidence</h4>
              <Button variant="ghost" size="sm" onClick={handleCopy}>
                {copied ? <Check className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
                {copied ? "Copied" : "Copy Quote"}
              </Button>
            </div>
            <div className="rounded-md border p-3 text-sm">
              <mark className="bg-accent px-0.5">{quote}</mark>
            </div>
          </div>

          <Button variant="outline" className="w-full" asChild>
            <a href={url} target="_blank" rel="noopener noreferrer">
              <ExternalLink className="h-4 w-4 mr-1" />
              Open in new tab
            </a>
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
