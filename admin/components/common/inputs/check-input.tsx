type CheckInputProp = Readonly<
  Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> & { label: string }
>;

export default function CheckInput({ label, ...props }: CheckInputProp) {
  return (
    <label className="flex items-center gap-2">
      <input {...props} type="checkbox" className="size-4 accent-brand" />
      {label}
    </label>
  );
}
