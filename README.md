# Clinical Triage Advisor - Modular Flask Expert System

A production-grade, modular Rule-Based Expert System implemented in Python and Flask using Clean Architecture principles. The system functions as a **Clinical Triage Advisor**, evaluating acute respiratory and febrile presentations (e.g. fever, cough severity, respiratory distress, duration, and pulse oximetry) to provide rapid clinical risk stratification, actionable directives, and full explainability.

> 📖 **Comprehensive Technical Documentation:** For an in-depth architectural breakdown, machine-learning vs expert system paradigms, forward-chaining mechanics, and auditability specs, see [**`DOCUMENTATION.md`**](file:///D:/HongBunleang/1_Norton/year3/Term1/4ExpertSystemDevelopment/ExportsystemTest/DOCUMENTATION.md).

---

## 🌐 Bilingual Support (English & Khmer)

The application features a lightweight, pure-Python internationalization engine ([`app/core/i18n.py`](file:///D:/HongBunleang/1_Norton/year3/Term1/4ExpertSystemDevelopment/ExportsystemTest/app/core/i18n.py)) with **zero external dependencies**:
- **Switch Languages Seamlessly**: Toggle between **`🇺🇸 English`** and **`🇰🇭 ភាសាខ្មែរ`** via the top-right button or `/lang/<locale>`.
- **Full Translation**: UI labels, clinical recommendations, triage priority badges, and audit trails are completely localized.
- **Typography**: Optimized typography with Google Font `Kantumruy Pro` for clear, accessible Khmer script.

---

## 🏗️ Project Architecture & Directory Layout

```
expert_system_flask/
├── .gitignore                      # Git ignore patterns for Python, venv, and pytest
├── README.md                       # Quickstart summary & project overview
├── DOCUMENTATION.md                # Comprehensive architectural and technical specification
├── requirements.txt                # Python package dependencies
├── run.py                          # Application entry point
├── config.py                       # Modular environment configs (Dev, Test, Prod)
├── app/
│   ├── __init__.py                 # Flask Application Factory pattern (create_app & i18n processor)
│   ├── routes.py                   # Web UI routes (GET/POST /), /lang/<locale>, and REST API
│   ├── core/                       # Pure Python domain core (Zero web framework dependencies)
│   │   ├── __init__.py             # Public exports for models and engine
│   │   ├── i18n.py                 # Pure-Python bilingual dictionary mapping (English & Khmer)
│   │   ├── models.py               # Fact, WorkingMemory, Priority, Deduction, Rule, AuditEntry
│   │   ├── rules.py                # Knowledge Base (Bilingual IF-THEN rules)
│   │   └── engine.py               # Forward-chaining engine & priority conflict resolution
│   ├── static/
│   │   ├── css/style.css           # Modern clinical CSS with accessible badges & responsive grid
│   │   └── js/main.js              # Client-side validation, presets, and dynamic audit filtering
│   └── templates/
│       ├── base.html               # Base Jinja2 layout with navigation & footer
│       └── index.html              # Diagnostic form, risk badges, working memory, & audit trail
└── tests/
    ├── __init__.py
    ├── test_rules.py               # Isolated unit tests for rule conditions & edge boundaries
    ├── test_engine.py              # Forward chaining, conflict resolution, & fallback tests
    └── test_routes.py              # Integration tests for Flask form POST, /lang/, & JSON REST API
```

---

## 💾 Where is Data Stored?

| Data Type | Storage Mechanism | Location in Code | Lifecycle / Retention |
| :--- | :--- | :--- | :--- |
| **Patient Symptoms & Facts** | Python Dictionary in RAM | [`WorkingMemory`](file:///D:/HongBunleang/1_Norton/year3/Term1/4ExpertSystemDevelopment/ExportsystemTest/app/core/models.py) | **Stateless & Ephemeral** (Request-scoped only; leaves no unencrypted PHI on disk) |
| **Clinical Rules & Logic** | Declarative Python objects | [`app/core/rules.py`](file:///D:/HongBunleang/1_Norton/year3/Term1/4ExpertSystemDevelopment/ExportsystemTest/app/core/rules.py) | Application runtime (loaded into memory at boot) |
| **Selected Language (`en`/`km`)** | Cryptographically Signed Cookie | `session['locale']` | Browser session |
| **Bilingual Translations** | Pure-Python hash map | [`app/core/i18n.py`](file:///D:/HongBunleang/1_Norton/year3/Term1/4ExpertSystemDevelopment/ExportsystemTest/app/core/i18n.py) | Application runtime |

---

## 🧠 Expert System Concepts & Design

### 1. Separation of Concerns (Clean Architecture)
The core reasoning engine (`app/core/`) is completely decoupled from Flask or any external web framework. It can be executed as a standalone Python library, CLI utility, or background worker without any web dependencies.

### 2. Working Memory & Facts
Observations submitted by the user are encapsulated in `Fact` objects and held within `WorkingMemory`. The engine supports two categories of facts:
- **`input` facts**: Raw biometric observations (e.g. `temperature = 39.5`, `cough_severity = 'severe'`).
- **`derived` facts**: Inferred intermediate abstractions generated by rules during inference cycles (e.g. `has_high_fever = True`, `persistent_fever = True`, `has_hypoxia = True`).

### 3. Forward-Chaining Inference Engine
The `InferenceEngine` executes multi-cycle forward chaining until a stable quiescent state is reached:
1. **Cycle 1**: Evaluates intermediate derivation rules against raw input observations, deducing clinical flags.
2. **Cycle 2+**: Newly asserted facts satisfy conditions of higher-order triage rules.
3. **Termination**: The loop breaks when no new rules fire or when `max_cycles` is reached.

### 4. Risk-Based Conflict Resolution
When multiple candidate rules match, clinical safety dictates that the highest-risk deduction must supersede milder diagnoses:
$$\text{EMERGENCY (5)} > \text{URGENT (4)} > \text{MODERATE (3)} > \text{LOW (2)} > \text{INCONCLUSIVE (1)}$$
If zero rules match atypical input facts, the engine falls back to `INCONCLUSIVE` with guidance to seek professional healthcare assessment.

### 5. Explainable AI (Audit Trail)
Every single rule evaluated is logged into an `AuditEntry`. The resulting audit trail records:
- Rule ID and human-readable clinical rationale (in both English and Khmer).
- Mathematical condition representation.
- Whether the rule fired (`True`/`False`) and why.
- Intermediate facts asserted into working memory.
- Conflict resolution explanation detailing which rules competed and why the winner was chosen.

---

## 📋 Clinical Knowledge Base (Rule Summary)

| Rule ID | Priority | Condition Summary | Clinical Diagnosis (English / ខ្មែរ) |
| :--- | :---: | :--- | :--- |
| `R_DERIVE_HIGH_FEVER` | Intermediate | `temperature >= 39.0°C` | Asserts `has_high_fever=True`, `has_fever=True` |
| `R_DERIVE_STANDARD_FEVER` | Intermediate | `38.0°C <= temperature < 39.0°C` | Asserts `has_fever=True` |
| `R_DERIVE_HYPOXIA` | Intermediate | `oxygen_saturation < 92.0%` | Asserts `has_hypoxia=True` |
| `R_DERIVE_PERSISTENT_FEVER`| Intermediate | `has_fever == True` AND `duration >= 3` | Asserts `persistent_fever=True` |
| `R_DERIVE_PROLONGED_ILLNESS`| Intermediate | `duration_days >= 7` | Asserts `is_prolonged=True` |
| `R_EMERG_RESP_DISTRESS` | **EMERGENCY** | `respiratory_distress == 'severe'` OR `has_hypoxia` | Critical Respiratory Distress / វិបត្តិផ្លូវដង្ហើមធ្ងន់ធ្ងរ |
| `R_EMERG_HYPERPYREXIA` | **EMERGENCY** | `temperature >= 40.5°C` | Extreme Hyperpyrexia (> 40.5°C) / កម្ដៅរាងកាយឡើងខ្ពស់ខ្លាំង |
| `R_EMERG_SEPSIS_ALERT` | **EMERGENCY** | (`has_high_fever` OR temp < 35.5) AND `lethargy_confusion` | Suspected Severe Sepsis / សង្ស័យឆ្លងមេរោគក្នុងឈាមធ្ងន់ធ្ងរ |
| `R_EMERG_CARDIOPULMONARY`| **EMERGENCY** | `chest_pain` AND (`distress in ['moderate','severe']` OR `has_high_fever`) | Acute Cardiopulmonary Syndrome / វិបត្តិបេះដូងនិងសួតស្រួចស្រាវ |
| `R_URG_PROLONGED_HIGH_FEVER` | **URGENT** | `has_high_fever` AND `persistent_fever` (>= 39°C, >= 3 days) | Prolonged High-Grade Pyrexia / ក្តៅខ្លួនខ្លាំងអូសបន្លាយយូរថ្ងៃ |
| `R_URG_PNEUMONIA_SUSPECT`| **URGENT** | `has_fever` AND cough in `['moderate','severe']` AND distress | Suspected Pneumonia / សង្ស័យរលាកសួត |
| `R_URG_HIGH_RISK_FEBRILE`| **URGENT** | `has_fever` AND `high_risk_condition` | High-Risk Febrile Patient / ក្តៅខ្លួនលើអ្នកជំងឺប្រឈមហានិភ័យខ្ពស់ |
| `R_URG_COMPLICATED_COUGH`| **URGENT** | cough == `'severe'` AND `duration >= 5` AND `has_fever` | Complicated Febrile Bronchitis / រលាកទងសួតស្មុគស្មាញ |
| `R_MOD_PERSISTENT_FEVER` | **MODERATE** | `has_fever` AND `duration >= 3` AND NOT `has_high_fever` | Persistent Moderate Fever / ក្តៅខ្លួនមធ្យមជាប់រហូត |
| `R_MOD_PROLONGED_COUGH` | **MODERATE** | cough in `['moderate','severe']` AND `is_prolonged` | Subacute Prolonged Cough / ក្អកអូសបន្លាយយូរថ្ងៃ |
| `R_MOD_FEBRILE_URI` | **MODERATE** | `has_fever` AND cough in `['mild','moderate']` AND duration < 3 | Acute Febrile URI / ឆ្លងមេរោគផ្លូវដង្ហើមផ្នែកលើមានក្តៅខ្លួន |
| `R_LOW_MILD_COLD` | **LOW** | cough == `'mild'` AND no fever AND duration < 7 | Mild Common Cold / ផ្តាសាយធម្មតា |
| `R_LOW_HEALTHY_BASELINE` | **LOW** | No cough, no distress, normal temperature (36.0 - 37.5°C) | Normal Physiological Baseline / សញ្ញាជីវិតធម្មតា |

---

## 🚀 Installation & Getting Started

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12 installed.

### 2. Setup Virtual Environment & Install Dependencies

```bash
# Clone or navigate to the project directory
cd expert_system_flask

# Create and activate virtual environment
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

---

## 🧪 Running the Automated Test Suite

The test suite contains **34 comprehensive pytest cases** covering unit boundary conditions, forward chaining, conflict resolution, edge cases, language switching, and REST routes.

```bash
# Run pytest with verbose output
pytest -v
```

Output:
```text
tests/test_engine.py::TestForwardChaining::test_forward_chaining_high_fever_and_persistent PASSED
tests/test_engine.py::TestForwardChaining::test_forward_chaining_hypoxia_triggers_emergency PASSED
tests/test_engine.py::TestConflictResolution::test_emergency_wins_over_urgent_and_moderate PASSED
tests/test_engine.py::TestConflictResolution::test_urgent_wins_over_moderate PASSED
...
tests/test_routes.py::TestWebRoutes::test_switch_language_to_khmer PASSED
tests/test_routes.py::TestWebRoutes::test_switch_language_to_english PASSED
============================= 34 passed in 0.38s ==============================
```

---

## 🌐 Booting the Flask Application

Run the server using the entry point script:

```bash
python run.py
```

The application will start on `http://127.0.0.1:5000`. Open your browser to access the diagnostic portal. Toggle between English and Khmer using the top-right button.

---

## 📡 REST API Documentation

### 1. Evaluate Patient Facts
- **Endpoint**: `POST /api/evaluate`
- **Headers**: `Content-Type: application/json`

#### Example Request Payload:
```json
{
  "temperature": 39.5,
  "duration_days": 4,
  "cough_severity": "moderate",
  "respiratory_distress": "none",
  "oxygen_saturation": 96.0,
  "chest_pain": false,
  "lethargy_confusion": false,
  "high_risk_condition": false
}
```

#### Example Response (HTTP 200 OK):
```json
{
  "status": "success",
  "data": {
    "final_deduction": {
      "risk_level": "URGENT",
      "risk_level_value": 4,
      "risk_label": "Urgent",
      "diagnosis": "Prolonged High-Grade Pyrexia (>= 39.0°C, >= 3 Days)",
      "diagnosis_km": "ក្តៅខ្លួនខ្លាំងអូសបន្លាយយូរថ្ងៃ (>= 39.0°C លើសពី ៣ ថ្ងៃ)",
      "action_advice": [
        "Urgent same-day clinical assessment by a physician is required (within 12-24 hours).",
        "Laboratory investigations needed: Complete Blood Count (CBC), CRP, ESR, and urinalysis.",
        "Maintain meticulous fluid intake and scheduled antipyretic dosing (paracetamol/ibuprofen)."
      ],
      "action_advice_km": [
        "ទាមទារការពិនិត្យវាយតម្លៃដោយគ្រូពេទ្យក្នុងថ្ងៃតែមួយ (ក្នុងរង្វង់ ១២ ទៅ ២៤ ម៉ោង)។",
        "ត្រូវធ្វើតេស្តមន្ទីរពិសោធន៍៖ វិភាគឈាមទូទៅ (CBC), CRP, ESR និងតេស្តទឹកនោម។",
        "រក្សាការពិសាជាតិទឹកឱ្យបានគ្រប់គ្រាន់ និងប្រើប្រាស់ថ្នាំបញ្ចុះកម្ដៅឱ្យបានត្រឹមត្រូវតាមកម្រិត។"
      ],
      "new_facts": {},
      "is_terminal": true
    },
    "matched_rules_count": 3,
    "matched_rule_ids": [
      "R_DERIVE_HIGH_FEVER",
      "R_DERIVE_PERSISTENT_FEVER",
      "R_URG_PROLONGED_HIGH_FEVER"
    ],
    "working_memory": {
      "temperature": {"name": "temperature", "value": 39.5, "source": "input"},
      "has_high_fever": {"name": "has_high_fever", "value": true, "source": "derived"},
      "persistent_fever": {"name": "persistent_fever", "value": true, "source": "derived"}
    },
    "conflict_resolution_notes": "Single triage rule 'R_URG_PROLONGED_HIGH_FEVER' (Urgent) fired without conflict.",
    "conflict_resolution_notes_km": "វិធានតែមួយ 'R_URG_PROLONGED_HIGH_FEVER' (បន្ទាន់ខ្លាំង) ត្រូវបានដំណើរការដោយគ្មានវិវាទ។",
    "execution_time_ms": 0.42,
    "audit_trail": [ ... ]
  }
}
```

### 2. Inspect Knowledge Base Rules
- **Endpoint**: `GET /api/rules`
- **Response**: List of all knowledge base rules with IDs, priority weight, condition strings, and bilingual clinical rationales.

---

## 🎨 Interactive Clinical UI Features

- **Instant Language Switcher**: One-click toggle between English and Khmer (`🇺🇸 EN / 🇰🇭 ខ្មែរ`).
- **Quick Presets**: 5 one-click clinical scenario buttons (Emergency, Urgent, Moderate, Low Cold, Normal Baseline) populate the form instantly.
- **Dynamic Pulse Oximetry Monitor**: Live client-side listener triggers an immediate visual warning if $SpO_2 < 92\%$.
- **Collapsible Fact Inspector**: View all facts in working memory separated by provenance (`INPUT` vs `DERIVED`).
- **Explainable Trace Filter**: Filter audit entries dynamically by `All`, `Fired Only`, or `Failed`.
#   E x p o r t S y s t e m T e s t  
 