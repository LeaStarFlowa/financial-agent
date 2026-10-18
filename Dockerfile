FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# 设置 Streamlit 访问 API 的地址
# 容器内的 FastAPI 服务地址为 fastapi:8000
ENV API_URL=http://fastapi:8000

# 暴露 FastAPI 与 Streamlit 的端口
EXPOSE 8000 8501

# 创建用于启动两个服务的入口脚本
RUN echo '#!/bin/bash\n\
uvicorn orchestrator.orchestrator:app --host 0.0.0.0 --port 8000 &\n\
FASTAPI_PID=$!\n\
echo "FastAPI 已启动，进程号： $FASTAPI_PID"\n\
# 等待 FastAPI 启动\n\
sleep 5\n\
# 启动 Streamlit\n\
streamlit run streamlit_app/app.py --server.port 8501 --server.address 0.0.0.0\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# 运行入口脚本
CMD ["/app/entrypoint.sh"]