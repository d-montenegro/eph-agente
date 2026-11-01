import { useState, type FormEvent } from "react";

import { api, ApiError, type AuthUser } from "../api/client";

export default function LoginPage({ onLogin }: { onLogin: (user: AuthUser) => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!username.trim() || !password) return;
    setLoading(true);
    setError(null);
    try {
      onLogin(await api.login(username.trim(), password));
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : "No se pudo iniciar sesión");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <section className="login-card" aria-label="Iniciar sesión">
        <div className="brand">
          Agente EPH <span>1T 2026</span>
        </div>
        <p className="muted">
          Acceso para la demo. Ingresá con tu usuario para consultar los microdatos.
        </p>
        <form onSubmit={submit}>
          <label>
            Usuario
            <input
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
              autoFocus
            />
          </label>
          <label>
            Contraseña
            <input
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={loading || !username.trim() || !password}>
            {loading ? "Ingresando…" : "Ingresar"}
          </button>
        </form>
        {error && (
          <p role="alert" className="error">
            {error}
          </p>
        )}
      </section>
    </div>
  );
}
