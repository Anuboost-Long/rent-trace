"use client";
import clsx from "clsx";
import { useRef, useState } from "react";

import { ErrorClassName } from "./config";

type OtpInputProp = Readonly<{
  name: string;
  label: string;
  length?: number;
  error?: string;
  autoFocus?: boolean;
}>;

// One box per digit; the joined code is submitted in a single hidden field called `name`.
export default function OtpInput({
  name,
  label,
  length = 6,
  error,
  autoFocus,
}: OtpInputProp) {
  const [digits, setDigits] = useState<string[]>(() => Array(length).fill(""));
  const boxes = useRef<(HTMLInputElement | null)[]>([]);

  const fillFrom = (start: number, text: string) => {
    const incoming = text
      .replace(/\D/g, "")
      .slice(0, length - start)
      .split("");
    if (incoming.length === 0) return;
    setDigits((current) => {
      const next = [...current];
      incoming.forEach((digit, offset) => (next[start + offset] = digit));
      return next;
    });
    boxes.current[Math.min(start + incoming.length, length - 1)]?.focus();
  };

  const onKeyDown = (
    index: number,
    event: React.KeyboardEvent<HTMLInputElement>,
  ) => {
    if (event.key === "Backspace" && digits[index] === "" && index > 0) {
      boxes.current[index - 1]?.focus();
    }
    if (event.key === "ArrowLeft") boxes.current[index - 1]?.focus();
    if (event.key === "ArrowRight") boxes.current[index + 1]?.focus();
  };

  return (
    <fieldset aria-describedby={error ? `${name}-error` : undefined}>
      <legend className="sr-only">{label}</legend>
      <input type="hidden" name={name} value={digits.join("")} />
      <div className="flex gap-2">
        {digits.map((digit, index) => (
          <input
            key={index}
            ref={(element) => {
              boxes.current[index] = element;
            }}
            value={digit}
            inputMode="numeric"
            autoComplete={index === 0 ? "one-time-code" : "off"}
            autoFocus={autoFocus && index === 0}
            maxLength={index === 0 ? length : 1}
            aria-label={`Digit ${index + 1} of ${length}`}
            aria-invalid={error ? true : undefined}
            onChange={(event) => {
              const value = event.target.value;
              if (value === "") {
                setDigits((current) =>
                  current.map((d, i) => (i === index ? "" : d)),
                );
                return;
              }
              fillFrom(index, value);
            }}
            onPaste={(event) => {
              event.preventDefault();
              fillFrom(index, event.clipboardData.getData("text"));
            }}
            onKeyDown={(event) => onKeyDown(index, event)}
            className={clsx(
              "size-12 rounded-lg border bg-background text-center text-heading tabular-nums",
              "focus-visible:border-brand-border focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-brand-border/25",
              error ? "border-error-accent" : "border-strong",
            )}
          />
        ))}
      </div>
      {error && (
        <p id={`${name}-error`} className={clsx("mt-2", ErrorClassName)}>
          {error}
        </p>
      )}
    </fieldset>
  );
}
