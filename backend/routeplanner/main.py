from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from route_planner import get_directions, evaluate_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend origin for better security, e.g., ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RouteRequest(BaseModel):
    origin: str
    destination: str
    mode: str = "walking"

@app.post("/getBestRoutes")
async def get_best_routes(req: RouteRequest):
    try:
        routes = get_directions(req.origin, req.destination, req.mode)
        results = evaluate_routes(routes)

        best_routes = [{
            "score": round(r["score"], 2),
            "avg_aqi": r["avg_aqi"],
            "avg_uv": r["avg_uv"],
            "elevation_gain": r["elevation_gain"],
            "route": r["route"]
        } for r in results]

        return {"routes": best_routes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
