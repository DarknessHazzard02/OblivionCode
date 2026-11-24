# ===============================================
# <App> — servidor local
# Author: Haz
# ===============================================
from waitress import serve

from app import create_app

if __name__ == "__main__":
    serve(create_app(), host="127.0.0.1", port=8080)
