"""Interfaz de línea de comandos para consultar el plan APPCC."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import webbrowser

from .audit import audit_plan
from .plan import export_default_plan, load_default_plan
from .preview import export_plan_preview


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Herramientas APPCC para Yeva")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("resumen", help="Muestra un resumen del plan")

    export_parser = sub.add_parser("exportar", help="Exporta el plan por defecto en JSON")
    export_parser.add_argument(
        "destino",
        type=Path,
        help="Ruta del archivo JSON a generar",
    )

    sub.add_parser(
        "auditoria",
        help="Ejecuta una auditoría rápida de cumplimiento APPCC sobre el plan por defecto",
    )

    preview_parser = sub.add_parser(
        "previsualizar",
        help="Genera una vista HTML del plan para abrirla en navegador",
    )
    preview_parser.add_argument(
        "destino",
        type=Path,
        nargs="?",
        default=Path("preview/appcc_yeva.html"),
        help="Ruta del archivo HTML a generar (por defecto: preview/appcc_yeva.html)",
    )
    preview_parser.add_argument(
        "--abrir",
        action="store_true",
        help="Intenta abrir automáticamente el HTML en el navegador local",
    )

    serve_parser = sub.add_parser(
        "servir-preview",
        help="Genera la vista HTML y la sirve en http://127.0.0.1:<puerto>",
    )
    serve_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host de escucha del servidor (por defecto: 0.0.0.0)",
    )
    serve_parser.add_argument(
        "--puerto",
        type=int,
        default=8000,
        help="Puerto HTTP para servir la previsualización (por defecto: 8000)",
    )

    return parser


def run_summary() -> None:
    plan = load_default_plan()
    print(plan.summary())


def run_export(path: Path) -> None:
    export_default_plan(path)
    print(f"Plan exportado en {path}")


def run_audit() -> int:
    report = audit_plan(load_default_plan())
    print(report.summary())
    return 0 if report.is_compliant else 1


def run_preview(path: Path, *, open_browser: bool = False) -> Path:
    output = export_plan_preview(load_default_plan(), path)
    resolved = output.resolve()
    print(f"Previsualización generada en {resolved}")
    print(f"Abre también con file://{resolved}")

    if open_browser:
        webbrowser.open_new_tab(f"file://{resolved}")

    return output


def run_serve_preview(host: str, port: int) -> None:
    output = run_preview(Path("preview/appcc_yeva.html"))
    directory = output.parent.resolve()
    filename = output.name

    handler = partial(SimpleHTTPRequestHandler, directory=str(directory))
    server = ThreadingHTTPServer((host, port), handler)
    print(f"Servidor activo en http://{host}:{port}/{filename}")
    if host == "0.0.0.0":
        print(f"URL local (misma máquina): http://127.0.0.1:{port}/{filename}")
    print("Si estás en contenedor/servidor remoto, 127.0.0.1 de tu PC no apunta al servidor remoto.")
    print("Usa port-forwarding o abre el archivo generado con file://.")
    print("Pulsa Ctrl+C para detenerlo.")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Servidor detenido.")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "resumen":
        run_summary()
    elif args.command == "exportar":
        run_export(args.destino)
    elif args.command == "auditoria":
        raise SystemExit(run_audit())
    elif args.command == "previsualizar":
        run_preview(args.destino, open_browser=args.abrir)
    elif args.command == "servir-preview":
        run_serve_preview(args.host, args.puerto)
    else:  # pragma: no cover
        parser.error("Comando no soportado")


if __name__ == "__main__":  # pragma: no cover
    main()
