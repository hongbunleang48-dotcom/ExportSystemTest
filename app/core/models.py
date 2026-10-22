"""app/core/models.py

Domain models and data structures for the Medical Expert System.
Defines Fact, WorkingMemory, Priority, Deduction, Rule, AuditEntry, and InferenceResult.
Supports bilingual rendering (English 'en' and Khmer 'km').
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Callable, Dict, List, Optional, Tuple


class Priority(IntEnum):
    """Clinical risk priority levels ordered hierarchically.
    
    Higher integer values represent higher urgency in conflict resolution.
    EMERGENCY (5) > URGENT (4) > MODERATE (3) > LOW (2) > INCONCLUSIVE (1)
    """
    INCONCLUSIVE = 1
    LOW = 2
    MODERATE = 3
    URGENT = 4
    EMERGENCY = 5

    @property
    def label(self) -> str:
        labels = {
            Priority.EMERGENCY: "Emergency",
            Priority.URGENT: "Urgent",
            Priority.MODERATE: "Moderate",
            Priority.LOW: "Low",
            Priority.INCONCLUSIVE: "Inconclusive",
        }
        return labels.get(self, self.name)

    def get_label(self, locale: str = "en") -> str:
        """Returns localized priority label for English or Khmer."""
        if locale == "km":
            labels_km = {
                Priority.EMERGENCY: "សង្គ្រោះបន្ទាន់",
                Priority.URGENT: "បន្ទាន់ខ្លាំង",
                Priority.MODERATE: "មធ្យម",
                Priority.LOW: "ទាប",
                Priority.INCONCLUSIVE: "មិនទាន់ច្បាស់លាស់",
            }
            return labels_km.get(self, self.label)
        return self.label

    @property
    def badge_class(self) -> str:
        """CSS badge class for UI styling."""
        badge_map = {
            Priority.EMERGENCY: "badge-emergency",
            Priority.URGENT: "badge-urgent",
            Priority.MODERATE: "badge-moderate",
            Priority.LOW: "badge-low",
            Priority.INCONCLUSIVE: "badge-inconclusive",
        }
        return badge_map.get(self, "badge-secondary")

    @property
    def hex_color(self) -> str:
        color_map = {
            Priority.EMERGENCY: "#DC2626",   # Red
            Priority.URGENT: "#EA580C",      # Orange
            Priority.MODERATE: "#D97706",    # Amber/Yellow
            Priority.LOW: "#059669",         # Emerald Green
            Priority.INCONCLUSIVE: "#4B5563" # Slate Gray
        }
        return color_map.get(self, "#6B7280")


@dataclass
class Fact:
    """Represents an atomic piece of knowledge or patient observation in working memory."""
    name: str
    value: Any
    source: str = "input"  # 'input', 'derived', or 'system'
    description: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "value": self.value,
            "source": self.source,
            "description": self.description,
            "created_at": self.created_at,
        }


class WorkingMemory:
    """Knowledge store holding current facts during an inference session."""

    def __init__(self, initial_facts: Optional[Dict[str, Any]] = None):
        self._facts: Dict[str, Fact] = {}
        if initial_facts:
            for key, val in initial_facts.items():
                self.set_fact(key, val, source="input")

    def set_fact(
        self,
        name: str,
        value: Any,
        source: str = "input",
        description: Optional[str] = None,
    ) -> Fact:
        fact = Fact(name=name, value=value, source=source, description=description)
        self._facts[name] = fact
        return fact

    def get_fact(self, name: str) -> Optional[Fact]:
        return self._facts.get(name)

    def get(self, name: str, default: Any = None) -> Any:
        fact = self._facts.get(name)
        return fact.value if fact is not None else default

    def has(self, name: str) -> bool:
        return name in self._facts

    def is_true(self, name: str) -> bool:
        return bool(self.get(name, False))

    def all_facts(self) -> Dict[str, Fact]:
        return self._facts.copy()

    def to_dict(self) -> Dict[str, Any]:
        return {k: f.to_dict() for k, f in self._facts.items()}

    def values_dict(self) -> Dict[str, Any]:
        return {k: f.value for k, f in self._facts.items()}

    def __repr__(self) -> str:
        return f"WorkingMemory({list(self._facts.keys())})"


@dataclass
class Deduction:
    """Payload produced when a rule fires, including clinical diagnosis and action advice.
    
    Supports bilingual English and Khmer text.
    """
    risk_level: Priority
    diagnosis: str
    action_advice: List[str]
    diagnosis_km: str = ""
    action_advice_km: List[str] = field(default_factory=list)
    new_facts: Dict[str, Any] = field(default_factory=dict)
    is_terminal: bool = True  # If False, rule acts as intermediate fact derivation

    def get_diagnosis(self, locale: str = "en") -> str:
        """Returns diagnosis in requested locale (defaults to English)."""
        if locale == "km" and self.diagnosis_km:
            return self.diagnosis_km
        return self.diagnosis

    def get_action_advice(self, locale: str = "en") -> List[str]:
        """Returns action advice list in requested locale."""
        if locale == "km" and self.action_advice_km:
            return self.action_advice_km
        return self.action_advice

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_level": self.risk_level.name,
            "risk_level_value": int(self.risk_level),
            "risk_label": self.risk_level.label,
            "diagnosis": self.diagnosis,
            "diagnosis_km": self.diagnosis_km,
            "action_advice": self.action_advice,
            "action_advice_km": self.action_advice_km,
            "new_facts": self.new_facts,
            "is_terminal": self.is_terminal,
        }


@dataclass
class Rule:
    """Formal IF-THEN production rule with clinical conditions and deductions.
    
    Supports bilingual titles and descriptions.
    """
    rule_id: str
    name: str
    description: str
    condition: Callable[[WorkingMemory], bool]
    deduction: Deduction
    priority: Priority
    weight: int = 0
    condition_repr: str = ""
    is_intermediate: bool = False
    name_km: str = ""
    description_km: str = ""

    def get_name(self, locale: str = "en") -> str:
        if locale == "km" and self.name_km:
            return self.name_km
        return self.name

    def get_description(self, locale: str = "en") -> str:
        if locale == "km" and self.description_km:
            return self.description_km
        return self.description

    def evaluate(self, memory: WorkingMemory) -> Tuple[bool, str]:
        """Evaluates the rule against the current working memory state.
        
        Returns:
            Tuple of (condition_passed: bool, rationale: str)
        """
        try:
            passed = bool(self.condition(memory))
            if passed:
                rationale = f"Rule '{self.rule_id}' satisfied condition: {self.condition_repr or self.description}"
            else:
                rationale = f"Rule '{self.rule_id}' condition not met."
            return passed, rationale
        except Exception as exc:
            return False, f"Rule '{self.rule_id}' evaluation error: {str(exc)}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "name_km": self.name_km,
            "description": self.description,
            "description_km": self.description_km,
            "priority": self.priority.name,
            "weight": self.weight,
            "condition_repr": self.condition_repr,
            "is_intermediate": self.is_intermediate,
            "deduction": self.deduction.to_dict(),
        }


@dataclass
class AuditEntry:
    """Detailed audit trace record for explainable AI reasoning with bilingual support."""
    rule_id: str
    rule_name: str
    priority: str
    priority_value: int
    evaluated: bool
    fired: bool
    condition_repr: str
    reason: str
    asserted_facts: Dict[str, Any]
    diagnosis: Optional[str] = None
    rule_name_km: str = ""
    reason_km: str = ""
    diagnosis_km: Optional[str] = None
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

    def get_rule_name(self, locale: str = "en") -> str:
        if locale == "km" and self.rule_name_km:
            return self.rule_name_km
        return self.rule_name

    def get_reason(self, locale: str = "en") -> str:
        if locale == "km" and self.reason_km:
            return self.reason_km
        return self.reason

    def get_diagnosis(self, locale: str = "en") -> Optional[str]:
        if locale == "km" and self.diagnosis_km:
            return self.diagnosis_km
        return self.diagnosis

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_name_km": self.rule_name_km,
            "priority": self.priority,
            "priority_value": self.priority_value,
            "evaluated": self.evaluated,
            "fired": self.fired,
            "condition_repr": self.condition_repr,
            "reason": self.reason,
            "reason_km": self.reason_km,
            "asserted_facts": self.asserted_facts,
            "diagnosis": self.diagnosis,
            "diagnosis_km": self.diagnosis_km,
            "timestamp": self.timestamp,
        }


@dataclass
class InferenceResult:
    """Comprehensive output of an inference session with bilingual support."""
    final_deduction: Deduction
    matched_rules: List[Rule]
    all_deductions: List[Deduction]
    working_memory: WorkingMemory
    audit_trail: List[AuditEntry]
    conflict_resolution_notes: str
    execution_time_ms: float
    conflict_resolution_notes_km: str = ""

    def get_conflict_resolution_notes(self, locale: str = "en") -> str:
        if locale == "km" and self.conflict_resolution_notes_km:
            return self.conflict_resolution_notes_km
        return self.conflict_resolution_notes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "final_deduction": self.final_deduction.to_dict(),
            "matched_rules_count": len(self.matched_rules),
            "matched_rule_ids": [r.rule_id for r in self.matched_rules],
            "working_memory": self.working_memory.to_dict(),
            "audit_trail": [entry.to_dict() for entry in self.audit_trail],
            "conflict_resolution_notes": self.conflict_resolution_notes,
            "conflict_resolution_notes_km": self.conflict_resolution_notes_km,
            "execution_time_ms": self.execution_time_ms,
        }
