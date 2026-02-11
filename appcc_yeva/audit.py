"""Motor de auditoría para validar la calidad de un plan APPCC."""

from __future__ import annotations

from dataclasses import dataclass
from .plan import HACCPPlan

VALID_HAZARD_CATEGORIES = {"Biológico", "Químico", "Físico", "Alérgenos"}


@dataclass(frozen=True)
class AuditIssue:
    """Incidencia detectada durante la auditoría."""

    level: str
    code: str
    message: str


@dataclass(frozen=True)
class AuditReport:
    """Resultado completo de la auditoría."""

    issues: tuple[AuditIssue, ...]

    @property
    def errors(self) -> tuple[AuditIssue, ...]:
        return tuple(issue for issue in self.issues if issue.level == "error")

    @property
    def warnings(self) -> tuple[AuditIssue, ...]:
        return tuple(issue for issue in self.issues if issue.level == "warning")

    @property
    def is_compliant(self) -> bool:
        return not self.errors

    def summary(self) -> str:
        lines = ["Auditoría APPCC", "===============", ""]
        lines.append(f"Cumplimiento: {'Sí' if self.is_compliant else 'No'}")
        lines.append(f"Errores: {len(self.errors)}")
        lines.append(f"Advertencias: {len(self.warnings)}")

        if self.issues:
            lines.append("")
            lines.append("Hallazgos:")
            for issue in self.issues:
                lines.append(f"- [{issue.level.upper()}] {issue.code}: {issue.message}")
        else:
            lines.append("")
            lines.append("No se detectaron incidencias.")

        return "\n".join(lines)


def audit_plan(plan: HACCPPlan) -> AuditReport:
    """Ejecuta validaciones de cumplimiento APPCC sobre un plan."""

    issues: list[AuditIssue] = []

    if len(plan.team) < 2:
        issues.append(
            AuditIssue(
                level="error",
                code="TEAM_MIN_SIZE",
                message="El equipo APPCC debe tener al menos dos responsables.",
            )
        )

    if not plan.product_description.strip():
        issues.append(
            AuditIssue(
                level="error",
                code="PRODUCT_DESCRIPTION_REQUIRED",
                message="La descripción del producto es obligatoria.",
            )
        )

    if not plan.intended_use.strip():
        issues.append(
            AuditIssue(
                level="error",
                code="INTENDED_USE_REQUIRED",
                message="El uso previsto del producto es obligatorio.",
            )
        )

    if not plan.process_steps:
        issues.append(
            AuditIssue(
                level="error",
                code="PROCESS_STEPS_REQUIRED",
                message="El plan debe incluir al menos un paso del proceso.",
            )
        )

    for step in plan.process_steps:
        if not step.hazards:
            issues.append(
                AuditIssue(
                    level="warning",
                    code="STEP_WITHOUT_HAZARDS",
                    message=f"El paso '{step.name}' no tiene peligros identificados.",
                )
            )

        if step.schedule_start and step.schedule_end and step.schedule_start >= step.schedule_end:
            issues.append(
                AuditIssue(
                    level="error",
                    code="INVALID_STEP_SCHEDULE",
                    message=f"El horario del paso '{step.name}' es inválido (inicio >= fin).",
                )
            )

        for hazard in step.hazards:
            if hazard.category not in VALID_HAZARD_CATEGORIES:
                issues.append(
                    AuditIssue(
                        level="warning",
                        code="UNKNOWN_HAZARD_CATEGORY",
                        message=(
                            f"El peligro '{hazard.name}' en '{step.name}' usa categoría "
                            f"'{hazard.category}', fuera del catálogo esperado."
                        ),
                    )
                )

            if not hazard.preventive_measures:
                issues.append(
                    AuditIssue(
                        level="warning",
                        code="MISSING_PREVENTIVE_MEASURES",
                        message=f"El peligro '{hazard.name}' en '{step.name}' no define medidas preventivas.",
                    )
                )

            if hazard.critical_limits and not hazard.monitoring:
                issues.append(
                    AuditIssue(
                        level="error",
                        code="MISSING_MONITORING",
                        message=(
                            f"El peligro '{hazard.name}' en '{step.name}' tiene límites críticos "
                            "pero no monitorización."
                        ),
                    )
                )

            if hazard.critical_limits and not hazard.corrective_actions:
                issues.append(
                    AuditIssue(
                        level="error",
                        code="MISSING_CORRECTIVE_ACTIONS",
                        message=(
                            f"El peligro '{hazard.name}' en '{step.name}' tiene límites críticos "
                            "pero no acciones correctivas."
                        ),
                    )
                )

    if not plan.verification_records:
        issues.append(
            AuditIssue(
                level="warning",
                code="VERIFICATION_RECORDS_REQUIRED",
                message="Se recomiendan registros de verificación para cerrar el ciclo APPCC.",
            )
        )

    if not plan.documentation:
        issues.append(
            AuditIssue(
                level="warning",
                code="DOCUMENTATION_REQUIRED",
                message="El plan debería incluir requisitos documentales.",
            )
        )

    for req in plan.documentation:
        if not req.retention_time.strip():
            issues.append(
                AuditIssue(
                    level="warning",
                    code="RETENTION_TIME_REQUIRED",
                    message=f"El documento '{req.name}' no define tiempo de retención.",
                )
            )

    return AuditReport(issues=tuple(issues))
