# Backends de base de datos

## Decisión

El agente separa la lógica estadística de la infraestructura mediante
`DatabaseSettings` y, en la siguiente fase, adaptadores con un contrato común.

| Backend | Estado | Uso recomendado |
|---|---|---|
| SQLite | Principal | Desarrollo local, pruebas y defensa sin internet. |
| PostgreSQL | Principal | Demo desplegada en Neon, Supabase u otro servicio administrado. |
| Cloudflare D1 | Experimental | Demo serverless cuando exista un adaptador HTTP/Worker probado. |
| Firestore | No apto para microdatos | Datos auxiliares futuros, no consultas EPH. |

## Por qué PostgreSQL es la opción remota principal

- Conserva SQL auditable y permite vistas, joins, agregaciones y roles read-only.
- Neon y Supabase ofrecen planes gratuitos suficientes para la base inicial.
- FastAPI puede conectarse con un driver estándar sin exponer la base al navegador.
- La migración desde SQLite puede probarse con el mismo golden set.

## Garantías por entorno

### SQLite local

- La base se reconstruye desde el ZIP original.
- El runtime abre el archivo con `mode=ro` y `PRAGMA query_only`.
- El archivo generado no se versiona.

### PostgreSQL remoto

- `EPH_DATABASE_URL` se inyecta como secreto.
- Se crea un rol del runtime con permisos `SELECT` solo sobre vistas semánticas.
- El rol de carga es distinto y no se usa durante consultas del agente.
- Se exige TLS (`sslmode=require` como mínimo).

### Cloudflare D1

- Usa dialecto SQLite, pero no una conexión local `sqlite3`.
- Requiere un adaptador que invoque D1 por API o mediante un Worker.
- No se considera soportado hasta pasar el mismo conjunto de pruebas que SQLite.

## Por qué Firestore no almacena los microdatos

Firestore es una base documental. Traducir preguntas EPH a consultas de documentos
eliminaría la característica central del trabajo: mostrar y auditar el SQL ejecutado.
Puede evaluarse más adelante para preferencias de usuario, borradores o historial de
conversaciones, que son datos auxiliares y no estadísticos.

## Configuración

```dotenv
EPH_DATABASE_BACKEND=sqlite
EPH_DATABASE_URL=sqlite:///eph.sqlite
```

Para PostgreSQL:

```dotenv
EPH_DATABASE_BACKEND=postgresql
EPH_DATABASE_URL=postgresql://usuario:clave@host/base?sslmode=require
```

Las credenciales permanecen en `.env` local o en el gestor de secretos de la
plataforma. La aplicación nunca devuelve `EPH_DATABASE_URL` al frontend.

## Próximo paso

Crear el protocolo `DatabaseAdapter` y dos implementaciones:

1. `SQLiteAdapter`, utilizado por pruebas y desarrollo.
2. `PostgresAdapter`, utilizado por el despliegue.

Ambos deberán exponer las mismas herramientas, aplicar límites equivalentes y pasar
el mismo golden set.
