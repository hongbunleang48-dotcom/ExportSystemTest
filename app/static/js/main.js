/**
 * main.js - Client-Side Interactivity for Clinical Triage Expert System
 */

document.addEventListener("DOMContentLoaded", () => {
    // Listen to SpO2 input to dynamically show hypoxia warning
    const spo2Input = document.getElementById("oxygen_saturation");
    if (spo2Input) {
        spo2Input.addEventListener("input", checkSpo2Warning);
        checkSpo2Warning();
    }
});

function checkSpo2Warning() {
    const spo2Input = document.getElementById("oxygen_saturation");
    const spo2Alert = document.getElementById("spo2Alert");
    if (!spo2Input || !spo2Alert) return;

    const val = parseFloat(spo2Input.value);
    if (!isNaN(val) && val > 0 && val < 92.0) {
        spo2Alert.classList.remove("hidden");
    } else {
        spo2Alert.classList.add("hidden");
    }
}

/**
 * Loads predefined clinical scenarios into the form.
 */
function loadScenario(type) {
    const scenarios = {
        emergency: {
            temperature: 39.6,
            duration_days: 2,
            cough_severity: "severe",
            respiratory_distress: "severe",
            oxygen_saturation: 89.0,
            chest_pain: true,
            lethargy_confusion: true,
            high_risk_condition: false,
        },
        urgent: {
            temperature: 39.2,
            duration_days: 4,
            cough_severity: "moderate",
            respiratory_distress: "mild",
            oxygen_saturation: 95.0,
            chest_pain: false,
            lethargy_confusion: false,
            high_risk_condition: true,
        },
        moderate: {
            temperature: 38.3,
            duration_days: 3,
            cough_severity: "moderate",
            respiratory_distress: "none",
            oxygen_saturation: 97.0,
            chest_pain: false,
            lethargy_confusion: false,
            high_risk_condition: false,
        },
        low: {
            temperature: 37.0,
            duration_days: 2,
            cough_severity: "mild",
            respiratory_distress: "none",
            oxygen_saturation: 98.5,
            chest_pain: false,
            lethargy_confusion: false,
            high_risk_condition: false,
        },
        baseline: {
            temperature: 36.7,
            duration_days: 1,
            cough_severity: "none",
            respiratory_distress: "none",
            oxygen_saturation: 99.0,
            chest_pain: false,
            lethargy_confusion: false,
            high_risk_condition: false,
        },
    };

    const data = scenarios[type];
    if (!data) return;

    // Set values
    document.getElementById("temperature").value = data.temperature;
    document.getElementById("duration_days").value = data.duration_days;
    document.getElementById("cough_severity").value = data.cough_severity;
    document.getElementById("respiratory_distress").value = data.respiratory_distress;
    document.getElementById("oxygen_saturation").value = data.oxygen_saturation;

    document.getElementById("chest_pain").checked = data.chest_pain;
    document.getElementById("lethargy_confusion").checked = data.lethargy_confusion;
    document.getElementById("high_risk_condition").checked = data.high_risk_condition;

    checkSpo2Warning();
}

/**
 * Resets the triage form to initial defaults.
 */
function resetForm() {
    document.getElementById("temperature").value = 37.0;
    document.getElementById("duration_days").value = 1;
    document.getElementById("cough_severity").value = "none";
    document.getElementById("respiratory_distress").value = "none";
    document.getElementById("oxygen_saturation").value = "";
    document.getElementById("chest_pain").checked = false;
    document.getElementById("lethargy_confusion").checked = false;
    document.getElementById("high_risk_condition").checked = false;

    checkSpo2Warning();
}

/**
 * Toggles visibility of collapsible sections (Working Memory, Audit Trail).
 */
function toggleSection(panelId) {
    const panel = document.getElementById(panelId);
    if (!panel) return;

    const isHidden = panel.classList.toggle("hidden");
    const indicator = panel.previousElementSibling?.querySelector(".toggle-indicator");
    if (indicator) {
        indicator.textContent = isHidden ? "▶" : "▼";
    }
}

/**
 * Filters audit trail items by firing status.
 */
function filterAudit(filterType, buttonEl) {
    // Update button active states
    const buttons = document.querySelectorAll(".btn-filter");
    buttons.forEach((btn) => btn.classList.remove("active"));
    buttonEl.classList.add("active");

    const items = document.querySelectorAll(".audit-item");
    items.forEach((item) => {
        const status = item.getAttribute("data-status");
        if (filterType === "all") {
            item.style.display = "block";
        } else if (filterType === "fired" && status === "fired") {
            item.style.display = "block";
        } else if (filterType === "failed" && status === "failed") {
            item.style.display = "block";
        } else {
            item.style.display = "none";
        }
    });
}
