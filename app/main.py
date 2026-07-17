from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from app.logging_config import configure_logging
from app.otel_setup import setup_telemetry
from app.routers import auth, accounts, transactions, budgets, dashboard

configure_logging()
tracer = setup_telemetry("poc-02-finance-api", poc_id="POC-02", phase=1)

app = FastAPI(title="Personal Finance Tracker API")
FastAPIInstrumentor.instrument_app(app)

app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(dashboard.router)

@app.get("/health")
def health():
    return {"status": "ok"}