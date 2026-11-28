"use client";
import Button from "@/components/common/button";
import { toast } from "@/utils/toast";
import { Check, Copy, Download, ShieldAlert } from "lucide-react";
import { useState } from "react";

type BackupCodesProp = Readonly<{ codes: string[]; onContinue: () => void }>;

const COPIED_MS = 2000;

export default function BackupCodes({ codes, onContinue }: BackupCodesProp) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(codes.join("\n"));
    } catch {
      toast.error("Couldn't copy. Select the codes and copy them by hand.");
      return;
    }
    setCopied(true);
    toast.success("Backup codes copied");
    setTimeout(() => setCopied(false), COPIED_MS);
  };

  const download = () => {
    const file = new Blob([codes.join("\n") + "\n"], { type: "text/plain" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(file);
    link.download = "renttrace-backup-codes.txt";
    link.click();
    URL.revokeObjectURL(link.href);
    toast.success("Backup codes downloaded");
  };

  return (
    <>
      <div
        role="note"
        className="flex gap-3 rounded-lg border border-warning-border bg-warning-background p-3 text-body-sm"
      >
        <ShieldAlert
          aria-hidden
          className="mt-0.5 size-5 shrink-0 text-warning"
        />
        <p className="text-fg-primary">
          This is the only time these codes are shown. Each one works once.
        </p>
      </div>

      <ul className="mt-4 grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-default bg-default font-mono text-body-sm">
        {codes.map((code) => (
          <li
            key={code}
            className="bg-subtle px-3 py-3 text-center tracking-wider select-all"
          >
            {code}
          </li>
        ))}
      </ul>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <Button
          type="button"
          variant="secondary"
          onClick={copy}
          className="gap-2 active:translate-y-px motion-reduce:active:translate-y-0"
        >
          {copied ? (
            <Check aria-hidden className="size-4" />
          ) : (
            <Copy aria-hidden className="size-4" />
          )}
          {copied ? "Copied" : "Copy"}
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={download}
          className="gap-2 active:translate-y-px motion-reduce:active:translate-y-0"
        >
          <Download aria-hidden className="size-4" />
          Download
        </Button>
      </div>

      <Button
        type="button"
        onClick={onContinue}
        className="mt-3 w-full active:translate-y-px motion-reduce:active:translate-y-0"
      >
        I&apos;ve saved them, continue
      </Button>
    </>
  );
}
