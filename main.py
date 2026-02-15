from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, HTMLResponse
from models import LPRequest
from interfaces import ISolver, IRenderer
from solvers import SciPySolver
from renderers import MatplotlibRenderer
import io


app = FastAPI(title="SOLID LP Solver")

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
def get_solver() -> ISolver:
    return SciPySolver()

def get_renderer() -> IRenderer:
    return MatplotlibRenderer()

@app.post("/solve")
def solve_endpoint(req: LPRequest, solver: ISolver = Depends(get_solver), renderer: IRenderer = Depends(get_renderer)):
    if req.mode == 'graphical' and req.n not in (2, 3):
        raise HTTPException(status_code=400, detail="Graphical mode requires 2 or 3 variables")
    sol = solver.solve(req)
    if not sol.success:
        return JSONResponse(status_code=400, content=sol.dict())

    if req.mode == 'numerical':
        return sol
    try:
        content = renderer.render_graph(req, sol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if isinstance(content, tuple) and len(content) == 2:
        body, media_type = content
        if media_type == 'text/html':
            return HTMLResponse(content=body.decode('utf-8'))
        else:
            return StreamingResponse(io.BytesIO(body), media_type=media_type)
    return StreamingResponse(io.BytesIO(content), media_type='image/png')
