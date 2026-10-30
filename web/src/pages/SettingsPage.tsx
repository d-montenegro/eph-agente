import { useEffect, useState, type FormEvent } from "react";

import {
  api,
  ApiError,
  type ProviderHealth,
  type ProvidersResponse,
} from "../api/client";
import ProviderStatus from "../components/ProviderStatus";

export default function SettingsPage() {
  const [data, setData] = useState<ProvidersResponse | null>(null);
  const [health, setHealth] = useState<Record<string, ProviderHealth>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [form, setForm] = useState({
    name: "",
    base_url: "http://host.docker.internal:11434/v1",
    model: "qwen2.5:7b",
    api_key: "",
    api_key_env: "",
    timeout_seconds: "60",
  });

  useEffect(() => {
    let active = true;
    api
      .getProviders()
      .then((payload) => {
        if (!active) return;
        setData(payload);
        setLoading(false);
      })
      .catch((cause: unknown) => {
        if (!active) return;
        setError(cause instanceof Error ? cause.message : "No se pudieron cargar los perfiles");
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  async function select(name: string) {
    setBusy(`select:${name}`);
    setError(null);
    try {
      const profile = await api.selectProvider(name);
      setData((previous) => (previous ? { ...previous, selected: profile.name } : previous));
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo seleccionar el perfil");
    } finally {
      setBusy(null);
    }
  }

  async function test(name: string) {
    setBusy(`test:${name}`);
    setError(null);
    try {
      const result = await api.testProvider(name, true);
      setHealth((previous) => ({ ...previous, [name]: result }));
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo probar el perfil");
    } finally {
      setBusy(null);
    }
  }

  async function addProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setCreating(true);
    setError(null);
    setMessage(null);
    try {
      const profile = await api.addCustomProvider({
        name: form.name.trim(),
        base_url: form.base_url.trim(),
        model: form.model.trim(),
        api_key: form.api_key || undefined,
        api_key_env: form.api_key_env || undefined,
        timeout_seconds: Number(form.timeout_seconds) || 60,
      });
      setData(await api.getProviders());
      setMessage(
        `Perfil "${profile.name}" agregado. Probá la conexión y después seleccionalo.`,
      );
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo agregar el perfil");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="page settings-page">
      <header className="page-header">
        <h2>Configuración</h2>
        <p>Perfiles de modelos compatibles con OpenAI. Las claves quedan en el servidor.</p>
      </header>

      {loading && <p className="muted">Cargando perfiles…</p>}
      {error && (
        <p role="alert" className="error">
          {error}
        </p>
      )}

      {data && (
        <>
          <p className={`mode-banner mode-${data.mode}`}>
            Modo <strong>{data.mode}</strong>
            {data.mode === "hosted"
              ? ": solo se permiten destinos de la lista blanca."
              : ": se pueden probar URLs locales o remotas."}
          </p>

          {data.mode === "local" && (
            <section className="custom-provider">
              <h3>Agregar perfil de modelo</h3>
              <p className="muted">
                Para Ollama en tu máquina con Docker usá{" "}
                <code>http://host.docker.internal:11434/v1</code>. Si pegás una clave,
                queda solo en memoria del servidor y no se muestra.
              </p>
              <form className="field-grid" onSubmit={addProfile}>
                <label>
                  Nombre
                  <input
                    value={form.name}
                    onChange={(event) => setForm({ ...form, name: event.target.value })}
                    placeholder="mi-modelo"
                    pattern="[a-z0-9_-]+"
                    required
                  />
                </label>
                <label>
                  URL base
                  <input
                    value={form.base_url}
                    onChange={(event) => setForm({ ...form, base_url: event.target.value })}
                    required
                  />
                </label>
                <label>
                  Modelo
                  <input
                    value={form.model}
                    onChange={(event) => setForm({ ...form, model: event.target.value })}
                    required
                  />
                </label>
                <label>
                  Clave (opcional)
                  <input
                    type="password"
                    value={form.api_key}
                    onChange={(event) => setForm({ ...form, api_key: event.target.value })}
                    placeholder="se guarda solo en memoria"
                  />
                </label>
                <label>
                  Variable de entorno (opcional)
                  <input
                    value={form.api_key_env}
                    onChange={(event) => setForm({ ...form, api_key_env: event.target.value })}
                    placeholder="EPH_LLM_API_KEY"
                  />
                </label>
                <label>
                  Timeout (segundos)
                  <input
                    type="number"
                    min="1"
                    max="600"
                    value={form.timeout_seconds}
                    onChange={(event) =>
                      setForm({ ...form, timeout_seconds: event.target.value })
                    }
                  />
                </label>
                <button type="submit" disabled={creating}>
                  {creating ? "Agregando…" : "Agregar perfil"}
                </button>
              </form>
              {message && <p className="notice">{message}</p>}
            </section>
          )}

          <ul className="profile-list">
            {data.profiles.map((profile) => {
              const isSelected = data.selected === profile.name;
              const isBusy = busy?.endsWith(`:${profile.name}`);
              const testedOk = health[profile.name]?.ok === true;
              return (
                <li key={profile.name} className={isSelected ? "profile selected" : "profile"}>
                  <div className="profile-head">
                    <h3>{profile.name}</h3>
                    {isSelected && <span className="badge">Seleccionado</span>}
                    {!profile.enabled && <span className="badge muted">Deshabilitado</span>}
                    {profile.hosted && <span className="badge">Hosted</span>}
                  </div>
                  <dl>
                    <div>
                      <dt>URL</dt>
                      <dd>{profile.base_url}</dd>
                    </div>
                    <div>
                      <dt>Modelo</dt>
                      <dd>{profile.model}</dd>
                    </div>
                    <div>
                      <dt>Clave</dt>
                      <dd>
                        {profile.api_key_env ?? "sin variable"}
                        {profile.has_api_key ? " (configurada)" : " (ausente)"}
                      </dd>
                    </div>
                  </dl>
                  <div className="profile-actions">
                    <button
                      type="button"
                      disabled={isBusy || !profile.enabled || !testedOk}
                      title={testedOk ? undefined : "Probá la conexión antes de seleccionar"}
                      onClick={() => select(profile.name)}
                    >
                      Usar
                    </button>
                    <button type="button" disabled={isBusy} onClick={() => test(profile.name)}>
                      {busy === `test:${profile.name}` ? "Probando…" : "Probar conexión"}
                    </button>
                  </div>
                  {health[profile.name] && <ProviderStatus health={health[profile.name]} />}
                  {!testedOk && (
                    <p className="muted">Probá la conexión para habilitar “Usar”.</p>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}
