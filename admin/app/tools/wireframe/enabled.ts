import { notFound } from "next/navigation";
import { connection } from "next/server";

export const requireWireframe = async () => {
  await connection();
  const enabled =
    process.env.NODE_ENV !== "production" ||
    process.env.WIREFRAME_ENABLED === "true";
  if (!enabled) notFound();
};
