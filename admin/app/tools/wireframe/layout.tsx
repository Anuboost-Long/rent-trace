const css = `
.wireframe { padding: 12px; font-size: 14px; }
.wireframe input, .wireframe select, .wireframe textarea, .wireframe button {
  border: 1px solid #888; padding: 2px 6px; background: #fff; color: #000;
}
.wireframe textarea { display: block; width: 28rem; height: 4rem; }
.wireframe summary { cursor: pointer; font-weight: 600; margin-top: 12px; }
.wireframe pre { background: #f2f2f2; color: #000; padding: 8px; overflow: auto; max-height: 24rem; }
.wireframe details { border-bottom: 1px solid #ccc; padding-bottom: 8px; }
.wireframe a { text-decoration: underline; }
`;

export default function Layout({ children }: LayoutProps<"/tools/wireframe">) {
  return (
    <div className="wireframe">
      <style>{css}</style>
      {children}
    </div>
  );
}
