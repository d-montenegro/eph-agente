import { useState, type FormEvent } from "react";

import { api, ApiError, type AgentAnswer } from "../api/client";
import ResultTable, { formatValue } from "../components/ResultTable";
import SqlPanel from "../components/SqlPanel";

export default function AgentPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<AgentAnswer | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    try {
      setAnswer(await api.askAgent(trimmed));
    } catch (cause) {
      setAnswer(null);
      setError(cause instanceof ApiError ? cause.message : "No se pudo consultar al agente");
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
      </form>

      {error && (
        <p role="alert" className="error">
          {error}
        </p>
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
          </section>
        )}
      </div>
    </div>
  );
}
