import type { Me } from "@/types/auth/models";
import { atom } from "jotai";

export const UserAtom = atom<Me | null>(null);
