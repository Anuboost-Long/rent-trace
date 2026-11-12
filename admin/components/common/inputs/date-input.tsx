"use client";
import {
  addDays,
  addMonths,
  longDate,
  monthLabel,
  monthWeeks,
  todayIso,
  WEEKDAYS,
} from "@/utils/calendar";
import { formatDate } from "@/utils/format-date";
import clsx from "clsx";
import { CalendarDays, ChevronLeft, ChevronRight } from "lucide-react";
import { useEffect, useId, useRef, useState } from "react";

import {
  ErrorClassName,
  InputBoxClassName,
  InputInvalidClassName,
  LabelClassName,
} from "./config";

type DateInputProp = Readonly<{
  name: string;
  label: string;
  defaultValue?: string;
  min?: string;
  required?: boolean;
  disabled?: boolean;
  error?: string;
  className?: string;
  onValueChange?: (value: string) => void;
}>;

const KEY_STEPS: Record<string, number> = {
  ArrowLeft: -1,
  ArrowRight: 1,
  ArrowUp: -7,
  ArrowDown: 7,
};

const navButtonClassName = clsx(
  "grid size-9 place-items-center rounded-md",
  "hover:bg-foreground/10 focus-visible:outline-2 focus-visible:outline-foreground",
);

export default function DateInput({
  name,
  label,
  defaultValue = "",
  min,
  required,
  disabled,
  error,
  className,
  onValueChange,
}: DateInputProp) {
  const id = useId();
  const rootRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const focusedDayRef = useRef<HTMLButtonElement>(null);
  const moveFocusToDay = useRef(false);
  const [value, setValue] = useState(defaultValue);
  const [open, setOpen] = useState(false);
  const [focused, setFocused] = useState(defaultValue);

  useEffect(() => {
    if (!open) return;
    const closeOnOutsidePress = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    document.addEventListener("pointerdown", closeOnOutsidePress);
    return () =>
      document.removeEventListener("pointerdown", closeOnOutsidePress);
  }, [open]);

  useEffect(() => {
    if (!open || !moveFocusToDay.current) return;
    moveFocusToDay.current = false;
    focusedDayRef.current?.focus();
  }, [open, focused]);

  const isBeforeMin = (iso: string) => min !== undefined && iso < min;

  const openCalendar = () => {
    const start = value || todayIso();
    setFocused(isBeforeMin(start) && min ? min : start);
    moveFocusToDay.current = true;
    setOpen(true);
  };

  const close = () => {
    setOpen(false);
    triggerRef.current?.focus();
  };

  const choose = (iso: string) => {
    if (isBeforeMin(iso)) return;
    setValue(iso);
    onValueChange?.(iso);
    close();
  };

  const clear = () => {
    setValue("");
    onValueChange?.("");
    close();
  };

  const moveFocus = (iso: string) => {
    moveFocusToDay.current = true;
    setFocused(iso);
  };

  const onDayKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    const step = KEY_STEPS[event.key];
    if (step !== undefined) {
      event.preventDefault();
      return moveFocus(addDays(focused, step));
    }
    switch (event.key) {
      case "PageUp":
      case "PageDown":
        event.preventDefault();
        return moveFocus(addMonths(focused, event.key === "PageUp" ? -1 : 1));
      case "Escape":
        event.preventDefault();
        return close();
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
        ref={triggerRef}
        id={id}
        type="button"
        disabled={disabled}
        aria-expanded={open}
        aria-controls={`${id}-calendar`}
        aria-describedby={error ? `${id}-error` : undefined}
        onClick={() => (open ? setOpen(false) : openCalendar())}
        className={clsx(
          InputBoxClassName,
          "justify-between text-left text-base",
          error && InputInvalidClassName,
          disabled && "opacity-60",
        )}
      >
        <span className={clsx(!value && "text-foreground/40")}>
          {value ? formatDate(value) : "Choose a date"}
        </span>
        <CalendarDays aria-hidden className="size-4 shrink-0" />
      </button>
      {open && (
        <div
          id={`${id}-calendar`}
          className="absolute top-full z-20 mt-1 w-72 rounded-lg border border-foreground/15 bg-background p-3"
        >
          <div className="mb-2 flex items-center justify-between">
            <button
              type="button"
              aria-label="Previous month"
              onClick={() => setFocused(addMonths(focused, -1))}
              className={navButtonClassName}
            >
              <ChevronLeft aria-hidden className="size-4" />
            </button>
            <p aria-live="polite" className="text-sm font-medium">
              {monthLabel(focused)}
            </p>
            <button
              type="button"
              aria-label="Next month"
              onClick={() => setFocused(addMonths(focused, 1))}
              className={navButtonClassName}
            >
              <ChevronRight aria-hidden className="size-4" />
            </button>
          </div>
          <table className="w-full table-fixed text-center text-sm">
            <thead>
              <tr>
                {WEEKDAYS.map((weekday) => (
                  <th
                    key={weekday.short}
                    scope="col"
                    className="pb-1 text-xs font-normal text-foreground/60"
                  >
                    <abbr title={weekday.long} className="no-underline">
                      {weekday.short}
                    </abbr>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {monthWeeks(focused).map((week) => (
                <tr key={week[0].iso}>
                  {week.map((cell) => (
                    <td key={cell.iso} className="p-0">
                      <button
                        ref={cell.iso === focused ? focusedDayRef : undefined}
                        type="button"
                        tabIndex={cell.iso === focused ? 0 : -1}
                        disabled={isBeforeMin(cell.iso)}
                        aria-label={longDate(cell.iso)}
                        aria-pressed={cell.iso === value}
                        onClick={() => choose(cell.iso)}
                        onKeyDown={onDayKeyDown}
                        className={clsx(
                          "grid size-9 w-full place-items-center rounded-md tabular-nums",
                          "focus-visible:outline-2 focus-visible:outline-foreground",
                          "disabled:cursor-not-allowed disabled:opacity-30",
                          cell.iso === value
                            ? "bg-foreground font-semibold text-background"
                            : "hover:bg-foreground/10",
                          !cell.inMonth &&
                            cell.iso !== value &&
                            "text-foreground/40",
                        )}
                      >
                        {cell.day}
                      </button>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-2 flex justify-between text-sm">
            <button
              type="button"
              onClick={() => choose(todayIso())}
              disabled={isBeforeMin(todayIso())}
              className="rounded-md px-2 py-1 hover:bg-foreground/10 disabled:opacity-30"
            >
              Today
            </button>
            {!required && value && (
              <button
                type="button"
                onClick={clear}
                className="rounded-md px-2 py-1 hover:bg-foreground/10"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      )}
      {error && (
        <p id={`${id}-error`} className={ErrorClassName}>
          {error}
        </p>
      )}
    </div>
  );
}
