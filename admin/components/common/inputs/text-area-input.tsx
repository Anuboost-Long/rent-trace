import clsx from "clsx";

import {
  ErrorClassName,
  InputInvalidClassName,
  LabelClassName,
} from "./config";

type TextAreaInputProp = Readonly<
  Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, "id"> & {
    name: string;
    label: string;
    error?: string;
  }
>;

export default function TextAreaInput({
  name,
  label,
  error,
  className,
  ...props
}: TextAreaInputProp) {
  return (
    <div className="flex w-full flex-col gap-1.5">
      <label htmlFor={name} className={LabelClassName}>
        {label}
      </label>
      <textarea
        rows={3}
        {...props}
        id={name}
        name={name}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? `${name}-error` : undefined}
        className={clsx(
          "w-full rounded-lg bg-background px-3 py-2 text-base",
          "border border-strong",
          error && InputInvalidClassName,
          "placeholder:text-fg-tertiary",
          "hover:border-fg-tertiary focus-visible:border-brand-border focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-brand-border/25",
          className,
        )}
      />
      {error && (
        <p id={`${name}-error`} className={ErrorClassName}>
          {error}
        </p>
      )}
    </div>
  );
}
