import { useEffect, useState, type ComponentType } from "react";

import { api, type AuthUser } from "./api/client";
import AgentPage from "./pages/AgentPage";
import LoginPage from "./pages/LoginPage";
import ProjectPage from "./pages/ProjectPage";
import SettingsPage from "./pages/SettingsPage";

type Route = {
  path: string;
  label: string;
  Component: ComponentType;
};

const ROUTES: Route[] = [
  { path: "proyecto", label: "Proyecto", Component: ProjectPage },
  { path: "agente", label: "Agente", Component: AgentPage },
  { path: "configuracion", label: "Configuración", Component: SettingsPage },
];

function routeFromHash(): string {
  const candidate = window.location.hash.replace(/^#\/?/, "");
  return ROUTES.some((route) => route.path === candidate) ? candidate : "proyecto";
}

export default function App() {
  const [current, setCurrent] = useState(routeFromHash);
  const [user, setUser] = useState<AuthUser | null | undefined>(undefined);

  useEffect(() => {
    let active = true;
    api
      .me()
      .then((value) => {
        if (active) setUser(value);
      })
      .catch(() => {
        if (active) setUser(null);
      });
    const onUnauthorized = () => setUser(null);
    window.addEventListener("eph:unauthorized", onUnauthorized);
    return () => {
      active = false;
      window.removeEventListener("eph:unauthorized", onUnauthorized);
    };
  }, []);

  useEffect(() => {
    if (!window.location.hash) {
      window.location.hash = "#/proyecto";
    }
    const onChange = () => setCurrent(routeFromHash());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  if (user === undefined) {
    return (
      <div className="app-shell">
        <main>
          <p className="muted">Cargando…</p>
        </main>
      </div>
    );
  }

  if (user === null) {
    return <LoginPage onLogin={setUser} />;
  }

  const route = ROUTES.find((item) => item.path === current) ?? ROUTES[0];
  const Active = route.Component;

  async function logout() {
    try {
      await api.logout();
    } finally {
      setUser(null);
    }
  }

  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        Saltar al contenido
      </a>
      <header className="app-header">
        <div className="brand">
          Agente EPH <span>1T 2026</span>
        </div>
        <nav aria-label="Secciones">
          {ROUTES.map((item) => (
            <a
              key={item.path}
              href={`#/${item.path}`}
              aria-current={item.path === current ? "page" : undefined}
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="user-menu">
          <span title="Usuario conectado">{user.username}</span>
          <button type="button" onClick={logout}>
            Salir
          </button>
        </div>
      </header>
      <main id="main">
        <Active />
      </main>
      <footer className="app-footer">
        Microdatos EPH 1T 2026 · INDEC · Respuestas auditables con SQL visible
      </footer>
    </div>
  );
}
