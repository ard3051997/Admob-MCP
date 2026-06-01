from typing import Optional, List
from pydantic import BaseModel, Field
from .mediation import MediationGroupLine

class AbExperiment(BaseModel):
    name: Optional[str] = None
    experiment_id: Optional[str] = None
    display_name: str
    treatment_traffic_percentage: int = Field(..., ge=1, le=99)
    treatment_mediation_group_lines: List[MediationGroupLine]
    state: str = "RUNNING"
    control_mediation_group_lines: Optional[List[MediationGroupLine]] = None

class ExperimentResult(BaseModel):
    winner: str = Field(..., description="VARIANT_CHOICE_A or VARIANT_CHOICE_B")
    experiment_id: str
