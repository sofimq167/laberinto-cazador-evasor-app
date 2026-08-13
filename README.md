
# Laberinto: Cazador vs Evasor

Simulador con Flask (backend) y HTML (frontend) en un solo contenedor.

## ¿Cómo correrlo con Docker Compose?

1. Asegúrate de tener Docker y Docker Compose instalados.
2. En la carpeta del proyecto, ejecuta:

```sh
docker compose up -d
```

3. Abre en tu navegador:
   - http://localhost:5000
   - Salud backend: http://localhost:5000/api/health

Para detener:

```sh
docker compose down
```

## Estructura del proyecto

```
.
├── Dockerfile              # Imagen única (contexto de build = raíz)
├── docker-compose.yml      # Orquestador simple
├── render.yaml             # Blueprint de despliegue en Render
├── .dockerignore
├── README.md
└── app/
    ├── backend/
    │   ├── maze_simulator_backend.py   # Backend Flask (API REST)
    │   └── requirements.txt
    └── frontend/
        ├── index.html                  # Frontend estático
        └── styles.css
```

> El paper académico (`paper/`) se mantiene fuera de este repositorio mediante
> `.gitignore`; aquí solo vive la aplicación.

El Dockerfile aplana `app/backend/` y `app/frontend/` dentro de `/app` en la
imagen, de modo que Flask (con `static_folder='.'`) sirve el frontend desde su
directorio de trabajo.

## API

| Método | Ruta                 | Descripción                                            |
| ------ | -------------------- | ------------------------------------------------------ |
| GET    | `/`                  | Frontend del simulador                                 |
| GET    | `/api/health`        | Estado del backend                                     |
| POST   | `/api/compute-path`  | Calcula un camino (`aStar`, `dijkstra`, `dfsMemo`, `bellmanFord`) |
| POST   | `/api/simulate-step` | Avanza un paso de la simulación cazador vs evasor      |

## Despliegue en Render

El repositorio incluye `render.yaml`, así que basta con crear un **Blueprint**
en Render apuntando a este repo: detecta el servicio Docker, expone `$PORT` y
usa `/api/health` como health check.

## Notas

- Todo se sirve en el mismo puerto (5000); en Render se respeta `$PORT`.
- No necesitas configurar variables de entorno extra.
- El plan gratuito de Render suspende el servicio tras un rato inactivo: la
  primera petición después de dormir puede tardar ~30 s.
