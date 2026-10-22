"""tests/test_rules.py

Unit tests verifying isolated rule logic, conditions, and boundary values.
Tests edge cases (e.g. 38.9°C vs 39.0°C, 37.9°C vs 38.0°C, duration 2 vs 3 days, SpO2 92% vs 91%).
"""

import pytest
from app.core.models import Priority, WorkingMemory
from app.core.rules import get_knowledge_base


@pytest.fixture
def rule_map():
    """Returns a dictionary of all rules indexed by rule_id."""
    rules = get_knowledge_base()
    return {r.rule_id: r for r in rules}


class TestIntermediateRules:
    """Verifies boundary values and logic for Stage 1 intermediate derivation rules."""

    def test_high_fever_boundary(self, rule_map):
        rule = rule_map["R_DERIVE_HIGH_FEVER"]

        # Below boundary: 38.9°C -> False
        mem_below = WorkingMemory({"temperature": 38.9})
        passed, _ = rule.evaluate(mem_below)
        assert passed is False

        # Exact boundary: 39.0°C -> True
        mem_exact = WorkingMemory({"temperature": 39.0})
        passed, _ = rule.evaluate(mem_exact)
        assert passed is True
        assert rule.deduction.new_facts == {"has_high_fever": True, "has_fever": True}

        # Above boundary: 39.8°C -> True
        mem_above = WorkingMemory({"temperature": 39.8})
        passed, _ = rule.evaluate(mem_above)
        assert passed is True

    def test_standard_fever_boundary(self, rule_map):
        rule = rule_map["R_DERIVE_STANDARD_FEVER"]

        # Below boundary: 37.9°C -> False
        mem_below = WorkingMemory({"temperature": 37.9})
        passed, _ = rule.evaluate(mem_below)
        assert passed is False

        # Exact lower boundary: 38.0°C -> True
        mem_exact = WorkingMemory({"temperature": 38.0})
        passed, _ = rule.evaluate(mem_exact)
        assert passed is True
        assert rule.deduction.new_facts["has_fever"] is True

        # Upper boundary: 38.99°C -> True
        mem_mid = WorkingMemory({"temperature": 38.9})
        passed, _ = rule.evaluate(mem_mid)
        assert passed is True

        # At/above 39.0°C -> False (this rule only handles standard fever)
        mem_high = WorkingMemory({"temperature": 39.0})
        passed, _ = rule.evaluate(mem_high)
        assert passed is False

    def test_hypoxia_boundary(self, rule_map):
        rule = rule_map["R_DERIVE_HYPOXIA"]

        # Normal SpO2: 95% -> False
        mem_normal = WorkingMemory({"oxygen_saturation": 95.0})
        passed, _ = rule.evaluate(mem_normal)
        assert passed is False

        # Boundary: 92% -> False (condition is < 92)
        mem_boundary = WorkingMemory({"oxygen_saturation": 92.0})
        passed, _ = rule.evaluate(mem_boundary)
        assert passed is False

        # Hypoxic: 91.9% -> True
        mem_hypoxic = WorkingMemory({"oxygen_saturation": 91.9})
        passed, _ = rule.evaluate(mem_hypoxic)
        assert passed is True
        assert rule.deduction.new_facts == {"has_hypoxia": True}

        # Missing SpO2 -> False
        mem_none = WorkingMemory({})
        passed, _ = rule.evaluate(mem_none)
        assert passed is False

    def test_persistent_fever_boundary(self, rule_map):
        rule = rule_map["R_DERIVE_PERSISTENT_FEVER"]

        # Fever present, duration 2 days -> False
        mem_2days = WorkingMemory({"has_fever": True, "duration_days": 2})
        passed, _ = rule.evaluate(mem_2days)
        assert passed is False

        # Fever present, duration 3 days -> True
        mem_3days = WorkingMemory({"has_fever": True, "duration_days": 3})
        passed, _ = rule.evaluate(mem_3days)
        assert passed is True

        # No fever, duration 5 days -> False
        mem_no_fever = WorkingMemory({"has_fever": False, "duration_days": 5})
        passed, _ = rule.evaluate(mem_no_fever)
        assert passed is False

    def test_prolonged_illness_boundary(self, rule_map):
        rule = rule_map["R_DERIVE_PROLONGED_ILLNESS"]

        # Duration 6 days -> False
        mem_6 = WorkingMemory({"duration_days": 6})
        passed, _ = rule.evaluate(mem_6)
        assert passed is False

        # Duration 7 days -> True
        mem_7 = WorkingMemory({"duration_days": 7})
        passed, _ = rule.evaluate(mem_7)
        assert passed is True


class TestEmergencyRules:
    """Verifies condition logic for all Emergency priority rules."""

    def test_emergency_respiratory_distress(self, rule_map):
        rule = rule_map["R_EMERG_RESP_DISTRESS"]
        assert rule.priority == Priority.EMERGENCY

        # Positive: severe distress
        mem_severe = WorkingMemory({"respiratory_distress": "severe"})
        passed, _ = rule.evaluate(mem_severe)
        assert passed is True

        # Positive: has_hypoxia flag
        mem_hypox = WorkingMemory({"has_hypoxia": True, "respiratory_distress": "none"})
        passed, _ = rule.evaluate(mem_hypox)
        assert passed is True

        # Negative: moderate or mild distress without hypoxia
        mem_mod = WorkingMemory({"respiratory_distress": "moderate", "has_hypoxia": False})
        passed, _ = rule.evaluate(mem_mod)
        assert passed is False

    def test_emergency_hyperpyrexia_boundary(self, rule_map):
        rule = rule_map["R_EMERG_HYPERPYREXIA"]
        assert rule.priority == Priority.EMERGENCY

        # Below boundary: 40.4°C -> False
        mem_below = WorkingMemory({"temperature": 40.4})
        passed, _ = rule.evaluate(mem_below)
        assert passed is False

        # Exact boundary: 40.5°C -> True
        mem_exact = WorkingMemory({"temperature": 40.5})
        passed, _ = rule.evaluate(mem_exact)
        assert passed is True

    def test_emergency_sepsis_alert(self, rule_map):
        rule = rule_map["R_EMERG_SEPSIS_ALERT"]

        # High fever + lethargy -> True
        mem_pos1 = WorkingMemory({"has_high_fever": True, "lethargy_confusion": True})
        passed, _ = rule.evaluate(mem_pos1)
        assert passed is True

        # Hypothermia (temp < 35.5) + lethargy -> True
        mem_pos2 = WorkingMemory({"temperature": 35.0, "lethargy_confusion": True})
        passed, _ = rule.evaluate(mem_pos2)
        assert passed is True

        # High fever alone without lethargy -> False
        mem_no_lethargy = WorkingMemory({"has_high_fever": True, "lethargy_confusion": False})
        passed, _ = rule.evaluate(mem_no_lethargy)
        assert passed is False

        # Lethargy with normal temperature -> False
        mem_norm_temp = WorkingMemory({"temperature": 36.8, "lethargy_confusion": True})
        passed, _ = rule.evaluate(mem_norm_temp)
        assert passed is False

    def test_emergency_cardiopulmonary(self, rule_map):
        rule = rule_map["R_EMERG_CARDIOPULMONARY"]

        # Chest pain + moderate distress -> True
        mem_pos = WorkingMemory({"chest_pain": True, "respiratory_distress": "moderate"})
        passed, _ = rule.evaluate(mem_pos)
        assert passed is True

        # Chest pain + high fever -> True
        mem_pos2 = WorkingMemory({"chest_pain": True, "has_high_fever": True})
        passed, _ = rule.evaluate(mem_pos2)
        assert passed is True

        # Chest pain alone with no distress or high fever -> False
        mem_pain_only = WorkingMemory({"chest_pain": True, "respiratory_distress": "none"})
        passed, _ = rule.evaluate(mem_pain_only)
        assert passed is False


class TestUrgentRules:
    """Verifies condition logic for Urgent priority rules."""

    def test_urgent_prolonged_high_fever(self, rule_map):
        rule = rule_map["R_URG_PROLONGED_HIGH_FEVER"]
        assert rule.priority == Priority.URGENT

        # Both flags true -> True
        mem_pos = WorkingMemory({"has_high_fever": True, "persistent_fever": True})
        passed, _ = rule.evaluate(mem_pos)
        assert passed is True

        # Only persistent fever (not high fever) -> False
        mem_neg = WorkingMemory({"has_high_fever": False, "persistent_fever": True})
        passed, _ = rule.evaluate(mem_neg)
        assert passed is False

    def test_urgent_pneumonia_suspect(self, rule_map):
        rule = rule_map["R_URG_PNEUMONIA_SUSPECT"]

        # Fever + moderate cough + mild respiratory distress -> True
        mem_pos = WorkingMemory({
            "has_fever": True,
            "cough_severity": "moderate",
            "respiratory_distress": "mild",
        })
        passed, _ = rule.evaluate(mem_pos)
        assert passed is True

        # No fever -> False
        mem_no_fever = WorkingMemory({
            "has_fever": False,
            "cough_severity": "moderate",
            "respiratory_distress": "mild",
        })
        passed, _ = rule.evaluate(mem_no_fever)
        assert passed is False

    def test_urgent_high_risk_febrile(self, rule_map):
        rule = rule_map["R_URG_HIGH_RISK_FEBRILE"]

        mem_pos = WorkingMemory({"has_fever": True, "high_risk_condition": True})
        passed, _ = rule.evaluate(mem_pos)
        assert passed is True

        mem_neg = WorkingMemory({"has_fever": True, "high_risk_condition": False})
        passed, _ = rule.evaluate(mem_neg)
        assert passed is False


class TestModerateAndLowRules:
    """Verifies Moderate and Low priority rules."""

    def test_moderate_persistent_fever(self, rule_map):
        rule = rule_map["R_MOD_PERSISTENT_FEVER"]
        assert rule.priority == Priority.MODERATE

        # Fever + duration 3 + not high fever -> True
        mem_pos = WorkingMemory({
            "has_fever": True,
            "duration_days": 3,
            "has_high_fever": False,
        })
        passed, _ = rule.evaluate(mem_pos)
        assert passed is True

        # If has_high_fever is True, this rule defers to Urgent -> False
        mem_high = WorkingMemory({
            "has_fever": True,
            "duration_days": 3,
            "has_high_fever": True,
        })
        passed, _ = rule.evaluate(mem_high)
        assert passed is False

    def test_low_mild_cold(self, rule_map):
        rule = rule_map["R_LOW_MILD_COLD"]
        assert rule.priority == Priority.LOW

        mem_pos = WorkingMemory({
            "cough_severity": "mild",
            "has_fever": False,
            "has_high_fever": False,
            "duration_days": 2,
            "respiratory_distress": "none",
        })
        passed, _ = rule.evaluate(mem_pos)
        assert passed is True

        # Fever present -> False
        mem_with_fever = WorkingMemory({
            "cough_severity": "mild",
            "has_fever": True,
            "duration_days": 2,
            "respiratory_distress": "none",
        })
        passed, _ = rule.evaluate(mem_with_fever)
        assert passed is False

    def test_low_healthy_baseline(self, rule_map):
        rule = rule_map["R_LOW_HEALTHY_BASELINE"]
        assert rule.priority == Priority.LOW

        mem_healthy = WorkingMemory({
            "cough_severity": "none",
            "respiratory_distress": "none",
            "has_fever": False,
            "has_high_fever": False,
            "chest_pain": False,
            "lethargy_confusion": False,
            "temperature": 36.6,
        })
        passed, _ = rule.evaluate(mem_healthy)
        assert passed is True
