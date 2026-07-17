from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

def setup_telemetry(service_name: str, poc_id: str, phase: int):
    resource = Resource.create({
        "service.name": service_name,
        "poc.id": poc_id,
        "poc.phase": str(phase),
    })

    provider = TracerProvider(resource=resource)
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    return trace.get_tracer(service_name)