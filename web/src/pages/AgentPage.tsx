import { useState, type FormEvent } from "react";

import { api, ApiError, type AgentAnswer } from "../api/client";
import ResultTable, { formatValue } from "../components/ResultTable";
import SqlPanel from "../components/SqlPanel";

const HISTORY_KEY = "eph-agent-history-v1";
const HISTORY_LIMIT = 20;

type HistoryEntry = {
  id: string;
  question: string;
  createdAt: string;
  answer: AgentAnswer;
};

function loadHistory(): HistoryEntry[] {
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY) ?? "[]").slice(0, HISTORY_LIMIT);
  } catch {
    return [];
  }
}

function saveHistory(entries: HistoryEntry[]) {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(entries.slice(0, HISTORY_LIMIT)));
}

export default function AgentPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AgentAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [debug, setDebug] = useState(false);
  const [errorTrace, setErrorTrace] = useState<Array<Record<string, unknown>> | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>(loadHistory);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    setErrorTrace(null);
    try {
      const nextAnswer = await api.askAgent(trimmed, debug);
      setAnswer(nextAnswer);
      const nextHistory = [
        {
          id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
          question: trimmed,
          createdAt: new Date().toISOString(),
          answer: nextAnswer,
        },
        ...history,
      ].slice(0, HISTORY_LIMIT);
      setHistory(nextHistory);
      saveHistory(nextHistory);
    } catch (cause) {
      setAnswer(null);
      if (cause instanceof ApiError) {
        setError(cause.message);
        setErrorTrace(cause.trace);
      } else {
        setError("No se pudo consultar al agente");
        setErrorTrace(null);
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page agent-page">
      <header className="page-header">
        <h2>Agente EPH</h2>
        <p>Preguntá sobre el mercado laboral y los ingresos del 1T 2026.</p>
      </header>

      <form className="ask-form" onSubmit={submit}>
        <label htmlFor="question">Pregunta</label>
        <textarea
          id="question"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="¿Cuál fue la tasa de desocupación de las mujeres en Gran Córdoba en el 1T 2026?"
          rows={3}
        />
        <button type="submit" disabled={loading || !question.trim()}>
          {loading ? "Consultando…" : "Consultar"}
        </button>
        <label className="checkbox">
          <input
            type="checkbox"
            checked={debug}
            onChange={(event) => setDebug(event.target.checked)}
          />
          Modo debugging (ver traza del loop y las herramientas)
        </label>
      </form>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {errorTrace && (
        <details className="trace" open>
          <summary>
            Traza del error · {errorTrace.length} turno
            {errorTrace.length === 1 ? "" : "s"}
          </summary>
          <pre>{JSON.stringify(errorTrace, null, 2)}</pre>
        </details>
      )}

      <div aria-live="polite">
        {answer && (
          <section className="answer" aria-label="Respuesta">
            <h3>Respuesta</h3>
            <p className="answer-text">{answer.answer}</p>

            {answer.result.kind === "scalar" ? (
              <p className="scalar" data-testid="scalar">
                {formatValue(answer.result.value)}
              </p>
            ) : (
              <ResultTable
                columns={answer.result.columns}
                rows={answer.result.rows}
                caption="Tabla resultante"
              />
            )}

            <section aria-label="Supuestos">
              <h3>Supuestos</h3>
              {answer.assumptions.length ? (
                <ul>
                  {answer.assumptions.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No se declararon supuestos adicionales.</p>
              )}
            </section>

            {answer.warnings.length > 0 && (
              <section className="warnings" aria-label="Advertencias">
                <h3>Advertencias</h3>
                <ul>
                  {answer.warnings.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </section>
            )}

            <p className="meta">
              Perfil <strong>{answer.profile}</strong> · Modelo{" "}
              <strong>{answer.model}</strong> · Filas <strong>{answer.sample_size}</strong>
            </p>

            <SqlPanel sql={answer.sql} />

            {debug && answer.trace && (
              <details className="trace">
                <summary>
                  Traza de depuración · {answer.trace.length} turno
                  {answer.trace.length === 1 ? "" : "s"}
                </summary>
                <pre>{JSON.stringify(answer.trace, null, 2)}</pre>
              </details>
            )}
          </section>
        )}
      </div>

      <section className="history" aria-label="Historial de consultas">
        <div className="history-header">
          <div>
            <h3>Historial</h3>
            <p>Últimas {HISTORY_LIMIT} respuestas guardadas solo en este navegador.</p>
          </div>
          {history.length > 0 && (
            <button
              type="button"
              onClick={() => {
                setHistory([]);
                localStorage.removeItem(HISTORY_KEY);
              }}
            >
              Borrar historial
            </button>
          )}
        </div>
        {history.length === 0 ? (
          <p className="muted">Todavía no hay consultas guardadas.</p>
        ) : (
          <ol className="history-list">
            {history.map((entry) => (
              <li key={entry.id}>
                <button
                  type="button"
                  onClick={() => {
                    setQuestion(entry.question);
                    setAnswer(entry.answer);
                    setError(null);
                    setErrorTrace(null);
                  }}
                >
                  <span>{entry.question}</span>
                  <time dateTime={entry.createdAt}>
                    {new Date(entry.createdAt).toLocaleString("es-AR")}
                  </time>
                </button>
              </li>
            ))}
          </ol>
        )}
      </section>
    </div>
  );
}
