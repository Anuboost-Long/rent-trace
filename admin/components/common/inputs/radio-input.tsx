type RadioInputProp = Readonly<
  Omit<React.InputHTMLAttributes<HTMLInputElement>, "type"> & {
    label: string;
  }
>;

export default function RadioInput({ label, ...props }: RadioInputProp) {
  return (
    <label className="flex items-center gap-2">
      <input {...props} type="radio" className="size-4 accent-brand" />
      {label}
    </label>
  );
}
