from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import falcon


class HealthCheck:
    def on_get(self, req: "falcon.Request", resp: "falcon.Response"):
        resp.media = ""
