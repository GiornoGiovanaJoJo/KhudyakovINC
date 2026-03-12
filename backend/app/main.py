from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import team, services, portfolio, chat, auth, leads

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="KhudyakovINC API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(team.router, prefix="/api/team", tags=["Team"])
app.include_router(services.router, prefix="/api/services", tags=["Services"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
