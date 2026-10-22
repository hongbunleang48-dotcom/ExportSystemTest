"""app/core/rules.py

Knowledge Base: Formal IF-THEN Clinical Triage Rules.
Defines medical heuristics with hierarchical priorities:
Emergency > Urgent > Moderate > Low > Inconclusive.

Supports intermediate forward-chaining rules and terminal triage recommendations
with complete bilingual English and Khmer documentation and deductions.
"""

from __future__ import annotations

from typing import List

from app.core.models import Deduction, Priority, Rule, WorkingMemory


def get_knowledge_base() -> List[Rule]:
    """Factory function returning the complete clinical triage rule set.
    
    Ordered systematically:
    1. Intermediate derivation rules (abstract primitive facts into clinical concepts).
    2. Emergency triage rules (Priority 5).
    3. Urgent triage rules (Priority 4).
    4. Moderate triage rules (Priority 3).
    5. Low-risk triage rules (Priority 2).
    """
    rules: List[Rule] = []

    # =========================================================================
    # STAGE 1: FORWARD-CHAINING INTERMEDIATE DERIVATION RULES
    # =========================================================================

    # Derivation: High Fever (temp >= 39.0°C)
    rules.append(
        Rule(
            rule_id="R_DERIVE_HIGH_FEVER",
            name="Derive High-Grade Fever",
            name_km="ទាញយកសញ្ញាណក្តៅខ្លួនខ្លាំង (High-Grade Fever)",
            description="Derives 'has_high_fever' and 'has_fever' if core body temperature is >= 39.0°C.",
            description_km="ទាញយកសញ្ញាណ 'has_high_fever' និង 'has_fever' ប្រសិនបើសីតុណ្ហភាពរាងកាយ >= 39.0°C។",
            condition=lambda m: float(m.get("temperature", 0.0)) >= 39.0,
            condition_repr="temperature >= 39.0°C",
            priority=Priority.LOW,
            weight=10,
            is_intermediate=True,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Intermediate: High-Grade Fever Identified",
                diagnosis_km="សញ្ញាណកម្រិតមធ្យម៖ ក្តៅខ្លួនខ្លាំងត្រូវបានកំណត់",
                action_advice=[],
                action_advice_km=[],
                new_facts={"has_high_fever": True, "has_fever": True},
                is_terminal=False,
            ),
        )
    )

    # Derivation: Standard Fever (38.0°C <= temp < 39.0°C)
    rules.append(
        Rule(
            rule_id="R_DERIVE_STANDARD_FEVER",
            name="Derive Standard Pyrexia",
            name_km="ទាញយកសញ្ញាណក្តៅខ្លួនធម្មតា (Standard Pyrexia)",
            description="Derives 'has_fever' if core body temperature is between 38.0°C and 38.9°C.",
            description_km="ទាញយកសញ្ញាណ 'has_fever' ប្រសិនបើសីតុណ្ហភាពរាងកាយនៅចន្លោះ 38.0°C ដល់ 38.9°C។",
            condition=lambda m: 38.0 <= float(m.get("temperature", 0.0)) < 39.0,
            condition_repr="38.0°C <= temperature < 39.0°C",
            priority=Priority.LOW,
            weight=9,
            is_intermediate=True,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Intermediate: Standard Fever Identified",
                diagnosis_km="សញ្ញាណកម្រិតមធ្យម៖ ក្តៅខ្លួនធម្មតាត្រូវបានកំណត់",
                action_advice=[],
                action_advice_km=[],
                new_facts={"has_fever": True, "has_high_fever": False},
                is_terminal=False,
            ),
        )
    )

    # Derivation: Hypoxia (SpO2 < 92%)
    rules.append(
        Rule(
            rule_id="R_DERIVE_HYPOXIA",
            name="Derive Blood Hypoxia",
            name_km="ទាញយកសញ្ញាណកង្វះអុកស៊ីសែនក្នុងឈាម (Hypoxia)",
            description="Derives 'has_hypoxia' if measured pulse oximetry SpO2 < 92%.",
            description_km="ទាញយកសញ្ញាណ 'has_hypoxia' ប្រសិនបើកម្រិត SpO2 < 92%។",
            condition=lambda m: m.get("oxygen_saturation") is not None
            and float(m.get("oxygen_saturation", 100)) < 92.0,
            condition_repr="oxygen_saturation < 92.0%",
            priority=Priority.LOW,
            weight=8,
            is_intermediate=True,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Intermediate: Hypoxemia Detected",
                diagnosis_km="សញ្ញាណកម្រិតមធ្យម៖ រកឃើញកង្វះអុកស៊ីសែនក្នុងឈាម",
                action_advice=[],
                action_advice_km=[],
                new_facts={"has_hypoxia": True},
                is_terminal=False,
            ),
        )
    )

    # Derivation: Persistent Fever (fever present and duration >= 3 days)
    rules.append(
        Rule(
            rule_id="R_DERIVE_PERSISTENT_FEVER",
            name="Derive Persistent Febrile Course",
            name_km="ទាញយកសញ្ញាណក្តៅខ្លួនជាប់រហូត (Persistent Fever)",
            description="Derives 'persistent_fever' if patient has fever and duration >= 3 days.",
            description_km="ទាញយកសញ្ញាណ 'persistent_fever' ប្រសិនបើមានក្តៅខ្លួន និងមានរយៈពេល >= 3 ថ្ងៃ។",
            condition=lambda m: m.is_true("has_fever")
            and int(m.get("duration_days", 0)) >= 3,
            condition_repr="has_fever == True and duration_days >= 3",
            priority=Priority.LOW,
            weight=7,
            is_intermediate=True,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Intermediate: Persistent Fever Identified",
                diagnosis_km="សញ្ញាណកម្រិតមធ្យម៖ ក្តៅខ្លួនជាប់រហូតត្រូវបានកំណត់",
                action_advice=[],
                action_advice_km=[],
                new_facts={"persistent_fever": True},
                is_terminal=False,
            ),
        )
    )

    # Derivation: Prolonged Illness Course (duration >= 7 days)
    rules.append(
        Rule(
            rule_id="R_DERIVE_PROLONGED_ILLNESS",
            name="Derive Prolonged Illness Course",
            name_km="ទាញយកសញ្ញាណជំងឺអូសបន្លាយយូរ (Prolonged Illness)",
            description="Derives 'is_prolonged' if symptom duration is 7 days or more.",
            description_km="ទាញយកសញ្ញាណ 'is_prolonged' ប្រសិនបើរោគសញ្ញាមានរយៈពេល ៧ ថ្ងៃ ឬលើសពីនេះ។",
            condition=lambda m: int(m.get("duration_days", 0)) >= 7,
            condition_repr="duration_days >= 7",
            priority=Priority.LOW,
            weight=6,
            is_intermediate=True,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Intermediate: Prolonged Illness Duration",
                diagnosis_km="សញ្ញាណកម្រិតមធ្យម៖ រយៈពេលជំងឺអូសបន្លាយយូរ",
                action_advice=[],
                action_advice_km=[],
                new_facts={"is_prolonged": True},
                is_terminal=False,
            ),
        )
    )

    # =========================================================================
    # STAGE 2: EMERGENCY TRIAGE RULES (Priority: EMERGENCY / 5)
    # =========================================================================

    # Emergency: Critical Respiratory Distress / Severe Hypoxia
    rules.append(
        Rule(
            rule_id="R_EMERG_RESP_DISTRESS",
            name="Emergency: Critical Respiratory Distress",
            name_km="សង្គ្រោះបន្ទាន់៖ វិបត្តិផ្លូវដង្ហើមធ្ងន់ធ្ងរ (Critical Respiratory Distress)",
            description="Severe breathing difficulty or SpO2 < 92% constitutes immediate respiratory threat.",
            description_km="ពិបាកដកដង្ហើមធ្ងន់ធ្ងរ ឬ SpO2 < 92% បង្ហាញពីហានិភ័យផ្លូវដង្ហើមធ្ងន់ធ្ងរភ្លាមៗ។",
            condition=lambda m: str(m.get("respiratory_distress", "")).lower() == "severe"
            or m.is_true("has_hypoxia"),
            condition_repr="respiratory_distress == 'severe' OR has_hypoxia == True",
            priority=Priority.EMERGENCY,
            weight=100,
            deduction=Deduction(
                risk_level=Priority.EMERGENCY,
                diagnosis="Critical Respiratory Distress / Impending Respiratory Failure",
                diagnosis_km="វិបត្តិផ្លូវដង្ហើមធ្ងន់ធ្ងរ / ហានិភ័យខ្សោយផ្លូវដង្ហើមស្រួចស្រាវ",
                action_advice=[
                    "Call Emergency Medical Services (911/112) immediately.",
                    "Administer supplemental high-flow oxygen if available.",
                    "Position patient in an upright, tripod sitting posture to ease respiratory effort.",
                    "Do not leave the patient unattended; monitor vitals and alertness continuously.",
                ],
                action_advice_km=[
                    "ទូរស័ព្ទទៅសេវាសង្គ្រោះបន្ទាន់ (119/112) ជាបន្ទាន់។",
                    "ផ្តល់អុកស៊ីសែនជំនួយកម្រិតខ្ពស់ ប្រសិនបើមានឧបករណ៍ និងបុគ្គលិកជំនាញ។",
                    "ដាក់អ្នកជំងឺក្នុងឥរិយាបថអង្គុយផ្អៀងទៅមុខ (Tripod position) ដើម្បីជួយសម្រាលការដកដង្ហើម។",
                    "មិនត្រូវទុកអ្នកជំងឺចោលតែម្នាក់ឯងឡើយ តាមដានសញ្ញាជីវិត និងស្មារតីជាប់ជានិច្ច។",
                ],
            ),
        )
    )

    # Emergency: Extreme Hyperpyrexia (temp >= 40.5°C)
    rules.append(
        Rule(
            rule_id="R_EMERG_HYPERPYREXIA",
            name="Emergency: Severe Hyperpyrexia",
            name_km="សង្គ្រោះបន្ទាន់៖ ក្តៅខ្លួនខ្លាំងកម្រិតគ្រោះថ្នាក់ (Severe Hyperpyrexia)",
            description="Core body temperature >= 40.5°C requires emergency clinical stabilization.",
            description_km="សីតុណ្ហភាពរាងកាយ >= 40.5°C ទាមទារឱ្យមានការសង្គ្រោះបន្ទាន់ភ្លាមៗ។",
            condition=lambda m: float(m.get("temperature", 0.0)) >= 40.5,
            condition_repr="temperature >= 40.5°C",
            priority=Priority.EMERGENCY,
            weight=95,
            deduction=Deduction(
                risk_level=Priority.EMERGENCY,
                diagnosis="Extreme Hyperpyrexia (> 40.5°C)",
                diagnosis_km="កម្ដៅរាងកាយឡើងខ្ពស់ខ្លាំងកម្រិតគ្រោះថ្នាក់ (> 40.5°C)",
                action_advice=[
                    "Seek immediate emergency room evaluation.",
                    "High risk of febrile encephalopathy, organ hypoperfusion, and seizures.",
                    "Initiate passive cooling: loosen tight clothing and apply cool damp cloths to forehead and axillae.",
                    "Ensure open airway and prepare for emergency antipyretic/IV administration.",
                ],
                action_advice_km=[
                    "ត្រូវបញ្ជូនទៅបន្ទប់សង្គ្រោះបន្ទាន់ភ្លាមៗ។",
                    "ហានិភ័យខ្ពស់នៃការខូចខាតប្រព័ន្ធសរសៃប្រសាទ ការប្រកាច់ និងខូចខាតសរីរាង្គ។",
                    "អនុវត្តការបញ្ចុះកម្ដៅបឋម៖ ដោះសម្លៀកបំពាក់ក្រាស់ៗ ជូតខ្លួនដោយកន្សែងសើមឧណ្ហៗលើថ្ងាស និងក្លៀក។",
                    "រក្សាផ្លូវដង្ហើមឱ្យស្រឡះ និងត្រៀមផ្តល់ថ្នាំបញ្ចុះកម្ដៅតាមការណែនាំរបស់គ្រូពេទ្យ។",
                ],
            ),
        )
    )

    # Emergency: Suspected Sepsis Alert (High fever or hypothermia + lethargy/confusion)
    rules.append(
        Rule(
            rule_id="R_EMERG_SEPSIS_ALERT",
            name="Emergency: Suspected Severe Sepsis",
            name_km="សង្គ្រោះបន្ទាន់៖ សង្ស័យការឆ្លងមេរោគក្នុងឈាមធ្ងន់ធ្ងរ (Suspected Severe Sepsis)",
            description="Abnormal temperature combined with altered mental status or severe lethargy.",
            description_km="សីតុណ្ហភាពខុសប្រក្រតីរួមផ្សំជាមួយការវង្វេងស្មារតី ឬងងុយដេកខ្លាំង។",
            condition=lambda m: (
                m.is_true("has_high_fever")
                or float(m.get("temperature", 37.0)) < 35.5
            )
            and m.is_true("lethargy_confusion"),
            condition_repr="(has_high_fever == True OR temperature < 35.5°C) AND lethargy_confusion == True",
            priority=Priority.EMERGENCY,
            weight=90,
            deduction=Deduction(
                risk_level=Priority.EMERGENCY,
                diagnosis="Suspected Severe Sepsis with Altered Mental State",
                diagnosis_km="សង្ស័យការឆ្លងមេរោគក្នុងឈាមធ្ងន់ធ្ងររួមផ្សំនឹងការប្រែប្រួលស្មារតី",
                action_advice=[
                    "Immediate transfer to an emergency resuscitation bay.",
                    "Time-critical condition: potential septic shock or meningoencephalitis.",
                    "Rule out acute hypoglycemia; initiate rapid fluid resuscitation and broad-spectrum IV antibiotics.",
                ],
                action_advice_km=[
                    "បញ្ជូនជាបន្ទាន់ទៅផ្នែកសង្គ្រោះបន្ទាន់នៃមន្ទីរពេទ្យ។",
                    "ស្ថានភាពធ្ងន់ធ្ងរប្រឈមនឹងការគាំងសរីរាង្គ ឬការរលាកស្រោមខួរក្បាល។",
                    "ពិនិត្យកម្រិតជាតិស្ករក្នុងឈាមភ្លាមៗ និងត្រៀមបញ្ចូលសេរ៉ូម និងថ្នាំផ្សះតាមសរសៃឈាម។",
                ],
            ),
        )
    )

    # Emergency: Acute Cardiopulmonary Distress (Chest pain + dyspnea or high fever)
    rules.append(
        Rule(
            rule_id="R_EMERG_CARDIOPULMONARY",
            name="Emergency: Acute Cardiopulmonary Distress",
            name_km="សង្គ្រោះបន្ទាន់៖ វិបត្តិបេះដូងនិងសួតស្រួចស្រាវ (Acute Cardiopulmonary Distress)",
            description="New-onset chest pain paired with moderate/severe respiratory distress or high fever.",
            description_km="ឈឺទ្រូងថ្មីៗរួមផ្សំនឹងការពិបាកដកដង្ហើមកម្រិតមធ្យម/ធ្ងន់ធ្ងរ ឬក្តៅខ្លួនខ្លាំង។",
            condition=lambda m: m.is_true("chest_pain")
            and (
                str(m.get("respiratory_distress", "")).lower() in ["moderate", "severe"]
                or m.is_true("has_high_fever")
            ),
            condition_repr="chest_pain == True AND (respiratory_distress IN ['moderate', 'severe'] OR has_high_fever == True)",
            priority=Priority.EMERGENCY,
            weight=85,
            deduction=Deduction(
                risk_level=Priority.EMERGENCY,
                diagnosis="Acute Cardiopulmonary / Pleuropericardial Syndrome",
                diagnosis_km="រោគសញ្ញាវិបត្តិបេះដូង និងសួតស្រួចស្រាវ / រលាកស្រោមសួត",
                action_advice=[
                    "Call emergency ambulance services without delay.",
                    "Needs emergency 12-lead ECG, cardiac biomarker panel (Troponin), and urgent chest imaging.",
                    "Keep patient calm, rested, and in a comfortable semi-reclined position.",
                ],
                action_advice_km=[
                    "ហៅរថយន្តសង្គ្រោះបន្ទាន់ជាបន្ទាន់ដោយមិនបង្អង់យូរ។",
                    "ទាមទារការវាស់ចង្វាក់បេះដូង (ECG 12-lead) ពិនិត្យសារធាតុគីមីបេះដូង (Troponin) និងថតកាំរស្មីអ៊ិចទ្រូងបន្ទាន់។",
                    "រក្សាអ្នកជំងឺឱ្យស្ងប់ស្ងាត់ សម្រាក និងក្នុងឥរិយាបថកល់ខ្នងពាក់កណ្តាល។",
                ],
            ),
        )
    )

    # =========================================================================
    # STAGE 3: URGENT TRIAGE RULES (Priority: URGENT / 4)
    # =========================================================================

    # Urgent: Prolonged High-Grade Fever (temp >= 39.0°C and duration >= 3 days)
    rules.append(
        Rule(
            rule_id="R_URG_PROLONGED_HIGH_FEVER",
            name="Urgent: Prolonged High-Grade Pyrexia",
            name_km="បន្ទាន់ខ្លាំង៖ ក្តៅខ្លួនខ្លាំងអូសបន្លាយយូរថ្ងៃ (Prolonged High-Grade Pyrexia)",
            description="High fever (>= 39°C) persisting for 3 or more days warrants same-day clinical assessment.",
            description_km="ក្តៅខ្លួនខ្លាំង (>= 39°C) បន្តលើសពី ៣ ថ្ងៃ ទាមទារឱ្យជួបគ្រូពេទ្យក្នុងថ្ងៃតែមួយ។",
            condition=lambda m: m.is_true("has_high_fever")
            and m.is_true("persistent_fever"),
            condition_repr="has_high_fever == True AND persistent_fever == True",
            priority=Priority.URGENT,
            weight=80,
            deduction=Deduction(
                risk_level=Priority.URGENT,
                diagnosis="Prolonged High-Grade Pyrexia (>= 39.0°C, >= 3 Days)",
                diagnosis_km="ក្តៅខ្លួនខ្លាំងអូសបន្លាយយូរថ្ងៃ (>= 39.0°C លើសពី ៣ ថ្ងៃ)",
                action_advice=[
                    "Urgent same-day clinical assessment by a physician is required (within 12-24 hours).",
                    "Laboratory investigations needed: Complete Blood Count (CBC), CRP, ESR, and urinalysis.",
                    "Maintain meticulous fluid intake and scheduled antipyretic dosing (paracetamol/ibuprofen).",
                ],
                action_advice_km=[
                    "ទាមទារការពិនិត្យវាយតម្លៃដោយគ្រូពេទ្យក្នុងថ្ងៃតែមួយ (ក្នុងរង្វង់ ១២ ទៅ ២៤ ម៉ោង)។",
                    "ត្រូវធ្វើតេស្តមន្ទីរពិសោធន៍៖ វិភាគឈាមទូទៅ (CBC), CRP, ESR និងតេស្តទឹកនោម។",
                    "រក្សាការពិសាជាតិទឹកឱ្យបានគ្រប់គ្រាន់ និងប្រើប្រាស់ថ្នាំបញ្ចុះកម្ដៅឱ្យបានត្រឹមត្រូវតាមកម្រិត។",
                ],
            ),
        )
    )

    # Urgent: Suspected Pneumonia (Fever + significant cough + moderate distress)
    rules.append(
        Rule(
            rule_id="R_URG_PNEUMONIA_SUSPECT",
            name="Urgent: Suspected Pneumonia / LRTI",
            name_km="បន្ទាន់ខ្លាំង៖ សង្ស័យរលាកសួត (Suspected Pneumonia / LRTI)",
            description="Fever paired with moderate-to-severe cough and respiratory distress suggests pneumonia.",
            description_km="ក្តៅខ្លួនរួមផ្សំក្អកមធ្យមទៅធ្ងន់ធ្ងរ និងពិបាកដកដង្ហើម បង្ហាញពីហានិភ័យរលាកសួត។",
            condition=lambda m: m.is_true("has_fever")
            and str(m.get("cough_severity", "")).lower() in ["moderate", "severe"]
            and str(m.get("respiratory_distress", "")).lower() in ["mild", "moderate"],
            condition_repr="has_fever == True AND cough IN ['moderate', 'severe'] AND respiratory_distress IN ['mild', 'moderate']",
            priority=Priority.URGENT,
            weight=75,
            deduction=Deduction(
                risk_level=Priority.URGENT,
                diagnosis="Suspected Lower Respiratory Tract Infection (Pneumonia)",
                diagnosis_km="សង្ស័យការឆ្លងមេរោគផ្លូវដង្ហើមផ្នែកក្រោម (រលាកសួត)",
                action_advice=[
                    "Urgent clinic or outpatient hospital evaluation within 12 hours.",
                    "Physical examination with lung auscultation and diagnostic chest X-ray strongly indicated.",
                    "Assess for sputum purulence, focal wheezes, or crackles.",
                ],
                action_advice_km=[
                    "ត្រូវទៅពិនិត្យនៅគ្លីនិក ឬមន្ទីរពេទ្យក្នុងរង្វង់ ១២ ម៉ោង។",
                    "ទាមទារការស្តាប់សួតដោយគ្រូពេទ្យ និងការថតកាំរស្មីអ៊ិចសួត (Chest X-ray) ជាចាំបាច់។",
                    "ពិនិត្យតាមដានស្លេស្ម សំឡេងកកិតសួត និងកម្រិតខ្យល់ក្នុងសួត។",
                ],
            ),
        )
    )

    # Urgent: High-Risk Febrile Patient (Fever + immunocompromised/chronic condition)
    rules.append(
        Rule(
            rule_id="R_URG_HIGH_RISK_FEBRILE",
            name="Urgent: Febrile Episode in High-Risk Patient",
            name_km="បន្ទាន់ខ្លាំង៖ ក្តៅខ្លួនលើអ្នកជំងឺប្រឈមហានិភ័យខ្ពស់ (High-Risk Febrile Patient)",
            description="Any confirmed fever in a patient with severe underlying chronic disease or immunosuppression.",
            description_km="រាល់ការក្តៅខ្លួនលើអ្នកជំងឺមានជំងឺប្រចាំកាយធ្ងន់ធ្ងរ ឬប្រព័ន្ធភាពស៊ាំចុះខ្សោយ។",
            condition=lambda m: m.is_true("has_fever")
            and m.is_true("high_risk_condition"),
            condition_repr="has_fever == True AND high_risk_condition == True",
            priority=Priority.URGENT,
            weight=70,
            deduction=Deduction(
                risk_level=Priority.URGENT,
                diagnosis="High-Risk Patient with Acute Febrile Illness",
                diagnosis_km="អ្នកជំងឺប្រឈមហានិភ័យខ្ពស់មានជំងឺក្តៅខ្លួនស្រួចស្រាវ",
                action_advice=[
                    "Same-day consultation with primary physician or treating specialist.",
                    "Lower threshold for antibiotic initiation and comprehensive microbiological workup.",
                    "Close clinical surveillance for signs of systemic decompensation.",
                ],
                action_advice_km=[
                    "ជួបពិគ្រោះជាមួយគ្រូពេទ្យផ្ទាល់ខ្លួន ឬគ្រូពេទ្យឯកទេសក្នុងថ្ងៃតែមួយ។",
                    "ពិចារណាការប្រើប្រាស់ថ្នាំផ្សះ និងការវិភាគរោគវិនិច្ឆ័យលម្អិតឱ្យបានលឿន។",
                    "តាមដានយ៉ាងដិតដល់នូវរាល់សញ្ញានៃការធ្លាក់ចុះសុខភាពទូទៅ។",
                ],
            ),
        )
    )

    # Urgent: Severe Complicated Bronchitis (Severe cough >= 5 days with fever)
    rules.append(
        Rule(
            rule_id="R_URG_COMPLICATED_COUGH",
            name="Urgent: Complicated Febrile Bronchitis",
            name_km="បន្ទាន់ខ្លាំង៖ រលាកទងសួតស្មុគស្មាញ (Complicated Febrile Bronchitis)",
            description="Severe cough with fever lasting 5 days or longer indicates secondary bacterial infection.",
            description_km="ក្អកធ្ងន់ធ្ងរជាមួយកម្តៅខ្លួនលើសពី ៥ ថ្ងៃ បង្ហាញពីការឆ្លងមេរោគបាក់តេរីបន្ទាប់បន្សំ។",
            condition=lambda m: str(m.get("cough_severity", "")).lower() == "severe"
            and int(m.get("duration_days", 0)) >= 5
            and m.is_true("has_fever"),
            condition_repr="cough_severity == 'severe' AND duration_days >= 5 AND has_fever == True",
            priority=Priority.URGENT,
            weight=65,
            deduction=Deduction(
                risk_level=Priority.URGENT,
                diagnosis="Complicated Acute Bronchitis / Secondary Bacterial Superinfection",
                diagnosis_km="រលាកទងសួតស្រួចស្រាវស្មុគស្មាញ / ការឆ្លងមេរោគបាក់តេរីបន្ទាប់បន្សំ",
                action_advice=[
                    "Schedule an urgent medical appointment within 24 hours.",
                    "Evaluate airway reactivity, consider sputum culture and targeted prescription therapy.",
                ],
                action_advice_km=[
                    "កំណត់ការណាត់ជួបគ្រូពេទ្យជាបន្ទាន់ក្នុងរង្វង់ ២៤ ម៉ោង។",
                    "វាយតម្លៃផ្លូវដង្ហើម ពិចារណាការបណ្តុះមេរោគស្លេស្ម និងទទួលវេជ្ជបញ្ជាព្យាបាលចំគោលដៅ។",
                ],
            ),
        )
    )

    # =========================================================================
    # STAGE 4: MODERATE TRIAGE RULES (Priority: MODERATE / 3)
    # =========================================================================

    # Moderate: Persistent Moderate Fever (temp >= 38.0°C and duration >= 3 days)
    rules.append(
        Rule(
            rule_id="R_MOD_PERSISTENT_FEVER",
            name="Moderate: Persistent Moderate Fever",
            name_km="មធ្យម៖ ក្តៅខ្លួនមធ្យមជាប់រហូត (Persistent Moderate Fever)",
            description="Fever lasting 3 or more days without immediate red-flag emergency symptoms.",
            description_km="ក្តៅខ្លួនមានរយៈពេល ៣ ថ្ងៃឡើងទៅ ប៉ុន្តែគ្មានសញ្ញាប្រកាសអាសន្នបន្ទាន់។",
            condition=lambda m: m.is_true("has_fever")
            and int(m.get("duration_days", 0)) >= 3
            and not m.is_true("has_high_fever"),
            condition_repr="has_fever == True AND duration_days >= 3 AND has_high_fever == False",
            priority=Priority.MODERATE,
            weight=50,
            deduction=Deduction(
                risk_level=Priority.MODERATE,
                diagnosis="Persistent Moderate Febrile Illness",
                diagnosis_km="ជំងឺក្តៅខ្លួនកម្រិតមធ្យមជាប់រហូត",
                action_advice=[
                    "Book an appointment with a primary care doctor within 24 to 48 hours.",
                    "Maintain continuous fluid replenishment and record temperature log every 4-6 hours.",
                    "Seek expedited care if fever escalates or breathing difficulty ensues.",
                ],
                action_advice_km=[
                    "ណាត់ជួបគ្រូពេទ្យថែទាំបឋមក្នុងរង្វង់ ២៤ ទៅ ៤៨ ម៉ោង។",
                    "ពិសាជាតិទឹកឱ្យបានច្រើន និងកត់ត្រាកម្តៅខ្លួនរៀងរាល់ ៤-៦ ម៉ោងម្តង។",
                    "ស្វែងរកការព្យាបាលលឿនជាងនេះ ប្រសិនបើកម្តៅកើនឡើងលើស ៣៩°C ឬចាប់ផ្តើមពិបាកដកដង្ហើម។",
                ],
            ),
        )
    )

    # Moderate: Subacute / Prolonged Cough (Moderate-severe cough lasting >= 7 days)
    rules.append(
        Rule(
            rule_id="R_MOD_PROLONGED_COUGH",
            name="Moderate: Subacute Prolonged Cough",
            name_km="មធ្យម៖ ក្អកអូសបន្លាយយូរថ្ងៃ (Subacute Prolonged Cough)",
            description="Cough persisting for 7 or more days without severe acute distress.",
            description_km="ក្អកបន្តលើសពី ៧ ថ្ងៃឡើងទៅ ដោយគ្មានការពិបាកដកដង្ហើមធ្ងន់ធ្ងរ។",
            condition=lambda m: str(m.get("cough_severity", "")).lower() in ["moderate", "severe"]
            and m.is_true("is_prolonged"),
            condition_repr="cough IN ['moderate', 'severe'] AND is_prolonged == True",
            priority=Priority.MODERATE,
            weight=45,
            deduction=Deduction(
                risk_level=Priority.MODERATE,
                diagnosis="Subacute / Prolonged Cough Illness",
                diagnosis_km="ជំងឺក្អកអូសបន្លាយយូរថ្ងៃ / រ៉ាំរ៉ៃ",
                action_advice=[
                    "Consult a primary care physician for chest auscultation and assessment.",
                    "Review potential etiologies including post-infectious bronchial hyperreactivity or sinusitis.",
                    "Stay well hydrated and avoid exposure to tobacco smoke or air irritants.",
                ],
                action_advice_km=[
                    "ពិគ្រោះជាមួយគ្រូពេទ្យដើម្បីស្តាប់សួត និងវាយតម្លៃមូលហេតុពិតប្រាកដ។",
                    "ពិនិត្យមូលហេតុដែលអាចបណ្តាលមកពីការរលាកផ្លូវដង្ហើមក្រោយឆ្លងមេរោគ ឬរលាកប្រហោងឆ្អឹង (Sinus)។",
                    "រក្សាជាតិទឹកឱ្យបានគ្រប់គ្រាន់ និងចៀសវាងផ្សែងបារី ឬសារធាតុបង្កប្រតិកម្មក្នុងបរិយាកាស។",
                ],
            ),
        )
    )

    # Moderate: Acute Febrile Upper Respiratory Syndrome (Fever + mild/moderate cough)
    rules.append(
        Rule(
            rule_id="R_MOD_FEBRILE_URI",
            name="Moderate: Acute Febrile Upper Respiratory Infection",
            name_km="មធ្យម៖ ឆ្លងមេរោគផ្លូវដង្ហើមផ្នែកលើមានក្តៅខ្លួន (Acute Febrile URI)",
            description="Fever with mild-to-moderate cough of short duration without respiratory compromise.",
            description_km="ក្តៅខ្លួនជាមួយក្អកស្រាលទៅមធ្យមក្នុងរយៈពេលខ្លី ដោយគ្មានវិបត្តិផ្លូវដង្ហើម។",
            condition=lambda m: m.is_true("has_fever")
            and str(m.get("cough_severity", "")).lower() in ["mild", "moderate"]
            and int(m.get("duration_days", 0)) < 3,
            condition_repr="has_fever == True AND cough IN ['mild', 'moderate'] AND duration_days < 3",
            priority=Priority.MODERATE,
            weight=40,
            deduction=Deduction(
                risk_level=Priority.MODERATE,
                diagnosis="Acute Febrile Upper Respiratory Tract Infection",
                diagnosis_km="ការឆ្លងមេរោគផ្លូវដង្ហើមផ្នែកលើស្រួចស្រាវមានក្តៅខ្លួន",
                action_advice=[
                    "Home rest, antipyretics for comfort, and oral rehydration therapy.",
                    "Monitor progression closely; seek medical evaluation if fever persists beyond 72 hours.",
                ],
                action_advice_km=[
                    "សម្រាកនៅផ្ទះ ប្រើប្រាស់ថ្នាំបញ្ចុះកម្តៅ និងពិសាជាតិទឹកឱ្យបានច្រើន។",
                    "តាមដានរោគសញ្ញាយ៉ាងដិតដល់ ប្រសិនបើក្តៅខ្លួនលើស ៧២ ម៉ោង ត្រូវទៅជួបគ្រូពេទ្យ។",
                ],
            ),
        )
    )

    # =========================================================================
    # STAGE 5: LOW TRIAGE RULES (Priority: LOW / 2)
    # =========================================================================

    # Low: Mild Cold Symptoms (Mild cough, no fever, duration < 7 days)
    rules.append(
        Rule(
            rule_id="R_LOW_MILD_COLD",
            name="Low: Mild Common Cold",
            name_km="ទាប៖ ផ្តាសាយធម្មតា (Mild Common Cold)",
            description="Mild upper airway symptoms without fever or respiratory distress.",
            description_km="រោគសញ្ញាផ្លូវដង្ហើមស្រាល ដោយគ្មានក្តៅខ្លួន ឬពិបាកដកដង្ហើមឡើយ។",
            condition=lambda m: str(m.get("cough_severity", "")).lower() == "mild"
            and not m.is_true("has_fever")
            and not m.is_true("has_high_fever")
            and int(m.get("duration_days", 0)) < 7
            and str(m.get("respiratory_distress", "none")).lower() in ["none", "false", ""],
            condition_repr="cough == 'mild' AND has_fever == False AND duration_days < 7 AND distress == 'none'",
            priority=Priority.LOW,
            weight=30,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Mild Upper Respiratory Tract Infection (Common Cold)",
                diagnosis_km="ការឆ្លងមេរោគផ្លូវដង្ហើមផ្នែកលើកម្រិតស្រាល (ផ្តាសាយធម្មតា)",
                action_advice=[
                    "Supportive home self-care: adequate rest, warm broths, honey, or throat lozenges.",
                    "Saline nasal rinses can relieve nasal congestion.",
                    "Expected resolution within 7 to 10 days; visit a clinic if symptoms worsen.",
                ],
                action_advice_km=[
                    "ថែទាំសុខភាពនៅផ្ទះ៖ សម្រាកឱ្យបានគ្រប់គ្រាន់ ពិសាទឹកក្តៅឧណ្ហៗ ទឹកឃ្មុំ ឬស្ករគ្រាប់បំបាត់ឈឺក។",
                    "អាចប្រើប្រាស់ទឹកអំបិលលាងច្រមុះដើម្បីសម្រាលការតឹងច្រមុះ។",
                    "ជាទូទៅនឹងជាសះស្បើយក្នុងរយៈពេល ៧ ទៅ ១០ ថ្ងៃ។ ប្រសិនបើរោគសញ្ញាមិនធូរស្រាល សូមទៅជួបគ្រូពេទ្យ។",
                ],
            ),
        )
    )

    # Low: Healthy Baseline (Asymptomatic / Normal Vitals)
    rules.append(
        Rule(
            rule_id="R_LOW_HEALTHY_BASELINE",
            name="Low: Normal Physiological Baseline",
            name_km="ទាប៖ សញ្ញាជីវិតធម្មតា (Normal Baseline Vitals)",
            description="Patient exhibits normal vital signs without cough, respiratory compromise, or fever.",
            description_km="អ្នកជំងឺបង្ហាញសញ្ញាជីវិតធម្មតា គ្មានក្អក គ្មានពិបាកដកដង្ហើម និងគ្មានក្តៅខ្លួន។",
            condition=lambda m: str(m.get("cough_severity", "none")).lower() in ["none", "", "false"]
            and str(m.get("respiratory_distress", "none")).lower() in ["none", "", "false"]
            and not m.is_true("has_fever")
            and not m.is_true("has_high_fever")
            and not m.is_true("chest_pain")
            and not m.is_true("lethargy_confusion")
            and 36.0 <= float(m.get("temperature", 36.8)) <= 37.5,
            condition_repr="No cough AND no respiratory distress AND normal temperature (36.0 - 37.5°C)",
            priority=Priority.LOW,
            weight=25,
            deduction=Deduction(
                risk_level=Priority.LOW,
                diagnosis="Asymptomatic / Baseline Normal Vitals",
                diagnosis_km="គ្មានរោគសញ្ញាស្រួចស្រាវ / សញ្ញាជីវិតស្ថិតក្នុងកម្រិតធម្មតា",
                action_advice=[
                    "No acute clinical intervention or prescription therapy indicated.",
                    "Maintain balanced nutrition, adequate sleep, and routine wellness practices.",
                ],
                action_advice_km=[
                    "មិនត្រូវការអន្តរាគមន៍វេជ្ជសាស្ត្រ ឬថ្នាំព្យាបាលនោះទេ។",
                    "បន្តរក្សារបបអាហារមានជីវជាតិ គេងឱ្យបានគ្រប់គ្រាន់ និងអនុវត្តការថែទាំសុខភាពប្រចាំថ្ងៃ។",
                ],
            ),
        )
    )

    return rules
