# APPCC de Yeva

Este repositorio contiene un ejemplo simplificado de la documentación APPCC (HACCP) para la empresa ficticia **Yeva**. El objetivo es ofrecer una base digital que pueda ampliarse con nuevos procesos, peligros y registros.

## Estructura

- `appcc_yeva/models.py`: dataclasses que modelan los diferentes elementos del plan (pasos, peligros, límites críticos, etc.).
- `appcc_yeva/plan.py`: lógica para construir el plan, serializarlo y exportarlo.
- `appcc_yeva/audit.py`: reglas de auditoría para validar cumplimiento mínimo del plan APPCC.
- `appcc_yeva/cli.py`: interfaz de línea de comandos para consultar el resumen, auditar, previsualizar, servir o exportar el plan en JSON.
- `appcc_yeva/preview.py`: generador de una vista HTML del plan APPCC.
- `tests/test_audit.py`: pruebas automáticas de la auditoría.
- `tests/test_preview.py`: pruebas automáticas de la previsualización.
- `pyproject.toml`: metadatos mínimos del proyecto y punto de entrada del CLI `appcc-yeva`.

## Requisitos

- Python 3.10 o superior.


## Si no tienes el proyecto en tu PC (paso previo)

Si en tu ordenador no existe la carpeta del proyecto, primero debes **descargar/clonar** el repositorio y entrar en esa carpeta.

### Opción A: descargar ZIP
1. Descarga el ZIP del repositorio desde GitHub/GitLab.
2. Descomprime el ZIP (por ejemplo en `Documentos/Pruebas-codex`).
3. Abre una terminal en esa carpeta.

### Opción B: clonar con Git (recomendado)
```bash
git clone <URL_DEL_REPOSITORIO>
cd Pruebas-codex
```

Después de eso ya podrás ejecutar comandos como:
```bash
python -m appcc_yeva.cli servir-preview --host 127.0.0.1 --puerto 8000
```

## Uso rápido

Instala las dependencias del proyecto (no se requieren paquetes externos) y ejecuta el comando:

```bash
python -m appcc_yeva.cli resumen
```

Esto mostrará un resumen con el equipo APPCC, el producto, el uso previsto y los puntos de control crítico identificados.

Para lanzar la auditoría de cumplimiento:

```bash
python -m appcc_yeva.cli auditoria
```

La auditoría devuelve código de salida `0` si el plan cumple los controles definidos y `1` si detecta errores.

Para generar una previsualización HTML:

```bash
python -m appcc_yeva.cli previsualizar
```

Esto crea por defecto `preview/appcc_yeva.html` y te muestra la ruta absoluta para abrirla con `file://...`.
Si quieres que intente abrirla automáticamente en tu navegador local:

```bash
python -m appcc_yeva.cli previsualizar --abrir
```

Para generar y servir la vista directamente (recomendado):

```bash
python -m appcc_yeva.cli servir-preview --host 0.0.0.0 --puerto 8000
```

Luego abre: `http://127.0.0.1:8000/appcc_yeva.html` **solo si el servidor corre en tu misma máquina**.

> Nota importante: si ejecutas el comando en un contenedor/servidor remoto, `127.0.0.1` de tu PC **no** apunta a ese servidor remoto (por eso aparece conexión rechazada). En ese caso usa port-forwarding del entorno o abre el HTML exportado localmente con `file://`.

Para exportar el plan completo en JSON:

```bash
python -m appcc_yeva.cli exportar plan.json
```

El archivo generado incluye todos los pasos del proceso, peligros asociados, límites críticos, acciones de monitorización, correctivos y requisitos documentales.

## Qué valida la auditoría

La auditoría actual comprueba automáticamente:

1. Equipo APPCC con al menos dos responsables.
2. Descripción de producto y uso previsto no vacíos.
3. Existencia de pasos de proceso.
4. Coherencia horaria por paso (`inicio < fin`).
5. Coherencia de peligros críticos (si hay límites críticos, debe haber monitorización y acciones correctivas).
6. Presencia de medidas preventivas por peligro.
7. Categorías de peligro en catálogo esperado (biológico, químico, físico y alérgenos).
8. Registros de verificación y requisitos documentales.

## Personalización

- Añade o modifica pasos del proceso editando `load_default_plan` en `appcc_yeva/plan.py`.
- Amplía los modelos en `appcc_yeva/models.py` si necesitas registrar nuevos atributos (por ejemplo, validaciones de proveedores o planes de formación).
- Ajusta los controles de `appcc_yeva/audit.py` para reflejar requisitos regulatorios internos o de cliente.
- Si quieres distribuir el CLI como paquete, utiliza `pip install -e .` y ejecuta `appcc-yeva` directamente desde cualquier terminal.

## Próximos pasos sugeridos

1. Añadir niveles de severidad/probabilidad para priorizar riesgos.
2. Soportar carga de planes desde YAML/JSON para separar datos de código.
3. Incorporar validaciones normativas específicas (por ejemplo, UE 852/2004) según el país objetivo.
