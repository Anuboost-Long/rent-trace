"use client";
import {
  addDays,
  addMonths,
  lastDayOfMonth,
  LONG_MONTHS,
  longDate,
  monthOf,
  monthWeeks,
  SHORT_MONTHS,
  todayIso,
  WEEKDAYS,
  withYearMonth,
  yearOf,
  YEARS_PER_PAGE,
  yearPageStart,
} from "@/utils/calendar";
import { formatDate } from "@/utils/format-date";
import clsx from "clsx";
import {
  CalendarDays,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
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

type View = "days" | "months" | "years";

const pickerCellClassName = clsx(
  "grid h-10 w-full place-items-center rounded-md text-sm tabular-nums",
  "focus-visible:outline-2 focus-visible:outline-foreground",
  "disabled:cursor-not-allowed disabled:opacity-30",
);

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
  const [view, setView] = useState<View>("days");

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
  }, [open, focused, view]);

  const isBeforeMin = (iso: string) => min !== undefined && iso < min;

  const openCalendar = () => {
    const start = value || todayIso();
    setFocused(isBeforeMin(start) && min ? min : start);
    moveFocusToDay.current = true;
    setView("days");
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

  const year = yearOf(focused);
  const yearStart = yearPageStart(year);

  const isMonthBeforeMin = (candidateYear: number, month: number) =>
    min !== undefined && lastDayOfMonth(candidateYear, month) < min;

  const isYearBeforeMin = (candidateYear: number) =>
    min !== undefined && lastDayOfMonth(candidateYear, 11) < min;

  const stepHeader = (direction: 1 | -1) => {
    if (view === "days") return setFocused(addMonths(focused, direction));
    const years = view === "months" ? 1 : YEARS_PER_PAGE;
    setFocused(addMonths(focused, direction * years * 12));
  };

  const pickMonth = (month: number) => {
    setFocused(withYearMonth(focused, year, month));
    moveFocusToDay.current = true;
    setView("days");
  };

  const pickYear = (candidateYear: number) => {
    setFocused(withYearMonth(focused, candidateYear, monthOf(focused)));
    moveFocusToDay.current = true;
    setView("days");
  };

  const backToDays = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key !== "Escape") return;
    event.preventDefault();
    moveFocusToDay.current = true;
    setView("days");
  };

  const onHeaderKeyDown = (event: React.KeyboardEvent<HTMLButtonElement>) => {
    if (event.key !== "Escape") return;
    event.preventDefault();
    if (view === "days") return close();
    backToDays(event);
  };

  const headerLabel = {
    days: "Previous month",
    months: "Previous year",
    years: "Previous years",
  }[view];

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
              aria-label={headerLabel}
              onClick={() => stepHeader(-1)}
              onKeyDown={onHeaderKeyDown}
              className={navButtonClassName}
            >
              <ChevronLeft aria-hidden className="size-4" />
            </button>
            <div className="flex items-center gap-1">
              {(
                [
                  ["months", LONG_MONTHS[monthOf(focused)]],
                  ["years", String(year)],
                ] as const
              ).map(([target, text]) => (
                <button
                  key={target}
                  type="button"
                  aria-pressed={view === target}
                  aria-label={`${text}, choose ${target === "months" ? "month" : "year"}`}
                  onClick={() => setView(view === target ? "days" : target)}
                  onKeyDown={onHeaderKeyDown}
                  className={clsx(
                    "flex h-9 items-center gap-1 rounded-md px-2 text-sm font-medium tabular-nums",
                    "focus-visible:outline-2 focus-visible:outline-foreground",
                    view === target
                      ? "bg-foreground/10"
                      : "hover:bg-foreground/10",
                  )}
                >
                  {text}
                  <ChevronDown aria-hidden className="size-3.5" />
                </button>
              ))}
            </div>
            <button
              type="button"
              aria-label={headerLabel.replace("Previous", "Next")}
              onClick={() => stepHeader(1)}
              onKeyDown={onHeaderKeyDown}
              className={navButtonClassName}
            >
              <ChevronRight aria-hidden className="size-4" />
            </button>
          </div>
          {view === "months" && (
            <div className="grid grid-cols-3 gap-1">
              {SHORT_MONTHS.map((short, month) => {
                const isShown = month === monthOf(focused);
                const isChosen =
                  value !== "" &&
                  yearOf(value) === year &&
                  monthOf(value) === month;
                return (
                  <button
                    key={short}
                    type="button"
                    disabled={isMonthBeforeMin(year, month)}
                    aria-pressed={isChosen}
                    onClick={() => pickMonth(month)}
                    onKeyDown={backToDays}
                    className={clsx(
                      pickerCellClassName,
                      isChosen
                        ? "bg-foreground font-semibold text-background"
                        : isShown
                          ? "bg-foreground/10"
                          : "hover:bg-foreground/10",
                    )}
                  >
                    {short}
                  </button>
                );
              })}
            </div>
          )}
          {view === "years" && (
            <div className="grid grid-cols-3 gap-1">
              {Array.from({ length: YEARS_PER_PAGE }, (_, offset) => {
                const candidate = yearStart + offset;
                const isChosen = value !== "" && yearOf(value) === candidate;
                return (
                  <button
                    key={candidate}
                    type="button"
                    disabled={isYearBeforeMin(candidate)}
                    aria-pressed={isChosen}
                    onClick={() => pickYear(candidate)}
                    onKeyDown={backToDays}
                    className={clsx(
                      pickerCellClassName,
                      isChosen
                        ? "bg-foreground font-semibold text-background"
                        : candidate === year
                          ? "bg-foreground/10"
                          : "hover:bg-foreground/10",
                    )}
                  >
                    {candidate}
                  </button>
                );
              })}
            </div>
          )}
          {view === "days" && (
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
          )}
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
