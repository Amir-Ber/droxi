import json
from tinydb import Query, TinyDB
from datetime import datetime
from uuid import uuid4
from tinydb_serialization import SerializationMiddleware
from tinydb_serialization.serializers import DateTimeSerializer
from tinydb_serialization import Serializer
from tinydb.storages import JSONStorage, MemoryStorage

db = TinyDB("db.json")


class SetSerializer(Serializer):
    OBJ_CLASS = set

    def encode(self, obj):
        return json.dumps(list(obj))

    def decode(self, s):
        return set(json.loads(s))


serialization = SerializationMiddleware(JSONStorage)

serialization.register_serializer(DateTimeSerializer(), 'TinyDate')
serialization.register_serializer(SetSerializer(), 'TinySet')

clinic = TinyDB("tinydb/db.json", create_dirs=True, storage=serialization)

patient_requests = clinic.table('PatientRequest')
tasks = clinic.table('Tasks')

_db_instance = TinyDB(storage=MemoryStorage)


def get_patient_requests_table():
    tbl = _db_instance.table("PatientRequest")
    return tbl


def init_db():
    existing_docs = (len(patient_requests))
    if existing_docs > 100:
        return

    # Add some closed requests to the patient_requests table
    generated_requests = [{
        'id': str(uuid4()),
        'patient_id': 'patient1',
        'status': 'Closed',
        'assigned_to': 'Primary',
        'created_date': datetime.now(),
        'updated_date': datetime.now(),
        'messages': [f'message{i}'],
        'medications': [{'code': '1234', 'name': 'Advil 200 mg'}],
    } for i in range(1, 101)]

    patient_requests.insert_multiple(generated_requests)
