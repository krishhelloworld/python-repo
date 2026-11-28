from fastapi import FastAPI, Path, HTTPException, Query
from pydantic import BaseModel, Field, computed_field
from typing import Any, Optional, Annotated, Literal
import json

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="patient id ")]
    name: Annotated[str, Field(..., description="name of the patient")]
    age: Annotated[int, Field(..., description="age of the patient", lt=100, gt=15)]
    gender: Annotated[
        Literal["male", "female", "other"],
        Field(..., description="gender of the patient"),
    ]
    weight: Annotated[float, Field(..., description="weight of the  patient")]
    height: Annotated[float, Field(..., description="height of the patient")]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight / (self.height) ** 2), 2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 17:
            return "underweight"
        elif self.bmi > 17:
            return "overweight"
        return "fit"


class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None)]
    gender: Annotated[
        Optional[Literal["male", "female", "other"]],
        Field(default=None),
    ]
    weight: Annotated[Optional[float], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None)]


# load data
# write_data
# view_data-> use the link to /view to show all the data
# view_patient()-> return the patient data , using the linke also -> Path
def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data


def write_data(data):
    with open("patients.json", "w") as f:
        json.dump(data, f)


@app.get("/view")
def view():
    data = load_data()
    return data


@app.get("/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="give the id of patient_id ")):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="there no patient exists")
    return data[patient_id]


@app.get("/sort")
def sort_patient(
    sort_by: str = Query(..., description="on the basis of height,weight or bmi"),
    order: str = Query("asc", description="sort in asc or desc order"),
):

    valid_fields = ["height", "weight", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400, detail=f"Invalid Field select from {valid_fields}"
        )
    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400, detail=f"Invalid order select between asn and dsec"
        )
    data = load_data()
    sort_order = True if order == "desc" else False
    sorted_data = sorted(
        data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order
    )
    return sorted_data


@app.post("/create")
def create_data(patient: Patient):
    data = load_data()
    if patient.id in data:
        raise HTTPException(status_code=501, detail="patient already exists")
    data[patient.id] = patient.model_dump(exclude="id")
    write_data(data)
    return JSONResponse(
        status_code=201, content={"message": "patient created successfully"}
    )


def extract_id(patient: dict):
    return patient.keys(), patient.values()


@app.put("/edit/{patient_id}")
def update_patient(patient_id: str, patient_updated: PatientUpdate):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code="501", detail="patient not exists")
    patient_info = data[patient_id]
    patient_updated = (patient_updated).model_dump(exclude_unset=True)
    patient_new_info = {**patient_info, **patient_updated}
    print(patient_new_info)
    patient_new_info = Patient(id=patient_id, **patient_new_info)
    data[patient_id] = patient_new_info.model_dump(exclude="id")
    print(data)
    write_data(data)
    return JSONResponse(
        status_code=201, content={"message": f"data updated of {patient_id}"}
    )
