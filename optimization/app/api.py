from __future__ import annotations

import io

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

from optimization.app.di import (
    get_golden_section_service,
    get_linear_programming_service,
    get_steepest_descent_service,
)
from optimization.app.dto import GoldenSectionRequest, SolveRequest, SteepestDescentRequest
from optimization.app.exceptions import ComputationError, FeatureUnavailableError, InputError, PresentationError
from optimization.app.golden_section_service import GoldenSectionApplicationService
from optimization.app.linear_service import LinearProgrammingService
from optimization.app.mappers import (
    dto_to_golden_section_command,
    dto_to_linear_command,
    dto_to_sd_command,
    golden_section_report_to_dto,
    solution_to_dto,
    steepest_descent_report_to_dto,
)
from optimization.app.steepest_descent_service import SteepestDescentApplicationService
from optimization.infrastructure.logging import configure_logging

API_VERSION = "v1"


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, InputError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, ComputationError):
        return JSONResponse(status_code=400, content={"success": False, "message": str(exc)})  # type: ignore[return-value]
    if isinstance(exc, PresentationError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if isinstance(exc, FeatureUnavailableError):
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    raise HTTPException(status_code=400, detail=str(exc)) from exc


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Optimization Solver", version=API_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/solve")
    def solve_endpoint(req: SolveRequest, service: LinearProgrammingService = Depends(get_linear_programming_service)):
        try:
            command = dto_to_linear_command(req)
            result = service.execute(command)
        except Exception as exc:
            maybe_response = _raise_http_error(exc)
            if maybe_response is not None:
                return maybe_response

        # numerical path
        if req.mode == "numerical" or not result.artifact:
            return solution_to_dto(result.solution)

        payload, media_type = result.artifact
        if media_type == "text/html":
            return HTMLResponse(content=payload.decode("utf-8"))
        return StreamingResponse(io.BytesIO(payload), media_type=media_type)

    @app.post("/optimize/steepest-descent")
    def sd_endpoint(
        req: SteepestDescentRequest,
        service: SteepestDescentApplicationService = Depends(get_steepest_descent_service),
    ):
        try:
            report = service.execute(dto_to_sd_command(req))
            return steepest_descent_report_to_dto(report)
        except Exception as exc:
            maybe_response = _raise_http_error(exc)
            if maybe_response is not None:
                return maybe_response

    @app.post("/optimize/golden-section")
    def golden_section_endpoint(
        req: GoldenSectionRequest,
        service: GoldenSectionApplicationService = Depends(get_golden_section_service),
    ):
        try:
            report = service.execute(dto_to_golden_section_command(req))
            return golden_section_report_to_dto(report)
        except Exception as exc:
            maybe_response = _raise_http_error(exc)
            if maybe_response is not None:
                return maybe_response

    return app


app = create_app()
