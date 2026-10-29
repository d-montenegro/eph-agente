-- Metadatos versionados de la capa semántica.
-- Se reconstruyen desde semantic/columns.yml en cada instalación; no se editan
-- a mano en la base.

CREATE TABLE IF NOT EXISTS semantic_views (
    view_name TEXT PRIMARY KEY,
    source_table TEXT NOT NULL,
    description TEXT NOT NULL,
    period_anio INTEGER NOT NULL,
    period_trimestre INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS semantic_columns (
    view_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    source_column TEXT,
    description TEXT NOT NULL,
    data_type TEXT NOT NULL,
    possible_values TEXT,
    null_meaning TEXT,
    universe TEXT,
    weight TEXT,
    synonyms TEXT,
    notes TEXT,
    PRIMARY KEY (view_name, column_name),
    FOREIGN KEY (view_name) REFERENCES semantic_views (view_name)
);
