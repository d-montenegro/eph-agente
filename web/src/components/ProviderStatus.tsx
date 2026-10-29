import type { ProviderHealth } from "../api/client";

const LABELS: Record<string, string> = {
  ok: "Conectado",
  unreachable: "Servidor inaccesible",
  invalid_credentials: "Credencial inválida",
  model_not_found: "Modelo inexistente",
  error: "Error del proveedor",
};

export default function ProviderStatus({ health }: { health: ProviderHealth }) {
  return (
    <div className={`status status-${health.status}`} role="status">
      <strong>{LABELS[health.status] ?? health.status}</strong>
      <span>{health.latency_ms.toFixed(0)} ms</span>
      {health.models.length > 0 && <span>{health.models.length} modelos</span>}
      {health.tools_supported !== null && (
        <span>{health.tools_supported ? "Tool calling OK" : "Sin tool calling"}</span>
      )}
      {health.detail && <p className="muted">{health.detail}</p>}
    </div>
  );
}
