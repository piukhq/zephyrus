from typing import Optional

import falcon
import opentracing
from opentracing.ext import tags as ot_tags


class OpentracingMiddleware:
    def __init__(self, tracer: opentracing.Tracer, store_scope_in_req: bool = True):
        self._current_scopes: dict[falcon.Request, opentracing.Scope] = {}
        self.store_scope_in_req = store_scope_in_req
        self.tracer = tracer

    def get_span(self, req: falcon.Request) -> Optional[opentracing.Span]:
        return self._current_scopes.get(req, None)

    def process_request(self, req: falcon.Request, resp: falcon.Response):
        operation_name = req.relative_uri
        headers = {k.lower(): v for k, v in req.headers.items()}

        try:
            span_ctx = self.tracer.extract(opentracing.Format.HTTP_HEADERS, headers)
            scope = self.tracer.start_active_span(operation_name, child_of=span_ctx)
        except (
            opentracing.InvalidCarrierException,
            opentracing.SpanContextCorruptedException,
        ):
            scope = self.tracer.start_active_span(operation_name)

        self._current_scopes[req] = scope

        span = scope.span
        span.set_tag(ot_tags.COMPONENT, "Falcon")
        span.set_tag(ot_tags.HTTP_METHOD, req.method)
        span.set_tag(ot_tags.HTTP_URL, req.uri)
        span.set_tag(ot_tags.SPAN_KIND, ot_tags.SPAN_KIND_RPC_SERVER)

        if self.store_scope_in_req:
            req.context.scope = scope

        self.before_request_span(span, req, headers)

    def before_request_span(self, span: opentracing.Span, req: falcon.Request, headers: dict[str, str]):
        pass

    def process_response(
        self,
        req: falcon.Request,
        resp: falcon.Response,
        resource: object,
        req_succeeded: bool,
    ):
        scope = self._current_scopes.pop(req, None)
        if not scope:
            return

        scope.span.set_tag(ot_tags.HTTP_STATUS_CODE, resp.status[:3])
        if not req_succeeded:
            scope.span.set_tag(ot_tags.ERROR, True)

        scope.close()


class AzureTracing(OpentracingMiddleware):
    def before_request_span(self, span: opentracing.Span, req: falcon.Request, headers: dict[str, str]):
        if "x-azure-ref" in headers:
            span.set_tag("azure.ref", headers["x-azure-ref"])
