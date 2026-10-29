import { useEffect, useState } from "react";

export default function SqlPanel({ sql }: { sql: string | null }) {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!copied) return;
    const timer = window.setTimeout(() => setCopied(false), 1500);
    return () => window.clearTimeout(timer);
  }, [copied]);

  async function copy() {
    if (!sql) return;
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <section className="sql-panel" aria-label="SQL ejecutado">
      <header>
        <h3>SQL ejecutado</h3>
        {sql && (
          <button type="button" onClick={copy}>
            {copied ? "Copiado" : "Copiar"}
          </button>
        )}
      </header>
      {sql ? (
        <pre>
          <code>{sql}</code>
        </pre>
      ) : (
        <p className="muted">No se ejecutó SQL.</p>
      )}
    </section>
  );
}
