from app import app
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=50# -*- coding: utf-8 -*-
from __future__ import annotations

from backend.app import app, db
from backend.core.config import settings

def main():
    with app.app_context():
        db.create_all()
        print(" Banco de dados inicializado com sucesso.")
    
    print(f" A iniciar {settings.APP_NAME} na porta {settings.APP_PORT} (Ambiente: {settings.APP_ENV})...")
    app.run(
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        debug=settings.APP_DEBUG
    )

if __name__ == "__main__":
    main()