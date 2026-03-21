from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import engine, Base
from .routers import team, services, portfolio, chat, auth, leads, upload, users, ai, push, projects, tasks
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'admin'"))
        except Exception:
            pass
    yield


app = FastAPI(
    title="KhudyakovINC API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost",
        "https://localhost",
        "capacitor://localhost",
        "http://leads.khudyakov-inc.ru",
        "https://leads.khudyakov-inc.ru",
        "http://khudyakov-inc.ru",
        "https://khudyakov-inc.ru",
    ],
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
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(push.router, prefix="/api/push", tags=["Push"])

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
