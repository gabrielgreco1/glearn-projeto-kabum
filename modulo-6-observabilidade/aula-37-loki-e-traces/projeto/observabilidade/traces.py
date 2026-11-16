"""Traces com OpenTelemetry. O Prefect 3 já cria um span para cada flow run e um para cada task run, filhos um do
outro, quando há para onde mandar: este arquivo liga o envio. Dentro das tasks, cada pedido à loja (o cliente httpx
do projeto) e cada comando ao Postgres viram spans filhos. Tudo vai por OTLP para o Collector
(OTEL_EXPORTER_OTLP_ENDPOINT, padrão http://localhost:4318), que entrega ao Tempo."""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from observabilidade import logs, metricas

rastreador = trace.get_tracer("kabum")


def configurar():
    """Liga o envio dos spans e a instrumentação. Chamar duas vezes não liga de novo."""
    if isinstance(trace.get_tracer_provider(), TracerProvider):
        return
    provedor = TracerProvider(resource=Resource.create({"service.name": logs.SERVICO}))
    provedor.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))  # junta os spans e manda em lotes, sem travar
    trace.set_tracer_provider(provedor)
    # Só o cliente que fala com a loja: instrumentar o httpx inteiro pegaria também o cliente do próprio Prefect.
    HTTPXClientInstrumentor.instrument_client(metricas.cliente)
    PsycopgInstrumentor().instrument(enable_commenter=False)  # um span para cada comando ao Postgres
