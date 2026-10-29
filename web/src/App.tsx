import { useEffect, useState, type ComponentType } from "react";

import AgentPage from "./pages/AgentPage";
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

  useEffect(() => {
    if (!window.location.hash) {
      window.location.hash = "#/proyecto";
    }
    const onChange = () => setCurrent(routeFromHash());
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const route = ROUTES.find((item) => item.path === current) ?? ROUTES[0];
  const Active = route.Component;

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
