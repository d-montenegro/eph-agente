import { describe, expect, it } from "vitest";

import { escapeHtml, renderMarkdown } from "./markdown";

describe("renderMarkdown", () => {
  it("renderiza títulos y párrafos", () => {
    const html = renderMarkdown("# Título\n\nUn párrafo.");

    expect(html).toContain("<h1>Título</h1>");
    expect(html).toContain("<p>Un párrafo.</p>");
  });

  it("aplica negrita, itálica, código y enlaces", () => {
    const html = renderMarkdown("**fuerte** *suave* `código` [INDEC](https://indec.gob.ar)");

    expect(html).toContain("<strong>fuerte</strong>");
    expect(html).toContain("<em>suave</em>");
    expect(html).toContain("<code>código</code>");
    expect(html).toContain('href="https://indec.gob.ar"');
  });

  it("arma listas ordenadas y desordenadas", () => {
    const html = renderMarkdown("- uno\n- dos\n\n1. primero\n2. segundo");

    expect(html).toContain("<ul>");
    expect(html).toContain("<li>dos</li>");
    expect(html).toContain("<ol>");
    expect(html).toContain("<li>primero</li>");
  });

  it("escapa HTML para no inyectar scripts", () => {
    const html = renderMarkdown('<script>alert("x")</script>');

    expect(html).not.toContain("<script>");
    expect(html).toContain("&lt;script&gt;");
  });

  it("respeta bloques de código", () => {
    const html = renderMarkdown("```\nSELECT 1 < 2\n```");

    expect(html).toContain("<pre><code>");
    expect(html).toContain("SELECT 1 &lt; 2");
  });
});

describe("escapeHtml", () => {
  it("escapa comillas y ampersands", () => {
    expect(escapeHtml(`<a href="x">&</a>`)).toBe("&lt;a href=&quot;x&quot;&gt;&amp;&lt;/a&gt;");
  });
});
