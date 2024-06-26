import json

import falcon

from app import queue


class HealthCheck:
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        resp.media = ""


class LivezCheck:
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        resp.status = falcon.HTTP_204


class ReadyzCheck:
    def on_get(self, req: falcon.Request, resp: falcon.Response):
        resp.status = falcon.HTTP_204

        ok, err = queue.is_available()
        if not ok:
            resp.status = falcon.HTTP_500
            resp.media = json.dumps({"error": err})
