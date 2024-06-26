import os
import sys

import settings
from app import create_app

app = create_app()

if __name__ == "__main__":
    try:
        import werkzeug.serving
    except ImportError:
        print("Dev requirements must be installed to run the API this way.")
        sys.exit(-1)

    in_debugger = bool(os.getenv("DEBUGGING"))

    werkzeug.serving.run_simple(
        hostname=settings.DEV_HOST,
        port=settings.DEV_PORT,
        application=app,
        use_reloader=not in_debugger,
        use_debugger=not in_debugger,
    )
