import Image from "next/image";

const LOGOS = {
  "wordmark-light": { src: "/brand/logo-light.svg", width: 2024, height: 538 },
  "wordmark-white": { src: "/brand/logo-white.svg", width: 2024, height: 538 },
  "emblem-blue": { src: "/brand/emblem-blue.svg", width: 1024, height: 1024 },
  "emblem-white": { src: "/brand/emblem-white.svg", width: 1024, height: 1024 },
} as const;

type BrandLogoProp =
  | Readonly<{
      variant: "wordmark";
      tone: "light" | "white";
      alt: string;
      className?: string;
    }>
  | Readonly<{
      variant: "emblem";
      tone: "blue" | "white";
      alt: string;
      className?: string;
    }>;

export default function BrandLogo({
  variant,
  tone,
  alt,
  className,
}: BrandLogoProp) {
  const key = `${variant}-${tone}` as keyof typeof LOGOS;
  return <Image {...LOGOS[key]} alt={alt} unoptimized className={className} />;
}
