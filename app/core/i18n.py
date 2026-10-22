"""app/core/i18n.py

Lightweight pure-Python internationalization (i18n) module.
Provides bilingual dictionary mappings and translation helpers for English ('en') and Khmer ('km').
Zero external dependencies.
"""

from typing import Any, Dict, Optional

SUPPORTED_LOCALES = ["en", "km"]
DEFAULT_LOCALE = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Brand & Navigation
    "app_title": {
        "en": "Clinical Triage Advisor",
        "km": "ប្រព័ន្ធវាយតម្លៃកម្រិតសង្គ្រោះបន្ទាន់",
    },
    "app_subtitle": {
        "en": "Rule-Based Expert System • Clean Architecture",
        "km": "ប្រព័ន្ធអ្នកជំនាញផ្អែកលើវិធាន • ស្ថាបត្យកម្មស្អាត",
    },
    "nav_triage": {
        "en": "Diagnostic Triage",
        "km": "ការវាយតម្លៃរោគវិនិច្ឆ័យ",
    },
    "nav_kb_api": {
        "en": "Knowledge Base (API)",
        "km": "មូលដ្ឋានចំណេះដឹង (API)",
    },
    "engine_active": {
        "en": "Forward-Chaining Engine Active",
        "km": "ម៉ាស៊ីនទាញហេតុផលទៅមុខកំពុងដំណើរការ",
    },
    "disclaimer": {
        "en": "Decision Support System Demonstration. For educational and triaging reference only. Not a substitute for direct clinical physician evaluation.",
        "km": "ការបង្ហាញប្រព័ន្ធជំនួយការសម្រេចចិត្ត។ សម្រាប់តែការអប់រំ និងការណែនាំតម្រៀបអ្នកជំងឺប៉ុណ្ណោះ។ មិនអាចជំនួសការពិនិត្យផ្ទាល់ដោយគ្រូពេទ្យបានឡើយ។",
    },
    "priority_hierarchy": {
        "en": "Inference Priority: Emergency > Urgent > Moderate > Low > Inconclusive",
        "km": "លំដាប់អាទិភាព៖ សង្គ្រោះបន្ទាន់ > បន្ទាន់ខ្លាំង > មធ្យម > ទាប > មិនទាន់ច្បាស់លាស់",
    },

    # Form Titles & Presets
    "patient_indicators": {
        "en": "Patient Clinical Indicators",
        "km": "សញ្ញាគ្លីនិក និងរោគសញ្ញារបស់អ្នកជំងឺ",
    },
    "indicators_desc": {
        "en": "Submit observed physiological vitals and symptoms for rule-based evaluation.",
        "km": "បញ្ចូលសញ្ញាសំខាន់ៗ និងរោគសញ្ញាដែលបានសង្កេតសម្រាប់ការវាយតម្លៃផ្អែកលើវិធាន។",
    },
    "quick_scenarios": {
        "en": "Quick Clinical Scenarios:",
        "km": "សេណារីយ៉ូគ្លីនិករហ័ស៖",
    },
    "preset_emergency": {
        "en": "🚨 Emergency (Hypoxia)",
        "km": "🚨 សង្គ្រោះបន្ទាន់ (ខ្វះអុកស៊ីសែន)",
    },
    "preset_urgent": {
        "en": "🔥 Urgent (Prolonged Pyrexia)",
        "km": "🔥 បន្ទាន់ខ្លាំង (ក្តៅខ្លួនយូរថ្ងៃ)",
    },
    "preset_moderate": {
        "en": "⚠️ Moderate (Persistent Fever)",
        "km": "⚠️ មធ្យម (ក្តៅខ្លួនជាប់)",
    },
    "preset_low": {
        "en": "🌿 Low (Mild Cold)",
        "km": "🌿 ទាប (ផ្តាសាយស្រាល)",
    },
    "preset_baseline": {
        "en": "🩺 Baseline Normal",
        "km": "🩺 សភាពធម្មតា",
    },

    # Input Fields
    "temp_label": {
        "en": "Body Temperature (°C)",
        "km": "សីតុណ្ហភាពរាងកាយ (°C)",
    },
    "temp_hint": {
        "en": "Normal: 36.5 - 37.5°C | Pyrexia: ≥ 38.0°C | High: ≥ 39.0°C",
        "km": "ធម្មតា៖ 36.5 - 37.5°C | ក្តៅខ្លួន៖ ≥ 38.0°C | ក្តៅខ្លាំង៖ ≥ 39.0°C",
    },
    "duration_label": {
        "en": "Symptom Duration (Days)",
        "km": "រយៈពេលនៃរោគសញ្ញា (ថ្ងៃ)",
    },
    "duration_hint": {
        "en": "Acute: < 3 days | Persistent: ≥ 3 days | Prolonged: ≥ 7 days",
        "km": "ស្រួចស្រាវ៖ < 3 ថ្ងៃ | ជាប់រហូត៖ ≥ 3 ថ្ងៃ | អូសបន្លាយ៖ ≥ 7 ថ្ងៃ",
    },
    "cough_label": {
        "en": "Cough Severity",
        "km": "កម្រិតធ្ងន់ធ្ងរនៃក្អក",
    },
    "cough_none": {
        "en": "None (No cough)",
        "km": "គ្មាន (គ្មានក្អក)",
    },
    "cough_mild": {
        "en": "Mild (Occasional throat tickle / dry cough)",
        "km": "ស្រាល (រមាស់ក / ក្អកស្ងួតម្តងម្កាល)",
    },
    "cough_moderate": {
        "en": "Moderate (Frequent paroxysms / productive)",
        "km": "មធ្យម (ក្អកញឹកញាប់ / មានស្លេស្ម)",
    },
    "cough_severe": {
        "en": "Severe (Exhausting, uninterrupted paroxysms)",
        "km": "ធ្ងន់ធ្ងរ (ក្អកខ្លាំងមិនឈប់ / អស់កម្លាំងខ្លាំង)",
    },
    "distress_label": {
        "en": "Respiratory Distress / Dyspnea",
        "km": "ពិបាកដកដង្ហើម / ដង្ហក់",
    },
    "critical_indicator": {
        "en": "Critical Triage Indicator",
        "km": "សូចនាករសង្គ្រោះបន្ទាន់សំខាន់",
    },
    "distress_none": {
        "en": "None (Normal unlabored breathing)",
        "km": "គ្មាន (ដកដង្ហើមធម្មតា)",
    },
    "distress_mild": {
        "en": "Mild (Short of breath only on physical exertion)",
        "km": "ស្រាល (ហត់ដង្ហក់ពេលធ្វើចលនា)",
    },
    "distress_moderate": {
        "en": "Moderate (Dyspnea when speaking full sentences)",
        "km": "មធ្យម (ដង្ហក់ពេលនិយាយប្រយោគពេញលេញ)",
    },
    "distress_severe": {
        "en": "Severe (Marked respiratory effort, gasping, stridor)",
        "km": "ធ្ងន់ធ្ងរ (ពិបាកដកដង្ហើមខ្លាំង ហត់ដង្ហក់ ឬដកដង្ហើមឮសូរ)",
    },
    "spo2_label": {
        "en": "Oxygen Saturation SpO2 (%)",
        "km": "កម្រិតអុកស៊ីសែនក្នុងឈាម SpO2 (%)",
    },
    "optional": {
        "en": "Optional",
        "km": "ស្រេចចិត្ត",
    },
    "spo2_hint": {
        "en": "Normal: ≥ 95% | Hypoxia Flag: < 92%",
        "km": "ធម្មតា៖ ≥ 95% | សញ្ញាកង្វះអុកស៊ីសែន៖ < 92%",
    },
    "spo2_alert": {
        "en": "⚠️ Critical: SpO2 < 92% triggers Emergency Respiratory Protocol",
        "km": "⚠️ សង្គ្រោះបន្ទាន់៖ SpO2 < 92% នឹងដំណើរការពិធីសារសង្គ្រោះបន្ទាន់ផ្លូវដង្ហើម",
    },

    # Checkboxes
    "red_flags_label": {
        "en": "Clinical Red Flags & Risk Modifiers",
        "km": "សញ្ញាប្រកាសអាសន្ន និងកត្តាហានិភ័យបន្ថែម",
    },
    "chest_pain_label": {
        "en": "Acute Chest Pain",
        "km": "ឈឺទ្រូងស្រួចស្រាវ",
    },
    "chest_pain_desc": {
        "en": "Pleuritic, substernal, or pressure sensation",
        "km": "ឈឺទ្រូងពេលដកដង្ហើម ឬមានអារម្មណ៍តឹងណែនទ្រូង",
    },
    "lethargy_label": {
        "en": "Lethargy / Altered Mental Status",
        "km": "ងងុយដេកខ្លាំង / វង្វេងស្មារតី",
    },
    "lethargy_desc": {
        "en": "Confusion, drowsiness, or uncharacteristic somnolence",
        "km": "វង្វេងស្មារតី ងងុយដេកខុសប្រក្រតី ឬពិបាកដាស់",
    },
    "comorbidity_label": {
        "en": "High-Risk Comorbidity",
        "km": "ជំងឺប្រចាំកាយប្រឈមហានិភ័យខ្ពស់",
    },
    "comorbidity_desc": {
        "en": "Immunocompromised, severe COPD/asthma, chronic heart failure",
        "km": "ប្រព័ន្ធភាពស៊ាំចុះខ្សោយ ជំងឺសួតរ៉ាំរ៉ៃ (COPD/ហឺត) ឬខ្សោយបេះដូង",
    },
    "btn_submit": {
        "en": "⚡ Execute Expert Triage",
        "km": "⚡ ដំណើរការវាយតម្លៃវេជ្ជសាស្ត្រ",
    },
    "btn_reset": {
        "en": "↺ Reset",
        "km": "↺ កំណត់ឡើងវិញ",
    },

    # Results Section
    "inference_time": {
        "en": "Inference Time:",
        "km": "រយៈពេលទាញហេតុផល៖",
    },
    "matched_rules": {
        "en": "Active Matched Rules:",
        "km": "វិធានដែលត្រូវគ្នា៖",
    },
    "priority_weight": {
        "en": "Priority Weight:",
        "km": "កម្រិតអាទិភាព៖",
    },
    "level_of": {
        "en": "Level {level} of 5",
        "km": "កម្រិត {level} នៃ 5",
    },
    "clinical_directives": {
        "en": "Recommended Clinical Directives",
        "km": "វិធានការណែនាំវេជ្ជសាស្ត្រ",
    },
    "conflict_analysis": {
        "en": "Conflict Resolution Analysis",
        "km": "ការវិភាគដោះស្រាយវិវាទវិធាន",
    },
    "working_memory_title": {
        "en": "Working Memory Fact Store",
        "km": "ឃ្លាំងអង្គហេតុនៃការចងចាំដំណើរការ",
    },
    "facts_count": {
        "en": "({count} facts)",
        "km": "({count} អង្គហេតុ)",
    },
    "th_fact_key": {
        "en": "Fact Key",
        "km": "ឈ្មោះអង្គហេតុ",
    },
    "th_value": {
        "en": "Value",
        "km": "តម្លៃ",
    },
    "th_source": {
        "en": "Source Type",
        "km": "ប្រភេទប្រភព",
    },
    "th_description": {
        "en": "Provenance / Description",
        "km": "ប្រភពដើម / ការពិពណ៌នា",
    },

    # Audit Trail
    "audit_trail_title": {
        "en": "Explainable Audit Trail",
        "km": "ដានសវនកម្មពន្យល់ពីហេតុផល",
    },
    "evaluations_count": {
        "en": "({count} evaluations)",
        "km": "({count} ការវាយតម្លៃ)",
    },
    "audit_intro": {
        "en": "Step-by-step trace showing each knowledge base rule evaluated, its mathematical condition, and whether it fired.",
        "km": "ដានពិនិត្យជាជំហានៗបង្ហាញពីវិធាននីមួយៗក្នុងមូលដ្ឋានចំណេះដឹង លក្ខខណ្ឌ និងថាតើវិធាននោះត្រូវបានដំណើរការឬអត់។",
    },
    "filter_all": {
        "en": "All",
        "km": "ទាំងអស់",
    },
    "filter_fired": {
        "en": "Fired Only",
        "km": "ដំណើរការតែប៉ុណ្ណោះ",
    },
    "filter_failed": {
        "en": "Not Fired",
        "km": "មិនដំណើរការ",
    },
    "audit_condition": {
        "en": "Condition:",
        "km": "លក្ខខណ្ឌ៖",
    },
    "audit_evaluation": {
        "en": "Evaluation:",
        "km": "ការវាយតម្លៃ៖",
    },
    "audit_asserted": {
        "en": "Asserted to Memory:",
        "km": "បានបញ្ចូលទៅការចងចាំ៖",
    },
    "audit_diagnosis": {
        "en": "Diagnosis:",
        "km": "រោគវិនិច្ឆ័យ៖",
    },

    # Empty State
    "empty_title": {
        "en": "Expert Diagnostic System Ready",
        "km": "ប្រព័ន្ធអ្នកជំនាញរោគវិនិច្ឆ័យរួចរាល់",
    },
    "empty_desc": {
        "en": "Provide patient vital signs and symptom observations on the left to begin forward-chaining clinical deduction.",
        "km": "សូមបញ្ចូលសញ្ញាសំខាន់ៗ និងរោគសញ្ញារបស់អ្នកជំងឺនៅខាងឆ្វេង ដើម្បីចាប់ផ្តើមការទាញហេតុផលវេជ្ជសាស្ត្រទៅមុខ។",
    },
    "feature_fc_title": {
        "en": "Forward Chaining",
        "km": "ការទាញហេតុផលទៅមុខ",
    },
    "feature_fc_desc": {
        "en": "Iteratively derives clinical concepts from raw biometric inputs across multiple evaluation cycles.",
        "km": "ទាញយកសញ្ញាណគ្លីនិកជាបន្តបន្ទាប់ពីទិន្នន័យដើមឆ្លងកាត់វដ្តវាយតម្លៃជាច្រើន។",
    },
    "feature_cr_title": {
        "en": "Risk-Based Conflict Resolution",
        "km": "ការដោះស្រាយវិវាទផ្អែកលើហានិភ័យ",
    },
    "feature_cr_desc": {
        "en": "Enforces strict medical priority ordering: Emergency > Urgent > Moderate > Low.",
        "km": "អនុវត្តលំដាប់អាទិភាពវេជ្ជសាស្ត្រតឹងរ៉ឹង៖ សង្គ្រោះបន្ទាន់ > បន្ទាន់ខ្លាំង > មធ្យម > ទាប។",
    },
    "feature_xai_title": {
        "en": "Full Explainability",
        "km": "ការពន្យល់យ៉ាងពេញលេញ",
    },
    "feature_xai_desc": {
        "en": "Every decision is supported by an exhaustive audit trail of evaluated rules and memory states.",
        "km": "រាល់ការសម្រេចចិត្តត្រូវបានគាំទ្រដោយដានសវនកម្មពេញលេញនៃវិធានដែលបានវាយតម្លៃ។",
    },
    "instructions_tip": {
        "en": "💡 Tip: Use the quick scenario buttons at the top of the form for instant demonstrations of each triage category.",
        "km": "💡 គន្លឹះ៖ ប្រើប៊ូតុងសេណារីយ៉ូរហ័សនៅផ្នែកខាងលើនៃទម្រង់សម្រាប់ការបង្ហាញសាកល្បងភ្លាមៗនៃកម្រិតនីមួយៗ។",
    },

    # Priority Labels
    "priority_emergency": {
        "en": "Emergency",
        "km": "សង្គ្រោះបន្ទាន់",
    },
    "priority_urgent": {
        "en": "Urgent",
        "km": "បន្ទាន់ខ្លាំង",
    },
    "priority_moderate": {
        "en": "Moderate",
        "km": "មធ្យម",
    },
    "priority_low": {
        "en": "Low",
        "km": "ទាប",
    },
    "priority_inconclusive": {
        "en": "Inconclusive",
        "km": "មិនទាន់ច្បាស់លាស់",
    },
}


def get_text(key: str, locale: str = DEFAULT_LOCALE, default: Optional[str] = None, **kwargs: Any) -> str:
    """Translates a string key into the specified locale.
    
    Args:
        key: Translation dictionary key.
        locale: Language code ('en' or 'km').
        default: Fallback string if key is not found.
        **kwargs: Format string variables.
        
    Returns:
        Translated string, or key if not found.
    """
    if locale not in SUPPORTED_LOCALES:
        locale = DEFAULT_LOCALE

    entry = TRANSLATIONS.get(key)
    if entry is not None:
        text = entry.get(locale) or entry.get(DEFAULT_LOCALE, key)
    else:
        text = default if default is not None else key

    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text

    return text
