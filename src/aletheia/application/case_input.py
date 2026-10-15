"""Versioned single-case intake and explicit UCI-to-frozen-pipeline mapping.

Administrative labels come from checksum-pinned IDS_mapping.csv. Count ceilings
are transport/computation bounds, not observed maxima or clinical normal ranges.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

COUNT_MAX = 2_147_483_647
ADMISSION_TYPES = {
    "1": "Emergency",
    "2": "Urgent",
    "3": "Elective",
    "4": "Newborn",
    "5": "Not Available",
    "6": "NULL (source category)",
    "7": "Trauma Center",
    "8": "Not Mapped",
}
ADMISSION_SOURCES = {
    "1": "Physician Referral",
    "2": "Clinic Referral",
    "3": "HMO Referral",
    "4": "Transfer from a hospital",
    "5": "Transfer from a Skilled Nursing Facility",
    "6": "Transfer from another health care facility",
    "7": "Emergency Room",
    "8": "Court/Law Enforcement",
    "9": "Not Available (9)",
    "10": "Transfer from critical access hospital",
    "11": "Normal Delivery",
    "12": "Premature Delivery",
    "13": "Sick Baby",
    "14": "Extramural Birth",
    "15": "Not Available (15)",
    "17": "NULL (source category)",
    "18": "Transfer from another home health agency",
    "19": "Readmission to same home health agency",
    "20": "Not Mapped",
    "21": "Unknown/Invalid",
    "22": "Transfer from same-facility inpatient care",
    "23": "Born inside this hospital",
    "24": "Born outside this hospital",
    "25": "Transfer from ambulatory surgery center",
    "26": "Transfer from hospice",
}


class CaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True)
    admission_type_id: Literal["1", "2", "3", "4", "5", "6", "7", "8"]
    admission_source_id: Literal[
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "17",
        "18",
        "19",
        "20",
        "21",
        "22",
        "23",
        "24",
        "25",
        "26",
    ]
    time_in_hospital: int = Field(ge=1, le=14)
    num_lab_procedures: int = Field(ge=1, le=COUNT_MAX)
    num_procedures: int = Field(ge=0, le=COUNT_MAX)
    num_medications: int = Field(ge=1, le=COUNT_MAX)
    number_outpatient: int = Field(ge=0, le=COUNT_MAX)
    number_emergency: int = Field(ge=0, le=COUNT_MAX)
    number_inpatient: int = Field(ge=0, le=COUNT_MAX)
    number_diagnoses: int = Field(ge=1, le=COUNT_MAX)
    max_glu_serum: Literal["None", "Norm", ">200", ">300"]
    A1Cresult: Literal["None", "Norm", ">7", ">8"]
    diabetesMed: Literal["Yes", "No"]

    def raw(self):
        """The research pipeline was fitted with string-valued source columns."""
        return {key: str(value) for key, value in self.model_dump().items()}


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    schema_version: Literal["case-input-v1"]
    model_version: str = Field(pattern=r"^[1-9][0-9]*$")
    inputs: CaseInput


LABELS = {
    "admission_type_id": "Admission type",
    "admission_source_id": "Admission source",
    "time_in_hospital": "Time in hospital",
    "num_lab_procedures": "Laboratory procedures",
    "num_procedures": "Procedures",
    "num_medications": "Distinct medications",
    "number_outpatient": "Outpatient visits in the preceding year",
    "number_emergency": "Emergency visits in the preceding year",
    "number_inpatient": "Inpatient visits in the preceding year",
    "number_diagnoses": "Diagnoses",
    "max_glu_serum": "Maximum glucose result",
    "A1Cresult": "A1C result",
    "diabetesMed": "Diabetes medication prescribed",
}
OPTIONS = {
    "admission_type_id": ADMISSION_TYPES,
    "admission_source_id": ADMISSION_SOURCES,
    "max_glu_serum": {
        "None": "Not measured",
        "Norm": "Normal (source category)",
        ">200": "Above 200 (source category)",
        ">300": "Above 300 (source category)",
    },
    "A1Cresult": {
        "None": "Not measured",
        "Norm": "Normal (source category)",
        ">7": "Above 7%",
        ">8": "Above 8%",
    },
    "diabetesMed": {"Yes": "Yes", "No": "No"},
}


def field_mapping():
    fields = []
    schema = CaseInput.model_json_schema()["properties"]
    for name in CaseInput.model_fields:
        numeric = name not in OPTIONS
        fields.append(
            {
                "field": name,
                "label": LABELS[name],
                "required": True,
                "control": "number" if numeric else "select",
                "options": [
                    {"value": v, "label": label}
                    for v, label in OPTIONS.get(name, {}).items()
                ],
                "minimum": schema[name].get("minimum"),
                "maximum": schema[name].get("maximum"),
                "unit": "days"
                if name == "time_in_hospital"
                else ("count" if numeric else "category"),
                "conversion": "Base-10 integer to source string"
                if numeric
                else "Selected option to exact source category",
                "help": (
                    "Required whole number. Count ceiling is a computation limit, "
                    "not a clinical range."
                )
                if numeric and name != "time_in_hospital"
                else "Required; use the recorded encounter value.",
            }
        )
    return {"schema_version": "case-input-v1", "fields": fields}
