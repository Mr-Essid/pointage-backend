from fastapi import FastAPI
import uvicorn
from controllers.controller_admin import admin_router
from controllers.controller_employer import employer_route
from controllers.controller_history import history_route, mqttApp

app = FastAPI()


@app.get("/")
def home_page():
    return "Hello Man"


mqttApp.init_app(app)

app.include_router(admin_router, tags=["Admin"])
app.include_router(employer_route, tags=["Employer"])
app.include_router(history_route, tags=["History"])

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True, host="0.0.0.0")
