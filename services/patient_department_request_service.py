
from collections import defaultdict

from tinydb import Query, where

from .patient_request_service import PatientRequestService
from models.patient_task import PatientTask
from models.patient_request import PatientRequest
from db.db_tinydb import get_patient_requests_table
from uuid import uuid4


class DepartmentPatientRequestService(PatientRequestService):

    def update_requests(self, tasks: list[PatientTask]):
        table = get_patient_requests_table()

        # Group by (patient_id, assigned_to)
        grouped = defaultdict(list)
        for task in tasks:
            key = (task.patient_id, task.assigned_to)
            grouped[key].append(task)

        # NEW: Remove all open requests for all affected patients, regardless of department
        q = Query()
        patient_ids = {task.patient_id for task in tasks}
        for patient_id in patient_ids:
            for item in table.search((q.patient_id == patient_id) & (q.status == "Open")):
                table.remove(doc_ids=[item.doc_id])


        # Insert new/updated requests for each (patient, department)
        for (patient_id, department), tasks_group in grouped.items():
            open_tasks = [t for t in tasks_group if t.status == "Open"]
            all_closed = len(open_tasks) == 0

            if all_closed:
                # CLOSED request (medications empty)
                request = PatientRequest(
                    id=str(uuid4()),
                    patient_id=patient_id,
                    status="Closed",
                    assigned_to=department,
                    department=department,
                    created_date=min(t.created_date for t in tasks_group),
                    updated_date=max(t.updated_date for t in tasks_group),
                    messages=[t.message for t in tasks_group],
                    task_ids=[t.id for t in tasks_group],
                    medications=[],
                    pharmacy_id=tasks_group[0].pharmacy_id,
                )
            else:
                # OPEN request
                meds_dict = {}
                for t in open_tasks:
                    for med in t.medications:
                        meds_dict[(med.code, med.name)] = {"code": med.code, "name": med.name}
                medications = list(meds_dict.values())

                request = PatientRequest(
                    id=str(uuid4()),
                    patient_id=patient_id,
                    status="Open",
                    assigned_to=department,
                    department=department,
                    created_date=min(t.created_date for t in open_tasks),
                    updated_date=max(t.updated_date for t in open_tasks),
                    messages=[t.message for t in open_tasks],
                    task_ids=[t.id for t in open_tasks],
                    medications=medications,
                    pharmacy_id=open_tasks[0].pharmacy_id,
                )

            table.insert(request.model_dump(mode="json"))

        # For debugging: show all open requests after update