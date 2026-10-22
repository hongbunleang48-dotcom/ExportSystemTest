"""app/core package

Exports the core inference engine, models, knowledge base rules, and i18n helpers.
"""

from app.core.models import (
    AuditEntry,
    Deduction,
    Fact,
    InferenceResult,
    Priority,
    Rule,
    WorkingMemory,
)
from app.core.rules import get_knowledge_base
from app.core.engine import InferenceEngine
from app.core.i18n import SUPPORTED_LOCALES, DEFAULT_LOCALE, get_text

__all__ = [
    "AuditEntry",
    "Deduction",
    "Fact",
    "InferenceEngine",
    "InferenceResult",
    "Priority",
    "Rule",
    "WorkingMemory",
    "get_knowledge_base",
    "SUPPORTED_LOCALES",
    "DEFAULT_LOCALE",
    "get_text",
]
