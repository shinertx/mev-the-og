from fastapi import FastAPI
import uvicorn

def launch_dashboard(port=8501):
    app = FastAPI()

    @app.get("/")
    def status():
        return {"status": "MEV The OG is live", "pnl": 0}

    uvicorn.run(app, host="0.0.0.0", port=port)
