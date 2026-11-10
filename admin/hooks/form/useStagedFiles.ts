"use client";
import type { PropertyFileKind } from "@/types/properties/models";
import {
  kindOfFile,
  NOT_SUPPORTED,
  problemWithFile,
} from "@/utils/property-files";
import { useEffect, useRef, useState } from "react";

export type PendingFile = {
  id: string;
  file: File;
  kind: PropertyFileKind;
  previewUrl: string | null;
};

const release = (item: PendingFile) => {
  if (item.previewUrl) URL.revokeObjectURL(item.previewUrl);
};

const useStagedFiles = () => {
  const [items, setItems] = useState<PendingFile[]>([]);
  const [rejected, setRejected] = useState<string[]>([]);
  const latest = useRef(items);

  useEffect(() => {
    latest.current = items;
  }, [items]);

  useEffect(
    () => () => {
      latest.current.forEach(release);
    },
    [],
  );

  const add = (files: File[]) => {
    const accepted: PendingFile[] = [];
    const problems: string[] = [];
    for (const file of files) {
      const kind = kindOfFile(file);
      const problem = kind ? problemWithFile(file, kind) : NOT_SUPPORTED;
      if (!kind || problem) {
        problems.push(`${file.name}: ${problem}`);
        continue;
      }
      accepted.push({
        id: crypto.randomUUID(),
        file,
        kind,
        previewUrl: kind === "PHOTO" ? URL.createObjectURL(file) : null,
      });
    }
    setRejected(problems);
    setItems((current) => [...current, ...accepted]);
  };

  const keepOnly = (ids: string[]) => {
    latest.current.filter((item) => !ids.includes(item.id)).forEach(release);
    setItems((current) => current.filter((item) => ids.includes(item.id)));
  };

  return {
    items,
    rejected,
    add,
    remove: (id: string) =>
      keepOnly(
        latest.current.map((item) => item.id).filter((other) => other !== id),
      ),
    keepOnly,
    clear: () => {
      keepOnly([]);
      setRejected([]);
    },
  };
};

export default useStagedFiles;
export type StagedFiles = ReturnType<typeof useStagedFiles>;
