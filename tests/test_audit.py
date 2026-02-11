from datetime import time
import unittest

from appcc_yeva.audit import audit_plan
from appcc_yeva.models import ProcessStep
from appcc_yeva.plan import HACCPPlan, load_default_plan


class AuditTests(unittest.TestCase):
    def test_default_plan_is_compliant(self) -> None:
        report = audit_plan(load_default_plan())
        self.assertTrue(report.is_compliant)
        self.assertEqual(0, len(report.errors))

    def test_detects_invalid_schedule(self) -> None:
        base = load_default_plan()
        broken_step = ProcessStep(
            name="Paso inválido",
            description="Horario incorrecto",
            schedule_start=time(12, 0),
            schedule_end=time(11, 0),
            hazards=[],
        )

        broken = HACCPPlan(
            team=base.team,
            product_description=base.product_description,
            intended_use=base.intended_use,
            process_steps=[broken_step],
            verification_records=base.verification_records,
            documentation=base.documentation,
        )

        report = audit_plan(broken)
        self.assertFalse(report.is_compliant)
        self.assertTrue(any(issue.code == "INVALID_STEP_SCHEDULE" for issue in report.issues))


if __name__ == "__main__":
    unittest.main()
