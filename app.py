from flask import Flask
import requests
import os

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# 配置 OpenTelemetry
resource = Resource.create({"service.name": "my-demo-app"})  # 修改为你应用的名字

# OTLP exporter 配置 (使用 Jaeger 作为后端)
# 确认 jaeger/otel 运行在 localhost 4317
otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")

# Tracer 提供者
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(tracer_provider)

# 获取 tracer
tracer = trace.get_tracer(__name__)

# 创建 Flask 应用
app = Flask(__name__)

# 自动检测 Flask 和 Requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()


@app.route("/")
def hello_world():
    with tracer.start_as_current_span("hello_world_span"):
        response = requests.get("https://www.example.com")  # 添加一个外部调用
        return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
