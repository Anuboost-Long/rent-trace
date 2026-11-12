import { handleGetViewer } from "@/api/services/auth/serve-action";
import { cache } from "react";

export const getViewer = cache(handleGetViewer);
