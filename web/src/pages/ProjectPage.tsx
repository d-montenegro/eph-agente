import { useEffect, useMemo, useRef, useState } from "react";

import { api } from "../api/client";
import { renderMarkdown } from "../lib/markdown";

type Mode = "editar" | "vista" | "presentacion";

const STORAGE_KEY = "eph-proyecto-draft";

export default function ProjectPage() {
  const [draft, setDraft] = useState(() => window.localStorage.getItem(STORAGE_KEY) ?? "");
  const [mode, setMode] = useState<Mode>("vista");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let active = true;
    api
      .getProject()
      .then(({ markdown }) => {
        if (!active) return;
        setDraft((previous) => previous || markdown);
        setLoading(false);
      })
      .catch((cause: unknown) => {
        if (!active) return;
        setError(cause instanceof Error ? cause.message : "No se pudo cargar el proyecto");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    if (draft) {
      window.localStorage.setItem(STORAGE_KEY, draft);
    }
  }, [draft]);

  const preview = useMemo(() => renderMarkdown(draft), [draft]);

  function exportDraft() {
    const blob = new Blob([draft], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "proyecto.md";
    link.click();
    URL.revokeObjectURL(url);
  }

  async function importDraft(file: File | undefined) {
    if (!file) return;
    setDraft(await file.text());
  }

  async function restore() {
    try {
      const { markdown } = await api.getProject();
      setDraft(markdown);
      window.localStorage.removeItem(STORAGE_KEY);
      setMode("vista");
      setError(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "No se pudo restaurar");
    }
  }

  if (mode === "presentacion") {
    return (
      <div className="presentation">
        <button type="button" className="exit-presentation" onClick={() => setMode("vista")}>
          Salir de la presentación
        </button>
        <article dangerouslySetInnerHTML={{ __html: preview }} />
      </div>
    );
  }

  return (
    <div className="page project-page">
      <header className="page-header">
        <h2>Proyecto</h2>
        <p>Explicación del trabajo, editable en el navegador y lista para presentar.</p>
      </header>

      {loading && <p className="muted">Cargando documento…</p>}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      <div className="toolbar" role="toolbar" aria-label="Acciones del proyecto">
        <button type="button" aria-pressed={mode === "editar"} onClick={() => setMode("editar")}>
          Editar
        </button>
        <button type="button" aria-pressed={mode === "vista"} onClick={() => setMode("vista")}>
          Vista previa
        </button>
        <button type="button" onClick={() => setMode("presentacion")}>
          Modo presentación
        </button>
        <span className="toolbar-separator" />
        <button type="button" onClick={exportDraft}>
          Exportar .md
        </button>
        <button type="button" onClick={() => fileRef.current?.click()}>
          Importar .md
        </button>
        <button type="button" onClick={restore}>
          Restaurar versión del repositorio
        </button>
        <input
          ref={fileRef}
          type="file"
          accept=".md,text/markdown"
          hidden
          onChange={(event) => importDraft(event.target.files?.[0])}
        />
      </div>

      <div className={mode === "editar" ? "editor-grid" : "editor-grid single"}>
        {mode === "editar" && (
          <label className="editor">
            <span>Borrador</span>
            <textarea
              aria-label="Borrador del proyecto"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
            />
          </label>
        )}
        <article
          className="preview"
          aria-label="Vista previa del proyecto"
          dangerouslySetInnerHTML={{ __html: preview }}
        />
      </div>
    </div>
  );
}
