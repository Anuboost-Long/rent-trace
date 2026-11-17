const RIPPLE_MS = 500;
const RIPPLE_PEAK_OPACITY = 0.25;

export const spawnRipple = (event: React.PointerEvent<HTMLElement>) => {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const target = event.currentTarget;
  const box = target.getBoundingClientRect();
  const size = Math.max(box.width, box.height) * 2;
  const ripple = document.createElement("span");
  Object.assign(ripple.style, {
    position: "absolute",
    pointerEvents: "none",
    borderRadius: "50%",
    backgroundColor: "currentColor",
    opacity: "0",
    width: `${size}px`,
    height: `${size}px`,
    left: `${event.clientX - box.left - size / 2}px`,
    top: `${event.clientY - box.top - size / 2}px`,
  });
  target.append(ripple);
  const animation = ripple.animate(
    [
      { opacity: RIPPLE_PEAK_OPACITY, transform: "scale(0)" },
      { opacity: 0, transform: "scale(1)" },
    ],
    { duration: RIPPLE_MS, easing: "ease-out" },
  );
  animation.onfinish = () => ripple.remove();
  animation.oncancel = () => ripple.remove();
};
