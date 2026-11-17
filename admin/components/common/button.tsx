"use client";
import { spawnRipple } from "@/utils/ripple";
import clsx from "clsx";

import {
  buttonClassName,
  type ButtonSize,
  type ButtonVariant,
} from "./button-class-name";

type ButtonProp = Readonly<
  React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: ButtonVariant;
    size?: ButtonSize;
    pending?: boolean;
  }
>;

export default function Button({
  variant,
  size,
  pending,
  className,
  disabled,
  children,
  onPointerDown,
  ...props
}: ButtonProp) {
  return (
    <button
      {...props}
      onPointerDown={(event) => {
        spawnRipple(event);
        onPointerDown?.(event);
      }}
      disabled={disabled || pending}
      className={clsx(buttonClassName(variant, size), className)}
    >
      {children}
    </button>
  );
}
