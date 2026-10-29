-- Capa semántica de la EPH 1T 2026.
-- Se construye sobre las tablas crudas del INDEC (individual y hogar), que
-- quedan intactas. Solo estas vistas son visibles para el agente.
-- Los códigos se traducen a etiquetas legibles y los valores especiales
-- (-9 no respuesta, 0 fuera de universo, 9 Ns/Nr) se convierten en NULL.

DROP VIEW IF EXISTS personas;
CREATE VIEW personas AS
SELECT
    CODUSU AS codusu,
    NRO_HOGAR AS nro_hogar,
    COMPONENTE AS componente,
    ANO4 AS anio,
    TRIMESTRE AS trimestre,
    CASE AGLOMERADO
        WHEN 2 THEN 'Gran La Plata'
        WHEN 3 THEN 'Bahía Blanca-Cerri'
        WHEN 4 THEN 'Gran Rosario'
        WHEN 5 THEN 'Gran Santa Fe'
        WHEN 6 THEN 'Gran Paraná'
        WHEN 7 THEN 'Posadas'
        WHEN 8 THEN 'Gran Resistencia'
        WHEN 9 THEN 'Comodoro Rivadavia-Rada Tilly'
        WHEN 10 THEN 'Gran Mendoza'
        WHEN 12 THEN 'Corrientes'
        WHEN 13 THEN 'Gran Córdoba'
        WHEN 14 THEN 'Concordia'
        WHEN 15 THEN 'Formosa'
        WHEN 17 THEN 'Neuquén-Plottier'
        WHEN 18 THEN 'Santiago del Estero-La Banda'
        WHEN 19 THEN 'Jujuy-Palpalá'
        WHEN 20 THEN 'Río Gallegos'
        WHEN 22 THEN 'Gran Catamarca'
        WHEN 23 THEN 'Gran Salta'
        WHEN 25 THEN 'La Rioja'
        WHEN 26 THEN 'Gran San Luis'
        WHEN 27 THEN 'Gran San Juan'
        WHEN 29 THEN 'Gran Tucumán-Tafí Viejo'
        WHEN 30 THEN 'Santa Rosa-Toay'
        WHEN 31 THEN 'Ushuaia-Río Grande'
        WHEN 32 THEN 'Ciudad Autónoma de Buenos Aires'
        WHEN 33 THEN 'Partidos del Gran Buenos Aires'
        WHEN 34 THEN 'Mar del Plata'
        WHEN 36 THEN 'Río Cuarto'
        WHEN 38 THEN 'San Nicolás-Villa Constitución'
        WHEN 91 THEN 'Rawson-Trelew'
        WHEN 93 THEN 'Viedma-Carmen de Patagones'
    END AS aglomerado,
    CASE REGION
        WHEN 1 THEN 'Gran Buenos Aires'
        WHEN 40 THEN 'Noroeste'
        WHEN 41 THEN 'Noreste'
        WHEN 42 THEN 'Cuyo'
        WHEN 43 THEN 'Pampeana'
        WHEN 44 THEN 'Patagonia'
    END AS region,
    PONDERA AS pondera,
    CASE CH04
        WHEN 1 THEN 'Varón'
        WHEN 2 THEN 'Mujer'
    END AS sexo,
    CASE WHEN CH06 < 0 OR CH06 = 99 THEN NULL ELSE CH06 END AS edad,
    CASE
        WHEN CH06 IS NULL OR CH06 < 0 OR CH06 = 99 THEN NULL
        WHEN CH06 < 10 THEN '0-9'
        WHEN CH06 < 15 THEN '10-14'
        WHEN CH06 < 25 THEN '15-24'
        WHEN CH06 < 35 THEN '25-34'
        WHEN CH06 < 45 THEN '35-44'
        WHEN CH06 < 55 THEN '45-54'
        WHEN CH06 < 65 THEN '55-64'
        ELSE '65+'
    END AS grupo_edad,
    CASE CH03
        WHEN 1 THEN 'Jefe/a'
        WHEN 2 THEN 'Cónyuge/pareja'
        WHEN 3 THEN 'Hijo/a/hijastro/a'
        WHEN 4 THEN 'Yerno/nuera'
        WHEN 5 THEN 'Nieto/a'
        WHEN 6 THEN 'Madre/padre'
        WHEN 7 THEN 'Suegro/a'
        WHEN 8 THEN 'Hermano/a'
        WHEN 9 THEN 'Otros familiares'
        WHEN 10 THEN 'No familiares'
    END AS parentesco,
    CASE ESTADO
        WHEN 1 THEN 'Ocupado'
        WHEN 2 THEN 'Desocupado'
        WHEN 3 THEN 'Inactivo'
        WHEN 4 THEN 'Menor de 10 años'
    END AS estado_actividad,
    CASE WHEN ESTADO = 1 THEN 1 ELSE 0 END AS es_ocupado,
    CASE WHEN ESTADO = 2 THEN 1 ELSE 0 END AS es_desocupado,
    CASE WHEN ESTADO = 3 THEN 1 ELSE 0 END AS es_inactivo,
    CASE CAT_OCUP
        WHEN 1 THEN 'Patrón'
        WHEN 2 THEN 'Cuenta propia'
        WHEN 3 THEN 'Obrero o empleado'
        WHEN 4 THEN 'Trabajador familiar sin remuneración'
    END AS categoria_ocupacion,
    CASE EMPLEO
        WHEN 1 THEN 'Formal'
        WHEN 2 THEN 'Informal'
    END AS empleo_formal,
    CASE SECTOR
        WHEN 1 THEN 'Formal'
        WHEN 2 THEN 'Informal'
        WHEN 3 THEN 'Hogares'
    END AS sector,
    CASE WHEN ESTADO = 1 AND P21 <> -9 THEN P21 END AS ingreso_ocupacion_principal,
    CASE WHEN ESTADO = 1 AND P21 <> -9 THEN PONDIIO END AS pondera_ingreso_ocupacion,
    CASE WHEN ESTADO IN (1, 2, 3) AND P47T <> -9 THEN P47T END AS ingreso_total_individual,
    CASE WHEN ESTADO IN (1, 2, 3) AND P47T <> -9 THEN PONDII END AS pondera_ingreso_total,
    ITF AS ingreso_total_familiar,
    IPCF AS ingreso_per_capita_familiar,
    PONDIH AS pondera_ingreso_familiar
FROM individual;

DROP VIEW IF EXISTS hogares;
CREATE VIEW hogares AS
SELECT
    CODUSU AS codusu,
    NRO_HOGAR AS nro_hogar,
    ANO4 AS anio,
    TRIMESTRE AS trimestre,
    CASE AGLOMERADO
        WHEN 2 THEN 'Gran La Plata'
        WHEN 3 THEN 'Bahía Blanca-Cerri'
        WHEN 4 THEN 'Gran Rosario'
        WHEN 5 THEN 'Gran Santa Fe'
        WHEN 6 THEN 'Gran Paraná'
        WHEN 7 THEN 'Posadas'
        WHEN 8 THEN 'Gran Resistencia'
        WHEN 9 THEN 'Comodoro Rivadavia-Rada Tilly'
        WHEN 10 THEN 'Gran Mendoza'
        WHEN 12 THEN 'Corrientes'
        WHEN 13 THEN 'Gran Córdoba'
        WHEN 14 THEN 'Concordia'
        WHEN 15 THEN 'Formosa'
        WHEN 17 THEN 'Neuquén-Plottier'
        WHEN 18 THEN 'Santiago del Estero-La Banda'
        WHEN 19 THEN 'Jujuy-Palpalá'
        WHEN 20 THEN 'Río Gallegos'
        WHEN 22 THEN 'Gran Catamarca'
        WHEN 23 THEN 'Gran Salta'
        WHEN 25 THEN 'La Rioja'
        WHEN 26 THEN 'Gran San Luis'
        WHEN 27 THEN 'Gran San Juan'
        WHEN 29 THEN 'Gran Tucumán-Tafí Viejo'
        WHEN 30 THEN 'Santa Rosa-Toay'
        WHEN 31 THEN 'Ushuaia-Río Grande'
        WHEN 32 THEN 'Ciudad Autónoma de Buenos Aires'
        WHEN 33 THEN 'Partidos del Gran Buenos Aires'
        WHEN 34 THEN 'Mar del Plata'
        WHEN 36 THEN 'Río Cuarto'
        WHEN 38 THEN 'San Nicolás-Villa Constitución'
        WHEN 91 THEN 'Rawson-Trelew'
        WHEN 93 THEN 'Viedma-Carmen de Patagones'
    END AS aglomerado,
    CASE REGION
        WHEN 1 THEN 'Gran Buenos Aires'
        WHEN 40 THEN 'Noroeste'
        WHEN 41 THEN 'Noreste'
        WHEN 42 THEN 'Cuyo'
        WHEN 43 THEN 'Pampeana'
        WHEN 44 THEN 'Patagonia'
    END AS region,
    PONDERA AS pondera,
    IX_TOT AS cantidad_miembros,
    ITF AS ingreso_total_familiar,
    IPCF AS ingreso_per_capita_familiar,
    PONDIH AS pondera_ingreso_familiar
FROM hogar;
