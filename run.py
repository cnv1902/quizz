"""
Entrypoint để chạy HanziQuizz server.
Chạy: python run.py
hoặc: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["*.db", "*.db-wal", "*.db-shm"],
    )
