"use client";
import clsx from "clsx";
import { useEffect, useState } from "react";

const lastIndexByGroup = new Map<string, number>();

type TabContentProp = Readonly<{
  group: string;
  activeIndex: number;
  children: React.ReactNode;
}>;

export default function TabContent({
  group,
  activeIndex,
  children,
}: TabContentProp) {
  const [previous] = useState(() => lastIndexByGroup.get(group));

  useEffect(() => {
    lastIndexByGroup.set(group, activeIndex);
  }, [group, activeIndex]);

  return (
    <div
      className={clsx(
        "overflow-x-clip motion-reduce:animate-none",
        previous === undefined && "animate-panel-in",
        previous !== undefined &&
          (activeIndex >= previous ? "slide-from-right" : "slide-from-left"),
      )}
    >
      {children}
    </div>
  );
}
