import logging

import uvicorn
from server.api import api

logger = logging.getLogger(__name__)

app = api.app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)