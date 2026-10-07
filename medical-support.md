# Medical support scope

This is the requested repository-evidence inventory, NOT an enabled catalog, device capability list, or patient result set. The database MedicalParameter records remain authoritative. The viewer accepts arbitrary entries, with stable database IDs, enablement, reviewed many-to-many system mappings, evidence category and source notes. No name whitelist, automatic diagnosis, clinical calculation or name-based organ inference is implemented.

## Inventory and mapping keys

| System key | Requested parameters and evidence |
| --- | --- |
| cardiovascular | Measurements: heart rate, resting/recovery heart rate, SDNN, RMSSD, systolic/diastolic BP, heart-rate zone durations, ECG voltage, R-R intervals where supplied. Labs: total cholesterol, HDL, triglycerides, hsCRP. Extraction: LDL, troponin, CK-MB, BNP. Calculated/face-scan: cardiovascular disease, heart-attack, stroke and hypertension risk; BP_RPP, BP_TAU, irregular-heartbeat count, SCORE2, Reynolds. |
| respiratory | Respiratory/breathing rate, sleep breathing rate, SpO2, VO2 max. VO2 max is cardiorespiratory fitness, not a lung diagnosis. |
| sleep_stress | Sleep duration; deep/light/REM duration; awake time; time in bed; bedtime duration; interruptions/awakenings; efficiency; sleep/wake-up latency; naps. Estimated sleep, stress, MSI, mental, readiness and recovery scores. Not direct brain-function measurements. |
| metabolic | Blood glucose, fasting glucose, HbA1c, CGM readings. Derived CGM average/highest/lowest, below/in/above-target percentages and variability CV%. Calculated/face-scan METS-IR, diabetes, elevated fasting-glucose, elevated HbA1c and overall metabolic risk; HDL/total-cholesterol and triglyceride risk channels. |
| liver | AST/SGOT, ALT/SGPT, albumin and platelets used in implemented calculations. Extraction: ALP, bilirubin (subtypes not established). Calculated fatty-liver risk, BARD, NAFLD fibrosis score, FNI. |
| renal | Extraction: creatinine, BUN, sodium, potassium, chloride, CO2, calcium. GFR categorization does not establish an enabled eGFR parameter or calculation. |
| thyroid | Extraction: TSH, T3, T4. Free versus total T3/T4 not established. |
| blood_immune | Labs/extraction: hemoglobin, hematocrit, RBC, WBC, platelets, WBC differential (no fixed cell enumeration), CRP, hsCRP, ESR. CRP and hsCRP remain separate IDs/entries. |
| body_composition | Measurements/device/profile: height, weight, BMI, body-fat percentage, skeletal muscle mass, bone mass. Face-scan/derived: waist circumference, waist-to-height ratio, ABSI, calculated BMI. Related extraction: calcium. Bone mass is not a bone-density scan. |
| temperature | Body temperature, basal body temperature, skin temperature, sleep skin-temperature deviation. |
| digestive | Questionnaire assessments: Rome IV and Manning symptom criteria. No established fixed stool-test or microbiome panel. |
| fitness | Steps, floors, active minutes, low/moderate/high activity durations, active/basal/total calories, calorie intake; total/walking/running/cycling/swimming/wheelchair distance; speed, pace, cadence, power; elevation gain/loss, ascent/descent; swimming lengths and distance per stroke. Calculated/estimated activity, strain, biological age/SensorAge, overall health, physical, physiological, risk and vital scores. Wellness/performance, not strictly medical tests. |

Cross-system examples: platelets can map to liver and blood_immune; calcium to renal and body_composition; hsCRP to cardiovascular and blood_immune; VO2 max to respiratory and fitness. These are navigation associations, not claims of organ disease. The host must review mappings, not infer them from labels.

## Unconfirmed evidence

Insulin appears in report categorization only. Vitamin D appears in report-monitoring labels and mock clinical data; vitamin B12 and ferritin in mock clinical data. CBC, LFT, RFT, lipid profile and thyroid profile are panel labels, not proof of individually configured constituents. None is enabled by this document. A host may supply an actual enabled database entry while still labeling its repository evidence as unconfirmed.

## Geometry limits

Existing meshes support heart, lungs/airway, brain, pancreas, liver, kidneys and digestive organs. Thyroid, blood/immune, muscles/bones, temperature and whole-body fitness are list-only groups: no invented meshes or substituted organ highlights. Existing bladder and gallbladder anatomy remains selectable without inventing parameter associations. Parameter metadata never changes fictional demo severity colors.

## Host integration

Pass `medicalParameters` into `AnatomyApp` or `AnatomyScreen` using `MedicalParameter` from `lib/medical_parameters.dart`. `null` means disconnected, `[]` means a loaded empty catalog. Disabled records are hidden; unknown or missing system mappings remain visible under Unmapped parameters. Names are displayed as supplied; no list of parameter names is compiled into the app. Distinct database IDs must be retained even when display names overlap.

This repository has no backend schema, endpoint or credentials. Fetching/authentication, database-to-model adaptation, device availability and patient observations belong to the host and are not implemented here. Replace the supplied list on host rebuild after catalog refresh. The current browser is metadata-only and does not display values, units, reference ranges or clinical assessments. The inventory does not implement the underlying tests, extraction pipelines or score calculations.
