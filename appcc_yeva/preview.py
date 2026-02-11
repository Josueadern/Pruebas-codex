"""Utilidades para generar una previsualización HTML del plan APPCC."""

from __future__ import annotations

from html import escape
from pathlib import Path

from .plan import HACCPPlan


def render_plan_html(plan: HACCPPlan) -> str:
    """Construye una página HTML simple para revisar el plan APPCC."""

    step_sections: list[str] = []
    for step in plan.process_steps:
        hazards = []
        for hazard in step.hazards:
            limits = "".join(
                f"<li>{escape(limit.describe())}</li>" for limit in hazard.critical_limits
            ) or "<li>Sin límites críticos definidos.</li>"
            monitors = "".join(
                f"<li>{escape(item.description)} ({escape(item.frequency)})</li>"
                for item in hazard.monitoring
            ) or "<li>Sin monitorización definida.</li>"
            actions = "".join(
                f"<li>{escape(item.description)} ({escape(item.responsible)})</li>"
                for item in hazard.corrective_actions
            ) or "<li>Sin acciones correctivas definidas.</li>"

            hazards.append(
                """
                <article class=\"hazard\">
                  <h4>{name}</h4>
                  <p><strong>Categoría:</strong> {category}</p>
                  <p><strong>Causa:</strong> {cause}</p>
                  <p><strong>Medidas preventivas:</strong> {measures}</p>
                  <p><strong>Límites críticos</strong></p>
                  <ul>{limits}</ul>
                  <p><strong>Monitorización</strong></p>
                  <ul>{monitors}</ul>
                  <p><strong>Acciones correctivas</strong></p>
                  <ul>{actions}</ul>
                </article>
                """.format(
                    name=escape(hazard.name),
                    category=escape(hazard.category),
                    cause=escape(hazard.cause),
                    measures=escape(", ".join(hazard.preventive_measures) or "Sin medidas preventivas definidas."),
                    limits=limits,
                    monitors=monitors,
                    actions=actions,
                )
            )

        slot = (
            f"{step.schedule_start.strftime('%H:%M')} - {step.schedule_end.strftime('%H:%M')}"
            if step.schedule_start and step.schedule_end
            else "Sin horario"
        )
        step_sections.append(
            """
            <section class=\"step\">
              <h3>{name}</h3>
              <p><strong>Horario:</strong> {slot}</p>
              <p>{description}</p>
              {hazards}
            </section>
            """.format(
                name=escape(step.name),
                slot=escape(slot),
                description=escape(step.description),
                hazards="".join(hazards) or "<p>Sin peligros identificados.</p>",
            )
        )

    docs = "".join(
        f"<li>{escape(doc.name)} — {escape(doc.location)} ({escape(doc.retention_time)})</li>"
        for doc in plan.documentation
    )

    return f"""<!doctype html>
<html lang=\"es\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\" />
    <title>Previsualización APPCC Yeva</title>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1a1a1a; background: #f7f9fc; }}
      .card {{ background: white; border-radius: 10px; padding: 1.25rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,.08); }}
      h1, h2, h3, h4 {{ margin-top: 0; }}
      .hazard {{ border-top: 1px solid #e6e9ef; margin-top: .75rem; padding-top: .75rem; }}
      ul {{ margin-top: .3rem; }}
    </style>
  </head>
  <body>
    <section class=\"card\">
      <h1>Plan APPCC de Yeva</h1>
      <p><strong>Equipo:</strong> {escape(', '.join(plan.team))}</p>
      <p><strong>Producto:</strong> {escape(plan.product_description)}</p>
      <p><strong>Uso previsto:</strong> {escape(plan.intended_use)}</p>
    </section>

    <section class=\"card\">
      <h2>Pasos del proceso</h2>
      {''.join(step_sections)}
    </section>

    <section class=\"card\">
      <h2>Documentación</h2>
      <ul>{docs}</ul>
    </section>
  </body>
</html>
"""


def export_plan_preview(plan: HACCPPlan, path: Path) -> Path:
    """Genera un archivo HTML de previsualización para el plan indicado."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_plan_html(plan), encoding="utf-8")
    return path
