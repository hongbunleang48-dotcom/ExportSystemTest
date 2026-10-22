"""tests/test_engine.py

Unit tests for InferenceEngine.
Verifies:
1. Forward chaining deduction flow across cycles.
2. Conflict resolution based on risk priority (Emergency > Urgent > Moderate > Low > Inconclusive).
3. Fallback handling when zero rules fire.
4. Completeness and accuracy of audit trail.
"""

import pytest
from app.core.engine import InferenceEngine
from app.core.models import Priority, Rule, Deduction, WorkingMemory


class TestForwardChaining:
    """Verifies that intermediate facts are derived and trigger downstream clinical rules."""

    def test_forward_chaining_high_fever_and_persistent(self):
        """Inputting temperature 39.5°C and duration 4 days should trigger:
        Cycle 1: R_DERIVE_HIGH_FEVER asserts has_high_fever=True, has_fever=True
        Cycle 2: R_DERIVE_PERSISTENT_FEVER asserts persistent_fever=True
        Cycle 3: R_URG_PROLONGED_HIGH_FEVER fires with Priority.URGENT!
        """
        engine = InferenceEngine()
        facts = {
            "temperature": 39.5,
            "duration_days": 4,
            "cough_severity": "none",
            "respiratory_distress": "none",
        }
        result = engine.evaluate(facts)

        # Verify derived facts are present in working memory
        assert result.working_memory.is_true("has_high_fever")
        assert result.working_memory.is_true("has_fever")
        assert result.working_memory.is_true("persistent_fever")

        # Verify final deduction is Urgent Prolonged High Fever
        assert result.final_deduction.risk_level == Priority.URGENT
        assert "Prolonged High-Grade Pyrexia" in result.final_deduction.diagnosis

        # Verify audit trail contains intermediate rules firing
        fired_ids = [entry.rule_id for entry in result.audit_trail if entry.fired]
        assert "R_DERIVE_HIGH_FEVER" in fired_ids
        assert "R_DERIVE_PERSISTENT_FEVER" in fired_ids
        assert "R_URG_PROLONGED_HIGH_FEVER" in fired_ids

    def test_forward_chaining_hypoxia_triggers_emergency(self):
        """Inputting SpO2 88% should derive has_hypoxia=True in cycle 1,
        which then immediately satisfies R_EMERG_RESP_DISTRESS in cycle 2.
        """
        engine = InferenceEngine()
        facts = {
            "temperature": 36.8,
            "duration_days": 1,
            "cough_severity": "mild",
            "respiratory_distress": "none",
            "oxygen_saturation": 88.0,
        }
        result = engine.evaluate(facts)

        assert result.working_memory.is_true("has_hypoxia")
        assert result.final_deduction.risk_level == Priority.EMERGENCY
        assert "Critical Respiratory Distress" in result.final_deduction.diagnosis


class TestConflictResolution:
    """Verifies hierarchical resolution: Emergency > Urgent > Moderate > Low > Inconclusive."""

    def test_emergency_wins_over_urgent_and_moderate(self):
        """When symptoms qualify for Moderate (fever + cough),
        Urgent (pneumonia suspect), AND Emergency (severe respiratory distress),
        the engine must resolve to EMERGENCY.
        """
        engine = InferenceEngine()
        facts = {
            "temperature": 38.5,
            "duration_days": 4,
            "cough_severity": "severe",
            "respiratory_distress": "severe",  # EMERGENCY indicator!
        }
        result = engine.evaluate(facts)

        assert result.final_deduction.risk_level == Priority.EMERGENCY
        assert "Emergency" in result.conflict_resolution_notes
        # Check that multiple rules matched
        assert len(result.all_deductions) >= 1

    def test_urgent_wins_over_moderate(self):
        """Patient with fever and moderate cough lasting 4 days qualifies for:
        - R_MOD_PERSISTENT_FEVER (fever >= 3 days)
        - But with high fever (39.2°C), qualifies for R_URG_PROLONGED_HIGH_FEVER.
        Urgent should win.
        """
        engine = InferenceEngine()
        facts = {
            "temperature": 39.2,
            "duration_days": 4,
            "cough_severity": "moderate",
            "respiratory_distress": "none",
        }
        result = engine.evaluate(facts)

        assert result.final_deduction.risk_level == Priority.URGENT
        assert "Prolonged High-Grade Pyrexia" in result.final_deduction.diagnosis

    def test_custom_rule_priority_conflict(self):
        """Direct test with custom conflicting rules verifying mathematical Priority sorting."""
        rule_low = Rule(
            rule_id="R_CUSTOM_LOW",
            name="Low Custom",
            description="Low",
            condition=lambda m: True,
            deduction=Deduction(Priority.LOW, "Low Match", ["Rest"]),
            priority=Priority.LOW,
            weight=10,
        )
        rule_emerg = Rule(
            rule_id="R_CUSTOM_EMERG",
            name="Emerg Custom",
            description="Emergency",
            condition=lambda m: True,
            deduction=Deduction(Priority.EMERGENCY, "Emerg Match", ["Emergency"]),
            priority=Priority.EMERGENCY,
            weight=5,
        )
        rule_urgent = Rule(
            rule_id="R_CUSTOM_URGENT",
            name="Urgent Custom",
            description="Urgent",
            condition=lambda m: True,
            deduction=Deduction(Priority.URGENT, "Urgent Match", ["Urgent"]),
            priority=Priority.URGENT,
            weight=20,
        )

        engine = InferenceEngine(rules=[rule_low, rule_emerg, rule_urgent])
        result = engine.evaluate({"temperature": 37.0})

        assert result.final_deduction.risk_level == Priority.EMERGENCY
        assert result.final_deduction.diagnosis == "Emerg Match"
        assert "Conflict Resolution" in result.conflict_resolution_notes


class TestFallbackAndEdgeCases:
    """Verifies fallback when no rules fire and robustness under atypical inputs."""

    def test_fallback_when_zero_rules_match(self):
        """When an atypical input fires zero rules, engine falls back cleanly to Inconclusive."""
        # Empty rule base
        empty_engine = InferenceEngine(rules=[])
        result = empty_engine.evaluate({"temperature": 37.0})

        assert result.final_deduction.risk_level == Priority.INCONCLUSIVE
        assert "Inconclusive" in result.final_deduction.diagnosis
        assert len(result.matched_rules) == 0
        assert "Zero terminal triage rules matched" in result.conflict_resolution_notes

    def test_isolated_unclassified_symptom_fallback(self):
        """A borderline case that doesn't trigger standard cold or baseline (e.g. temp 37.8, no cough)."""
        engine = InferenceEngine()
        # 37.8°C is neither fever (< 38.0) nor baseline (36.0 - 37.5), no cough, no other symptoms
        facts = {
            "temperature": 37.8,
            "duration_days": 1,
            "cough_severity": "none",
            "respiratory_distress": "none",
        }
        result = engine.evaluate(facts)

        assert result.final_deduction.risk_level == Priority.INCONCLUSIVE
        assert result.final_deduction.risk_level.label == "Inconclusive"

    def test_audit_trail_integrity(self):
        """Verifies that audit trail contains both fired and unfired rule entries."""
        engine = InferenceEngine()
        facts = {
            "temperature": 41.0,  # Extreme hyperpyrexia
            "duration_days": 1,
            "cough_severity": "none",
            "respiratory_distress": "none",
        }
        result = engine.evaluate(facts)

        assert len(result.audit_trail) > 0
        fired_entries = [e for e in result.audit_trail if e.fired]
        unfired_entries = [e for e in result.audit_trail if not e.fired]

        assert len(fired_entries) >= 1
        assert len(unfired_entries) >= 1
        assert any(e.rule_id == "R_EMERG_HYPERPYREXIA" and e.fired for e in fired_entries)
        assert result.execution_time_ms >= 0.0

    def test_serialization(self):
        """Verifies to_dict serialization works cleanly for JSON export."""
        engine = InferenceEngine()
        result = engine.evaluate({"temperature": 36.6, "cough_severity": "none", "respiratory_distress": "none"})
        data = result.to_dict()

        assert "final_deduction" in data
        assert "working_memory" in data
        assert "audit_trail" in data
        assert "conflict_resolution_notes" in data
        assert "execution_time_ms" in data
        assert isinstance(data["audit_trail"], list)
