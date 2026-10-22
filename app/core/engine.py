"""app/core/engine.py

Inference Engine for Clinical Expert System.
Implements:
1. Forward-chaining evaluation over working memory.
2. Conflict resolution using hierarchical risk priority:
   Emergency > Urgent > Moderate > Low > Inconclusive.
3. Complete explainability with an audit trail of rule evaluations.
4. Robust fallback handling for inconclusive presentations.
5. Full bilingual English and Khmer reason traces and notes.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from app.core.models import (
    AuditEntry,
    Deduction,
    InferenceResult,
    Priority,
    Rule,
    WorkingMemory,
)
from app.core.rules import get_knowledge_base


class InferenceEngine:
    """Forward-chaining Rule-Based Inference Engine with Conflict Resolution."""

    def __init__(
        self,
        rules: Optional[List[Rule]] = None,
        max_cycles: int = 10,
    ):
        """Initializes the inference engine with a rule base.
        
        Args:
            rules: List of Rule objects. If None, default clinical rules are loaded.
            max_cycles: Maximum forward-chaining deduction cycles before loop termination.
        """
        self.rules: List[Rule] = rules if rules is not None else get_knowledge_base()
        self.max_cycles = max_cycles

    @staticmethod
    def _normalize_facts(raw_facts: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes and type-casts input facts for consistent rule evaluation."""
        normalized: Dict[str, Any] = {}
        for k, v in raw_facts.items():
            normalized[k] = v

        # Parse temperature
        if "temperature" in normalized and normalized["temperature"] not in (None, ""):
            try:
                normalized["temperature"] = float(normalized["temperature"])
            except (ValueError, TypeError):
                normalized["temperature"] = 37.0
        else:
            normalized["temperature"] = 37.0

        # Parse duration_days
        if "duration_days" in normalized and normalized["duration_days"] not in (None, ""):
            try:
                normalized["duration_days"] = int(normalized["duration_days"])
            except (ValueError, TypeError):
                normalized["duration_days"] = 1
        else:
            normalized["duration_days"] = 1

        # Parse oxygen_saturation
        if "oxygen_saturation" in normalized and normalized["oxygen_saturation"] not in (None, ""):
            try:
                normalized["oxygen_saturation"] = float(normalized["oxygen_saturation"])
            except (ValueError, TypeError):
                normalized["oxygen_saturation"] = None
        else:
            normalized["oxygen_saturation"] = None

        # Parse string fields
        for field in ["cough_severity", "respiratory_distress"]:
            if field in normalized and normalized[field] is not None:
                normalized[field] = str(normalized[field]).strip().lower()
            else:
                normalized[field] = "none"

        # Parse boolean fields
        for b_field in ["chest_pain", "lethargy_confusion", "high_risk_condition"]:
            val = normalized.get(b_field)
            if isinstance(val, str):
                normalized[b_field] = val.strip().lower() in ["true", "1", "yes", "on"]
            else:
                normalized[b_field] = bool(val)

        return normalized

    def evaluate(self, raw_facts: Dict[str, Any]) -> InferenceResult:
        """Executes forward-chaining inference over the provided facts.
        
        Returns:
            InferenceResult containing final deduction, audit trail, and resolution notes.
        """
        start_time = time.perf_counter()

        # Step 1: Initialize Working Memory with normalized input facts
        clean_facts = self._normalize_facts(raw_facts)
        working_memory = WorkingMemory(clean_facts)

        fired_rule_ids: set[str] = set()
        matched_rules: List[Rule] = []
        all_deductions: List[Deduction] = []
        audit_trail: List[AuditEntry] = []

        # Step 2: Forward-Chaining Deduction Cycles
        for cycle in range(1, self.max_cycles + 1):
            new_rule_fired_in_cycle = False

            for rule in self.rules:
                if rule.rule_id in fired_rule_ids:
                    continue  # Already fired in a previous cycle

                passed, reason = rule.evaluate(working_memory)

                if passed:
                    fired_rule_ids.add(rule.rule_id)
                    matched_rules.append(rule)
                    new_rule_fired_in_cycle = True

                    # Assert derived facts into working memory
                    asserted_facts: Dict[str, Any] = {}
                    if rule.deduction.new_facts:
                        for f_name, f_val in rule.deduction.new_facts.items():
                            working_memory.set_fact(
                                name=f_name,
                                value=f_val,
                                source="derived",
                                description=f"Derived by {rule.rule_id} in cycle {cycle}",
                            )
                            asserted_facts[f_name] = f_val

                    # If this rule provides a clinical diagnosis/triage recommendation
                    if not rule.is_intermediate:
                        all_deductions.append(rule.deduction)

                    # Log successful audit entry (bilingual)
                    audit_trail.append(
                        AuditEntry(
                            rule_id=rule.rule_id,
                            rule_name=rule.name,
                            rule_name_km=rule.name_km,
                            priority=rule.priority.name,
                            priority_value=int(rule.priority),
                            evaluated=True,
                            fired=True,
                            condition_repr=rule.condition_repr,
                            reason=f"[Cycle {cycle}] FIRED: {reason}",
                            reason_km=f"[វដ្ត {cycle}] បានដំណើរការ៖ {rule.name_km or reason}",
                            asserted_facts=asserted_facts,
                            diagnosis=rule.deduction.diagnosis,
                            diagnosis_km=rule.deduction.diagnosis_km,
                        )
                    )
                else:
                    # Log failed condition audit entry (only in cycle 1)
                    if cycle == 1:
                        audit_trail.append(
                            AuditEntry(
                                rule_id=rule.rule_id,
                                rule_name=rule.name,
                                rule_name_km=rule.name_km,
                                priority=rule.priority.name,
                                priority_value=int(rule.priority),
                                evaluated=True,
                                fired=False,
                                condition_repr=rule.condition_repr,
                                reason=f"[Cycle {cycle}] Condition not met: {reason}",
                                reason_km=f"[វដ្ត {cycle}] លក្ខខណ្ឌមិនត្រូវគ្នា៖ {rule.name_km or reason}",
                                asserted_facts={},
                                diagnosis=None,
                                diagnosis_km=None,
                            )
                        )

            # If no new rules fired in this cycle, working memory has stabilized
            if not new_rule_fired_in_cycle:
                break

        # Step 3: Conflict Resolution
        # Clinical Risk Priority Hierarchy: Emergency (5) > Urgent (4) > Moderate (3) > Low (2) > Inconclusive (1)
        terminal_rules = [r for r in matched_rules if not r.is_intermediate]

        if not terminal_rules:
            # Fallback when zero clinical triage rules match
            final_deduction = Deduction(
                risk_level=Priority.INCONCLUSIVE,
                diagnosis="Inconclusive Clinical Presentation",
                diagnosis_km="រោគវិនិច្ឆ័យមិនទាន់ច្បាស់លាស់",
                action_advice=[
                    "The combination of symptoms does not match high-probability diagnostic patterns.",
                    "If symptoms persist beyond 48 hours or worsen, consult a healthcare provider.",
                    "Seek prompt care immediately if red-flag signs (severe shortness of breath, confusion, high persistent fever) emerge.",
                ],
                action_advice_km=[
                    "ការរួមបញ្ចូលគ្នានៃរោគសញ្ញាមិនត្រូវគ្នានឹងគំរូរោគវិនិច្ឆ័យជាក់លាក់ណាមួយឡើយ។",
                    "ប្រសិនបើរោគសញ្ញាបន្តលើសពី ៤៨ ម៉ោង ឬកាន់តែធ្ងន់ធ្ងរ សូមពិគ្រោះជាមួយគ្រូពេទ្យ។",
                    "សូមស្វែងរកការសង្គ្រោះបន្ទាន់ភ្លាមៗ ប្រសិនបើលេចចេញសញ្ញាអាសន្ន (ពិបាកដកដង្ហើមខ្លាំង វង្វេងស្មារតី ក្តៅខ្លួនខ្លាំងជាប់រហូត)។",
                ],
                is_terminal=True,
            )
            conflict_notes = (
                "Zero terminal triage rules matched the submitted facts. "
                "Defaulting to INCONCLUSIVE triage classification with clinical safety guidance."
            )
            conflict_notes_km = (
                "គ្មានវិធានតម្រៀបអ្នកជំងឺណាមួយត្រូវគ្នានឹងអង្គហេតុដែលបានបញ្ចូលឡើយ។ "
                "កំណត់ទៅជាកម្រិតមិនទាន់ច្បាស់លាស់ (INCONCLUSIVE) ជាមួយនឹងការណែនាំសុវត្ថិភាពវេជ្ជសាស្ត្រ។"
            )
        else:
            # Sort terminal rules: Highest Priority first, then highest weight
            terminal_rules.sort(
                key=lambda r: (int(r.priority), r.weight),
                reverse=True,
            )
            winning_rule = terminal_rules[0]
            final_deduction = winning_rule.deduction

            if len(terminal_rules) == 1:
                conflict_notes = (
                    f"Single triage rule '{winning_rule.rule_id}' ({winning_rule.priority.label}) "
                    f"fired without conflict."
                )
                conflict_notes_km = (
                    f"វិធានតែមួយ '{winning_rule.rule_id}' ({winning_rule.priority.get_label('km')}) "
                    f"ត្រូវបានដំណើរការដោយគ្មានវិវាទ។"
                )
            else:
                other_rules_summary = ", ".join(
                    f"{r.rule_id} [{r.priority.label}]" for r in terminal_rules[1:]
                )
                other_rules_summary_km = ", ".join(
                    f"{r.rule_id} [{r.priority.get_label('km')}]" for r in terminal_rules[1:]
                )
                conflict_notes = (
                    f"Conflict Resolution: {len(terminal_rules)} competing rules fired. "
                    f"Selected highest-priority rule '{winning_rule.rule_id}' ({winning_rule.priority.label}) "
                    f"over lower-priority candidates ({other_rules_summary}) "
                    f"in adherence to clinical triage safety protocols."
                )
                conflict_notes_km = (
                    f"ការដោះស្រាយវិវាទ៖ មានវិធានប្រកួតប្រជែងចំនួន {len(terminal_rules)} បានដំណើរការ។ "
                    f"បានជ្រើសរើសវិធានដែលមានអាទិភាពខ្ពស់បំផុត '{winning_rule.rule_id}' ({winning_rule.priority.get_label('km')}) "
                    f"លើវិធានដែលមានអាទិភាពទាបជាង ({other_rules_summary_km}) "
                    f"ស្របតាមពិធីសារសុវត្ថិភាពតម្រៀបអ្នកជំងឺព្យាបាល។"
                )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        return InferenceResult(
            final_deduction=final_deduction,
            matched_rules=matched_rules,
            all_deductions=all_deductions,
            working_memory=working_memory,
            audit_trail=audit_trail,
            conflict_resolution_notes=conflict_notes,
            conflict_resolution_notes_km=conflict_notes_km,
            execution_time_ms=elapsed_ms,
        )
