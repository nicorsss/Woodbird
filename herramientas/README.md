# Herramientas del proyecto

Copia versionada de los generadores de documentos, pruebas y gestión del proyecto Woodbird (cierre del riesgo R8, 16/11/2026).

Las fuentes de trabajo están en la carpeta `herramientas/` que está al lado de `sitio/` (`../herramientas`), y los scripts esperan ejecutarse desde ahí. Calculan las rutas como `Path(__file__).parent.parent / "sitio"`. Si se pierde esa carpeta, copiá esta de nuevo al lado de `sitio/` y ejecutá desde la raíz del proyecto, por ejemplo:

```
python herramientas/cierre_proyecto.py
python herramientas/pruebas_sprint4.py --docx
```

| Script | Genera |
|---|---|
| `terminos.py` | Términos y Condiciones (página y .docx) |
| `gestion_sprint3.py` | Matriz de riesgos, plan de casos de prueba y registro de cambios (Sprint 3) |
| `campana_instagram.py`, `panel_kpis.py` | Campaña de Instagram y Panel de KPIs (Sprint 3) |
| `carpeta_sprint3.py` | Carpeta integradora del Sprint 3 (PDF) |
| `imagenes_ia.py` | Importa, convierte y registra las imágenes generadas con IA |
| `cierre_sprint4.py` | Despliegue HTTPS y auditoría legal final (tareas 4.1 y 4.6) |
| `pruebas_sprint4.py` | Informe de pruebas y Lighthouse (tarea 4.2) |
| `cierre_proyecto.py` | Costos y desvíos, Gantt real y Acta de Cierre (tareas 4.3 y 4.4) |
| `trello.py` | Lista, mueve, crea y comenta tarjetas. Las credenciales se leen de `~/.trello.env` y **no** están en el repositorio |

Necesitan Python 3.11 con `python-docx`, `matplotlib` y `Pillow`, Node 22 y Chrome. La carpeta integradora usa además Word (COM).
