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
          "border border-foreground/15",
          error && InputInvalidClassName,
          "placeholder:text-foreground/40",
          "focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-foreground",
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
