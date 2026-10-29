import { useEffect, useState } from "react";

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
