"use client";
import clsx from "clsx";
import { Eye, EyeOff } from "lucide-react";
import { useState } from "react";

import {
  ErrorClassName,
  InputBoxClassName,
  InputClassName,
  InputInvalidClassName,
  LabelClassName,
} from "./config";

type TextInputProp = Readonly<
  Omit<React.InputHTMLAttributes<HTMLInputElement>, "id"> & {
    name: string;
    label?: string;
    error?: string;
    rightSlot?: React.ReactNode;
    className?: string;
  }
>;

export default function TextInput({
  name,
  label,
  error,
  rightSlot,
  className,
  type = "text",
  required,
  ...props
}: TextInputProp) {
  const [revealed, setRevealed] = useState(false);
  const isPassword = type === "password";

  return (
    <div className={clsx("flex w-full flex-col gap-1.5", className)}>
      {label && (
        <label htmlFor={name} className={LabelClassName}>
          {label}
        </label>
      )}
      <div className={clsx(InputBoxClassName, error && InputInvalidClassName)}>
        <input
          {...props}
          id={name}
          name={name}
          required={required}
          type={isPassword && revealed ? "text" : type}
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? `${name}-error` : undefined}
          className={InputClassName}
        />
        {isPassword ? (
          <button
            type="button"
            onClick={() => setRevealed((value) => !value)}
            aria-label={revealed ? "Hide password" : "Show password"}
            aria-pressed={revealed}
            className="text-foreground/70 hover:text-foreground"
          >
            {revealed ? (
              <EyeOff aria-hidden className="size-4" />
            ) : (
              <Eye aria-hidden className="size-4" />
            )}
          </button>
        ) : (
          rightSlot
        )}
      </div>
      {error && (
        <p id={`${name}-error`} className={ErrorClassName}>
          {error}
        </p>
      )}
    </div>
  );
}
