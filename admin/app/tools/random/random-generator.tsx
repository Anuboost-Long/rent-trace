"use client";
import Button from "@/components/common/button";
import {
  entropyBits,
  FERNET_LENGTH,
  generateRandom,
  MAX_LENGTH,
  type RandomKind,
} from "@/utils/random";
import clsx from "clsx";
import { Check, Copy, RefreshCw } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const KINDS: { value: RandomKind; label: string; hint: string }[] = [
  {
    value: "alphanumeric",
    label: "Letters & numbers",
    hint: "Upper and lower case letters and digits.",
  },
  { value: "digits", label: "Numbers", hint: "Digits only." },
  {
    value: "hex",
    label: "Hex",
    hint: "Digits and the letters a to f. A good fit for API keys and signing keys.",
  },
  {
    value: "fernet",
    label: "Fernet key",
    hint: "A ready-made 44-character key, like the one MFA_ENCRYPTION_KEY needs.",
  },
];

const DEFAULT_LENGTH = 32;
const COPIED_MS = 2000;

export default function RandomGenerator() {
  const [kind, setKind] = useState<RandomKind>("alphanumeric");
  const [length, setLength] = useState(DEFAULT_LENGTH);
  const [value, setValue] = useState("");
  const [fresh, setFresh] = useState(0);
  const [copied, setCopied] = useState(false);
  const copiedTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

  const isFernet = kind === "fernet";
  const shownLength = isFernet ? FERNET_LENGTH : length;

  const generate = (nextKind = kind, nextLength = length) => {
    setValue(generateRandom(nextKind, nextLength));
    setCopied(false);
  };

  useEffect(() => {
    queueMicrotask(() => generate());
    return () => clearTimeout(copiedTimer.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const generateAgain = () => {
    generate();
    setFresh((count) => count + 1);
  };

  const copy = async () => {
    if (!value) return;
    await navigator.clipboard.writeText(value);
    setCopied(true);
    clearTimeout(copiedTimer.current);
    copiedTimer.current = setTimeout(() => setCopied(false), COPIED_MS);
  };

  const changeLength = (next: number) => {
    const clamped = Math.min(MAX_LENGTH, Math.max(1, next || 1));
    setLength(clamped);
    generate(kind, clamped);
  };

  return (
    <div className="flex flex-col gap-8">
      <section
        aria-label="Generated value"
        className="rounded-2xl border border-foreground/15"
      >
        <button
          type="button"
          onClick={copy}
          disabled={!value}
          aria-label="Copy value"
          className="block w-full rounded-t-2xl p-6 text-left hover:bg-foreground/3 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-foreground"
        >
          <span
            key={fresh}
            className="animate-panel-in block font-mono text-xl leading-relaxed break-all motion-reduce:animate-none sm:text-2xl"
          >
            {value || <span className="text-foreground/40">Generating…</span>}
          </span>
        </button>
        <div className="flex flex-wrap items-center justify-between gap-3 border-t border-foreground/15 px-6 py-3">
          <p className="text-sm text-foreground/70">
            {shownLength} characters, about {entropyBits(kind, shownLength)}{" "}
            bits of randomness
          </p>
          <div className="flex gap-2">
            <Button
              variant="quiet"
              size="sm"
              className="gap-2"
              onClick={generateAgain}
            >
              <RefreshCw aria-hidden className="size-4" />
              Generate again
            </Button>
            <Button
              size="sm"
              className="gap-2"
              onClick={copy}
              disabled={!value}
            >
              {copied ? (
                <Check aria-hidden className="size-4" />
              ) : (
                <Copy aria-hidden className="size-4" />
              )}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
        </div>
        <p role="status" className="sr-only">
          {copied ? "Copied to clipboard" : ""}
        </p>
      </section>

      <fieldset className="min-w-0">
        <legend className="mb-2 text-sm font-medium">Type</legend>
        <div className="grid grid-cols-2 gap-1 rounded-xl border border-foreground/15 p-1 sm:grid-cols-4">
          {KINDS.map((option) => (
            <label
              key={option.value}
              className={clsx(
                "flex h-10 cursor-pointer items-center justify-center rounded-lg px-2",
                "text-sm font-medium whitespace-nowrap",
                "transition-colors motion-reduce:transition-none",
                "hover:bg-foreground/5 has-checked:bg-foreground has-checked:text-background",
                "has-focus-visible:outline-2 has-focus-visible:outline-offset-2 has-focus-visible:outline-foreground",
              )}
            >
              <input
                type="radio"
                name="kind"
                value={option.value}
                checked={kind === option.value}
                onChange={() => {
                  setKind(option.value);
                  generate(option.value);
                }}
                className="sr-only"
              />
              {option.label}
            </label>
          ))}
        </div>
        <p className="mt-2 text-sm text-foreground/70">
          {KINDS.find((option) => option.value === kind)?.hint}
        </p>
      </fieldset>

      <div>
        <div className="flex items-center justify-between gap-4">
          <label htmlFor="length" className="text-sm font-medium">
            Length
          </label>
          <input
            type="number"
            aria-label="Length in characters"
            min={1}
            max={MAX_LENGTH}
            value={shownLength}
            disabled={isFernet}
            onChange={(event) => changeLength(Number(event.target.value))}
            className="h-9 w-20 rounded-lg border border-foreground/15 bg-background px-2 text-right font-mono text-sm focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-foreground disabled:opacity-40"
          />
        </div>
        <input
          id="length"
          type="range"
          min={1}
          max={MAX_LENGTH}
          value={shownLength}
          disabled={isFernet}
          onChange={(event) => changeLength(Number(event.target.value))}
          className="mt-3 w-full accent-foreground disabled:opacity-40"
        />
        {isFernet && (
          <p className="mt-2 text-sm text-foreground/70">
            A Fernet key is always {FERNET_LENGTH} characters.
          </p>
        )}
      </div>
    </div>
  );
}
