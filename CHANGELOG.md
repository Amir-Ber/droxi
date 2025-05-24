# Implementation Change Log

**Environment:**  
- macOS Sequoia 15.4.1 (24E263) on MacBook Pro (Intel)  
- Python 3.12.10 (venv)  
- PyCharm 2024.1

| File | What Changed | Way It Was Changed | Assumptions |
|------|--------------|--------------------|-------------|
| `services/patient_department_request_service.py` | Added department-aware merging, correct open/closed logic, de‑dup meds, removal of stale records. | • Group tasks by `(patient_id, assigned_to)`.<br>• On each batch: remove previous rows for that combo, then insert a single fresh record.<br>• Translate `Medication` objects → unique dict list.<br>• Insert `Closed` request when **all** tasks closed; otherwise `Open`. | External system delivers all updates since last tick; TinyDB used as persistence. |
| `db/db_tinydb.py` | Encapsulated TinyDB singleton + helper to fetch `PatientRequest` table. | Wrapped DB instance in `_db_instance`; added `get_patient_requests_table()`; removed noisy debug & unused helpers. | TinyDB tables are light‑weight; single process access. |
| `clinic_manager.py` | Plugged new service into manager. | Passed service object into `ClinicManager` and delegated update calls. | `ClinicManager` remains orchestrator only. |
| `tests/config.py` | Disabled auto‑generation of 100 closed requests during CI. | Added `generate_requests` flag. | Keeps unit tests deterministic. |

