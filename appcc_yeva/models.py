"""Modelos de dominio para describir un plan APPCC."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from typing import List, Optional


@dataclass
class CriticalLimit:
    """Define los límites críticos medibles para un peligro."""

    parameter: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None

    def describe(self) -> str:
        parts = [self.parameter]
        if self.min_value is not None:
            parts.append(f">= {self.min_value}{self.unit or ''}")
        if self.max_value is not None:
            parts.append(f"<= {self.max_value}{self.unit or ''}")
        return " ".join(parts)


@dataclass
class MonitoringAction:
    """Actividad que verifica un límite crítico."""

    description: str
    frequency: str
    responsible: str


@dataclass
class CorrectiveAction:
    """Acción que debe tomarse cuando un límite crítico se incumple."""

    description: str
    responsible: str


@dataclass
class Hazard:
    """Peligro identificado en el proceso."""

    name: str
    category: str
    cause: str
    preventive_measures: List[str] = field(default_factory=list)
    critical_limits: List[CriticalLimit] = field(default_factory=list)
    monitoring: List[MonitoringAction] = field(default_factory=list)
    corrective_actions: List[CorrectiveAction] = field(default_factory=list)


@dataclass
class ProcessStep:
    """Paso del proceso productivo."""

    name: str
    description: str
    schedule_start: Optional[time] = None
    schedule_end: Optional[time] = None
    hazards: List[Hazard] = field(default_factory=list)

    def is_critical(self) -> bool:
        return any(h.critical_limits for h in self.hazards)


@dataclass
class VerificationRecord:
    """Registros de verificación del plan."""

    description: str
    frequency: str
    responsible: str
    evidence: str


@dataclass
class DocumentationRequirement:
    """Requisito documental asociado al plan."""

    name: str
    location: str
    retention_time: str

