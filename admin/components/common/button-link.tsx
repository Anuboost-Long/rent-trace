"use client";
import { spawnRipple } from "@/utils/ripple";
import clsx from "clsx";
import Link from "next/link";

import {
  buttonClassName,
  type ButtonSize,
  type ButtonVariant,
} from "./button-class-name";

type ButtonLinkProp = Readonly<
  React.ComponentProps<typeof Link> & {
    variant?: ButtonVariant;
    size?: ButtonSize;
  }
>;

export default function ButtonLink({
  variant,
  size,
  className,
  onPointerDown,
  ...props
}: ButtonLinkProp) {
  return (
    <Link
      {...props}
      onPointerDown={(event) => {
        spawnRipple(event);
        onPointerDown?.(event);
      }}
      className={clsx(buttonClassName(variant, size), className)}
    />
  );
}
