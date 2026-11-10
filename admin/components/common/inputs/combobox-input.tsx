"use client";
import clsx from "clsx";
import { Check, ChevronDown } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import {
  ErrorClassName,
  InputBoxClassName,
  InputClassName,
  InputInvalidClassName,
  LabelClassName,
} from "./config";

export type ComboboxOption = { value: string; label: string; hint?: string };

type ComboboxInputProp = Readonly<{
  name: string;
  label: string;
  value: string;
  onSelect: (option: ComboboxOption) => void;
  options?: ComboboxOption[];
  loadOptions?: (query: string) => Promise<ComboboxOption[]>;
  placeholder?: string;
  emptyMessage?: string;
  disabled?: boolean;
  error?: string;
  className?: string;
}>;

const SEARCH_DELAY_MS = 250;

export default function ComboboxInput({
  name,
  label,
  value,
  onSelect,
  options,
  loadOptions,
  placeholder,
  emptyMessage = "No matches",
  disabled,
  error,
  className,
}: ComboboxInputProp) {
  const id = useId();
  const listId = `${id}-list`;
  const rootRef = useRef<HTMLDivElement>(null);
  const latestSearch = useRef(0);
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loaded, setLoaded] = useState<ComboboxOption[]>([]);
  const [loading, setLoading] = useState(false);

  const selectedLabel =
    options?.find((option) => option.value === value)?.label ?? value;
  const needle = query.trim().toLowerCase();
  const visible = loadOptions
    ? loaded
    : (options ?? []).filter((option) =>
        option.label.toLowerCase().includes(needle),
      );

  useEffect(() => {
    if (!open || !loadOptions) return;
    const search = ++latestSearch.current;
    const timer = setTimeout(async () => {
      setLoading(true);
      const found = await loadOptions(query);
      if (search !== latestSearch.current) return;
      setLoaded(found);
      setActiveIndex(0);
      setLoading(false);
    }, SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [open, query, loadOptions]);

  useEffect(() => {
    if (!open) return;
    const closeOnOutsidePress = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setOpen(false);
        setQuery("");
      }
    };
    document.addEventListener("pointerdown", closeOnOutsidePress);
    return () =>
      document.removeEventListener("pointerdown", closeOnOutsidePress);
  }, [open]);

  const choose = (option: ComboboxOption) => {
    onSelect(option);
    setOpen(false);
    setQuery("");
  };

  const move = (index: number) => {
    const clamped = Math.min(visible.length - 1, Math.max(0, index));
    setActiveIndex(clamped);
    document
      .getElementById(`${id}-option-${clamped}`)
      ?.scrollIntoView({ block: "nearest" });
  };

  const onKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    switch (event.key) {
      case "ArrowDown":
      case "ArrowUp":
        event.preventDefault();
        if (!open) return setOpen(true);
        return move(activeIndex + (event.key === "ArrowDown" ? 1 : -1));
      case "Enter":
        if (!open) return;
        event.preventDefault();
        if (visible[activeIndex]) choose(visible[activeIndex]);
        return;
      case "Escape":
        setOpen(false);
        setQuery("");
        return;
      case "Tab":
        setOpen(false);
        setQuery("");
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
      <div
        className={clsx(
          InputBoxClassName,
          error && InputInvalidClassName,
          disabled && "opacity-60",
        )}
      >
        <input
          id={id}
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={
            open && visible.length > 0
              ? `${id}-option-${activeIndex}`
              : undefined
          }
          aria-invalid={error ? true : undefined}
          autoComplete="off"
          disabled={disabled}
          placeholder={open ? selectedLabel || placeholder : placeholder}
          value={open ? query : selectedLabel}
          onChange={(event) => {
            setQuery(event.target.value);
            setActiveIndex(0);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onClick={() => setOpen(true)}
          onKeyDown={onKeyDown}
          className={InputClassName}
        />
        <ChevronDown
          aria-hidden
          className={clsx("size-4 shrink-0", open && "rotate-180")}
        />
      </div>
      {open && (
        <ul
          id={listId}
          role="listbox"
          aria-label={label}
          className="absolute top-full z-20 mt-1 max-h-60 w-full overflow-auto rounded-lg border border-foreground/15 bg-background p-1"
        >
          {visible.map((option, index) => (
            <li
              key={`${option.value}-${option.hint ?? ""}`}
              id={`${id}-option-${index}`}
              role="option"
              aria-selected={option.value === value}
              onPointerEnter={() => setActiveIndex(index)}
              onPointerDown={(event) => event.preventDefault()}
              onClick={() => choose(option)}
              className={clsx(
                "flex h-10 cursor-pointer items-center justify-between gap-3 rounded-md px-3 text-sm",
                index === activeIndex && "bg-foreground/10",
                option.value === value && "font-semibold",
              )}
            >
              <span className="truncate">{option.label}</span>
              <span className="flex shrink-0 items-center gap-2 text-foreground/60">
                {option.hint}
                {option.value === value && (
                  <Check aria-hidden className="size-4" />
                )}
              </span>
            </li>
          ))}
          {(loading || visible.length === 0) && (
            <li
              role="presentation"
              className="px-3 py-2 text-sm text-foreground/60"
            >
              <span role="status">{loading ? "Searching…" : emptyMessage}</span>
            </li>
          )}
        </ul>
      )}
      {error && <p className={ErrorClassName}>{error}</p>}
    </div>
  );
}
