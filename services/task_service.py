from collections.abc import Iterable
from tinydb import Query, where
from models.patient_task import PatientTask
from models.patient_request import PatientRequest
import db.db_tinydb as db

from operator import attrgetter

task_date_getter = attrgetter('updated_date')

Task = Query()


class TaskService:

    def updates_tasks(self, tasks: list[PatientTask]):
        # Question : This code is the result of a limitation by TinyDB. What is the issue and what feature
        # would a more complete DB solution offer ?
        # Answer :
        # TinyDB doesn’t support bulk upserts, so we have to loop through each task
        # and upsert it one by one. This works fine for small datasets, but it can get
        # pretty slow when you’re dealing with lots of tasks — each .upsert() call
        # is a separate write operation.
        #
        # In a more complete DB (like MongoDB or PostgreSQL), you’d do this in a single,
        # efficient batch operation:
        #
        # ▶ MongoDB:
        #   collection.bulk_write([
        #       UpdateOne({'_id': task.id}, {'$set': task_dict}, upsert=True)
        #   ])
        #
        # ▶ PostgreSQL:
        #   INSERT INTO tasks (id, status, ...)
        #   VALUES
        #       ('task1', 'Open'),
        #       ('task2', 'Closed')
        #   ON CONFLICT (id) DO UPDATE SET status = EXCLUDED.status;
        #
        # These approaches are faster, more atomic, and better for large-scale data updates.
        # Unfortunately, TinyDB doesn’t offer this kind of bulk operation, so we’re stuck
        # looping one-by-one here.
        for task in tasks:
            db.tasks.upsert(task.model_dump(), Task.id == task.id)

    def get_open_tasks(self) -> Iterable[PatientTask]:
        return (PatientTask(**task_doc) for task_doc in db.tasks.search(where("status") == 'Open'))