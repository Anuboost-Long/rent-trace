import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "RentTrace",
    short_name: "RentTrace",
    description: "Rent records for tenants and landlords",
    start_url: "/",
    display: "standalone",
    background_color: "#F3F7FC",
    theme_color: "#0B4298",
    icons: [
      { src: "/pwa-192.png", sizes: "192x192", type: "image/png" },
      { src: "/pwa-512.png", sizes: "512x512", type: "image/png" },
    ],
  };
}
