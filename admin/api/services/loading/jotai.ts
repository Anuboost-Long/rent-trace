import { atom } from "jotai";

type LoadingState = { visible: boolean; message: string };

export const LoadingAtom = atom<LoadingState>({ visible: false, message: "" });
