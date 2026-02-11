"""Lógica para construir y consultar el plan APPCC de Yeva."""

from __future__ import annotations

from datetime import time
from pathlib import Path
from typing import Iterable, List

import json

from .models import (
    CorrectiveAction,
    CriticalLimit,
    DocumentationRequirement,
    Hazard,
    MonitoringAction,
    ProcessStep,
    VerificationRecord,
)


class HACCPPlan:
    """Estructura inmutable que representa el plan APPCC."""

    def __init__(
        self,
        *,
        team: List[str],
        product_description: str,
        intended_use: str,
        process_steps: List[ProcessStep],
        verification_records: List[VerificationRecord],
        documentation: List[DocumentationRequirement],
    ) -> None:
        self.team = team
        self.product_description = product_description
        self.intended_use = intended_use
        self.process_steps = process_steps
        self.verification_records = verification_records
        self.documentation = documentation

    # Métodos auxiliares -------------------------------------------------
    def critical_control_points(self) -> List[ProcessStep]:
        return [step for step in self.process_steps if step.is_critical()]

    def summary(self) -> str:
        lines = ["Plan APPCC de Yeva", "====================", ""]
        lines.append("Equipo APPCC: " + ", ".join(self.team))
        lines.append("Producto: " + self.product_description)
        lines.append("Uso previsto: " + self.intended_use)
        lines.append("")
        lines.append("Puntos de control crítico:")
        for step in self.critical_control_points():
            lines.append(f"- {step.name}: {len(step.hazards)} peligros")
        lines.append("")
        lines.append("Documentación clave:")
        for doc in self.documentation:
            lines.append(f"- {doc.name} ({doc.location})")
        return "\n".join(lines)

    # Serialización ------------------------------------------------------
    def to_dict(self) -> dict:
        return {
            "team": self.team,
            "product_description": self.product_description,
            "intended_use": self.intended_use,
            "process_steps": [self._step_to_dict(step) for step in self.process_steps],
            "verification_records": [record.__dict__ for record in self.verification_records],
            "documentation": [doc.__dict__ for doc in self.documentation],
        }

    @staticmethod
    def _step_to_dict(step: ProcessStep) -> dict:
        return {
            "name": step.name,
            "description": step.description,
            "schedule_start": step.schedule_start.isoformat() if step.schedule_start else None,
            "schedule_end": step.schedule_end.isoformat() if step.schedule_end else None,
            "hazards": [
                {
                    "name": hazard.name,
                    "category": hazard.category,
                    "cause": hazard.cause,
                    "preventive_measures": hazard.preventive_measures,
                    "critical_limits": [limit.__dict__ for limit in hazard.critical_limits],
                    "monitoring": [monitor.__dict__ for monitor in hazard.monitoring],
                    "corrective_actions": [action.__dict__ for action in hazard.corrective_actions],
                }
                for hazard in step.hazards
            ],
        }

    def to_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


# Datos por defecto -------------------------------------------------------

def load_default_plan() -> HACCPPlan:
    """Construye un plan APPCC simplificado para Yeva."""

    steps: List[ProcessStep] = [
        ProcessStep(
            name="Recepción de materias primas",
            description="Control de proveedores, temperaturas y estado del envase.",
            schedule_start=time(6, 0),
            schedule_end=time(8, 0),
            hazards=[
                Hazard(
                    name="Contaminación microbiológica",
                    category="Biológico",
                    cause="Materia prima sin cadena de frío",
                    preventive_measures=[
                        "Homologación de proveedores",
                        "Solicitud de certificados sanitarios",
                        "Verificación de temperaturas a la recepción",
                    ],
                    critical_limits=[
                        CriticalLimit(parameter="Temperatura", max_value=4, unit="ºC"),
                    ],
                    monitoring=[
                        MonitoringAction(
                            description="Medir temperatura de cada lote con termómetro calibrado",
                            frequency="Cada recepción",
                            responsible="Operario de almacén",
                        )
                    ],
                    corrective_actions=[
                        CorrectiveAction(
                            description="Rechazar el lote y notificar a compras",
                            responsible="Jefe de almacén",
                        )
                    ],
                )
            ],
        ),
        ProcessStep(
            name="Cocción",
            description="Cocción al vacío controlada.",
            schedule_start=time(8, 30),
            schedule_end=time(10, 30),
            hazards=[
                Hazard(
                    name="Supervivencia de patógenos",
                    category="Biológico",
                    cause="Insuficiente temperatura de cocción",
                    preventive_measures=["Calibración diaria del termómetro"],
                    critical_limits=[
                        CriticalLimit(parameter="Temperatura del centro del producto", min_value=72, unit="ºC"),
                        CriticalLimit(parameter="Tiempo", min_value=2, unit="min"),
                    ],
                    monitoring=[
                        MonitoringAction(
                            description="Registrar temperatura final de cada lote",
                            frequency="Cada lote",
                            responsible="Responsable de cocina",
                        )
                    ],
                    corrective_actions=[
                        CorrectiveAction(
                            description="Prolongar cocción y volver a verificar",
                            responsible="Responsable de cocina",
                        ),
                        CorrectiveAction(
                            description="Retener lote dudoso y evaluar microbiológicamente",
                            responsible="Calidad",
                        ),
                    ],
                )
            ],
        ),
        ProcessStep(
            name="Enfriamiento rápido",
            description="Paso a abatidor y sellado",
            schedule_start=time(10, 30),
            schedule_end=time(11, 30),
            hazards=[
                Hazard(
                    name="Multiplicación de patógenos",
                    category="Biológico",
                    cause="Descenso de temperatura demasiado lento",
                    preventive_measures=["Mantenimiento preventivo del abatidor"],
                    critical_limits=[
                        CriticalLimit(parameter="Tiempo para bajar de 63ºC a 10ºC", max_value=120, unit="min"),
                    ],
                    monitoring=[
                        MonitoringAction(
                            description="Revisar gráfico de temperatura del abatidor",
                            frequency="Cada ciclo",
                            responsible="Operario de producción",
                        )
                    ],
                    corrective_actions=[
                        CorrectiveAction(
                            description="Separar las bandejas y reiniciar el ciclo",
                            responsible="Operario de producción",
                        )
                    ],
                )
            ],
        ),
        ProcessStep(
            name="Almacenamiento refrigerado",
            description="Cámaras a 2ºC, control de inventario FIFO",
            schedule_start=time(11, 30),
            schedule_end=time(17, 0),
            hazards=[
                Hazard(
                    name="Desarrollo de Listeria monocytogenes",
                    category="Biológico",
                    cause="Temperaturas inadecuadas durante el almacenamiento",
                    preventive_measures=["Alarmas de temperatura en cámara", "Registro diario"],
                    critical_limits=[
                        CriticalLimit(parameter="Temperatura de cámara", max_value=4, unit="ºC"),
                    ],
                    monitoring=[
                        MonitoringAction(
                            description="Verificar registro digital y firmar checklist",
                            frequency="Cada turno",
                            responsible="Responsable de almacén",
                        )
                    ],
                    corrective_actions=[
                        CorrectiveAction(
                            description="Trasladar producto a cámara auxiliar y avisar a mantenimiento",
                            responsible="Responsable de almacén",
                        )
                    ],
                )
            ],
        ),
    ]

    verification_records = [
        VerificationRecord(
            description="Revisión mensual de registros de PCC",
            frequency="Mensual",
            responsible="Calidad",
            evidence="Checklist de verificación",
        ),
        VerificationRecord(
            description="Auditoría interna del sistema APPCC",
            frequency="Trimestral",
            responsible="Dirección técnica",
            evidence="Informe firmado",
        ),
    ]

    documentation = [
        DocumentationRequirement(
            name="Plan APPCC firmado",
            location="SharePoint / Calidad / APPCC",
            retention_time="3 años",
        ),
        DocumentationRequirement(
            name="Registros de temperatura",
            location="Tablet de producción + backup en la nube",
            retention_time="12 meses",
        ),
    ]

    return HACCPPlan(
        team=["Yeva", "Responsable de Calidad", "Chef ejecutivo"],
        product_description="Platos preparados refrigerados listos para consumir",
        intended_use="Consumo tras un recalentamiento doméstico",
        process_steps=steps,
        verification_records=verification_records,
        documentation=documentation,
    )


def export_default_plan(path: Path) -> None:
    """Exporta el plan por defecto en formato JSON."""

    plan = load_default_plan()
    plan.to_json(path)

