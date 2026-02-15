from typing import List, Literal, Optional, Annotated
from pydantic import BaseModel, Field, field_validator, model_validator

Sense = Literal['maximize', 'minimize']
Ineq = Literal['<=','>=','=']

class Constraint(BaseModel):
    a: Annotated[List[float], Field(min_length=1)]  # coefficients
    sense: Ineq
    b: float

    @model_validator(mode="before")
    @classmethod
    def _accept_legacy_keys(cls, values):
        if not isinstance(values, dict):
            return values
        if "coefficients" in values and "a" not in values:
            values["a"] = values.pop("coefficients")
        if "type" in values and "sense" not in values:
            values["sense"] = values.pop("type")
        if "rhs" in values and "b" not in values:
            values["b"] = values.pop("rhs")
        return values

class LPRequest(BaseModel):
    mode: Literal['numerical','graphical'] = 'numerical'
    n: int = 2
    c: Annotated[List[float], Field(min_length=1)]
    sense: Sense = 'maximize'
    constraints: List[Constraint] = []
    nonneg: bool = True
    
    @field_validator('constraints')
    @classmethod
    def validate_constraint_length(cls, v, info):
        n = info.data.get('n')
        if n and any(len(c.a) != n for c in v):
            raise ValueError('All constraint coefficients must match n variables')
        return v
    

class LPSolution(BaseModel):
    x: List[float]
    objective: float
    success: bool
    message: Optional[str] = None
