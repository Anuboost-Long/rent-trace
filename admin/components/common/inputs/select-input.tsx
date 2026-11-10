"use client";
import clsx from "clsx";
import { Check, ChevronDown } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import { ErrorClassName, LabelClassName } from "./config";

type Option = { value: string; label: string };

type SelectInputProp = Readonly<{
  name: string;
  label: string;
  options: Option[];
  defaultValue?: string;
  value?: string;
  onValueChange?: (value: string) => void;
  error?: string;
  disabled?: boolean;
  className?: string;
}>;

export default function SelectInput({
  name,
  label,
  options,
  defaultValue,
  value: controlledValue,
  onValueChange,
  error,
  disabled,
  className,
}: SelectInputProp) {
  const id = useId();
  const listId = `${id}-list`;
  const rootRef = useRef<HTMLDivElement>(null);
  const [internalValue, setInternalValue] = useState(
    defaultValue ?? options[0]?.value ?? "",
  );
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);

  const value = controlledValue ?? internalValue;
  const selectedIndex = Math.max(
    0,
    options.findIndex((option) => option.value === value),
  );

  useEffect(() => {
    if (!open) return;
    const closeOnOutsidePress = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", closeOnOutsidePress);
    return () =>
      document.removeEventListener("pointerdown", closeOnOutsidePress);
  }, [open]);

  const openWindow = () => {
    setActiveIndex(selectedIndex);
    setOpen(true);
  };

  const choose = (index: number) => {
    const next = options[index].value;
    setInternalValue(next);
    onValueChange?.(next);
    setOpen(false);
  };

  const move = (index: number) => {
    const clamped = Math.min(options.length - 1, Math.max(0, index));
    setActiveIndex(clamped);
    document
      .getElementById(`${id}-option-${clamped}`)
      ?.scrollIntoView({ block: "nearest" });
  };

  const typeAhead = (character: string) => {
    const from = open ? activeIndex + 1 : selectedIndex + 1;
    const ordered = [...options.keys()].map(
      (_, step) => (from + step) % options.length,
    );
    const match = ordered.find((index) =>
      options[index].label.toLowerCase().startsWith(character.toLowerCase()),
    );
    if (match === undefined) return;
    if (open) move(match);
    else choose(match);
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    switch (event.key) {
      case "ArrowDown":
      case "ArrowUp":
        event.preventDefault();
        if (!open) return openWindow();
        return move(activeIndex + (event.key === "ArrowDown" ? 1 : -1));
      case "Home":
      case "End":
        if (!open) return;
        event.preventDefault();
        return move(event.key === "Home" ? 0 : options.length - 1);
      case "Enter":
      case " ":
        event.preventDefault();
        return open ? choose(activeIndex) : openWindow();
      case "Escape":
        return setOpen(false);
      case "Tab":
        return setOpen(false);
      default:
        if (event.key.length === 1 && !event.metaKey && !event.ctrlKey) {
          typeAhead(event.key);
        }
    }
  };

  return (
    <div
      ref={rootRef}
      className={clsx("relative flex w-full flex-col gap-1.5", className)}
    >
      <label htmlFor={id} className={LabelClassName}>
        {label}
      </label>
      <input type="hidden" name={name} value={value} />
      <button
        id={id}
        type="button"
        role="combobox"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        aria-activedescendant={open ? `${id}-option-${activeIndex}` : undefined}
        aria-invalid={error ? true : undefined}
        disabled={disabled}
        onClick={() => (open ? setOpen(false) : openWindow())}
        onKeyDown={onKeyDown}
        className={clsx(
          "flex h-11 w-full items-center justify-between gap-2 rounded-lg bg-background",
          error ? "border border-red-600" : "border border-foreground/15",
          "px-3 text-left text-base",
          "focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-foreground disabled:opacity-60",
        )}
      >
        <span className="truncate">{options[selectedIndex]?.label}</span>
        <ChevronDown
          aria-hidden
          className={clsx("size-4 shrink-0", open && "rotate-180")}
        />
      </button>
      {open && (
        <ul
          id={listId}
          role="listbox"
          aria-label={label}
          className="absolute top-full z-20 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-foreground/15 bg-background p-1"
        >
          {options.map((option, index) => (
            <li
              key={option.value}
              id={`${id}-option-${index}`}
              role="option"
              aria-selected={option.value === value}
              onPointerEnter={() => setActiveIndex(index)}
              onClick={() => choose(index)}
              className={clsx(
                "flex h-10 cursor-pointer items-center justify-between rounded-md px-3 text-sm",
                index === activeIndex && "bg-foreground/10",
                option.value === value && "font-semibold",
              )}
            >
              {option.label}
              {option.value === value && (
                <Check aria-hidden className="size-4" />
              )}
            </li>
          ))}
        </ul>
      )}
      {error && <p className={ErrorClassName}>{error}</p>}
    </div>
  );
}
