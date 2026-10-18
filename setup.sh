#!/bin/bash

# 此脚本用于以不同方式配置和运行晨间市场简报助手。

show_help() {
    echo "晨间市场简报助手启动脚本"
    echo ""
    echo "用法：./setup.sh [选项]"
    echo ""
    echo "选项："
    echo "  --docker        使用 Docker Compose 启动两个服务"
    echo "  --local         在本地启动两个服务"
    echo "  --fastapi       仅在本地启动 FastAPI 服务"
    echo "  --streamlit     仅在本地启动 Streamlit 服务"
    echo "  --help          显示帮助信息"
    echo ""
    echo "示例："
    echo "  ./setup.sh --docker     # 使用 Docker 启动两个服务"
    echo "  ./setup.sh --local      # 在本地启动两个服务"
    echo ""
}

setup_secrets() {
    # 若 .streamlit 目录不存在则创建
    if [ ! -d ".streamlit" ]; then
        echo "正在创建 .streamlit 目录……"
        mkdir -p .streamlit
    fi

    # 若 secrets.toml 文件不存在则创建
    if [ ! -f ".streamlit/secrets.toml" ]; then
        echo "正在创建 .streamlit/secrets.toml 文件……"
        echo '[server]
API_URL = "http://localhost:8000"' > .streamlit/secrets.toml
        echo "配置文件创建成功。"
    else
        echo "配置文件已存在。"
    fi
}

run_docker() {
    echo "正在通过 Docker Compose 启动服务……"
    docker-compose up --build
}

run_local() {
    echo "正在配置本地开发环境……"
    setup_secrets
    
    # 检查 Python 虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "正在创建 Python 虚拟环境……"
        python -m venv venv
    fi
    
    # 激活虚拟环境
    echo "正在激活虚拟环境……"
    source venv/bin/activate
    
    # 安装依赖
    echo "正在安装依赖……"
    pip install -r requirements.txt
    
    # 运行两个服务
    echo "正在启动 FastAPI 和 Streamlit 服务……"
    echo "正在 8000 端口启动 FastAPI……"
    uvicorn orchestrator.orchestrator:app --host 0.0.0.0 --port 8000 &
    FASTAPI_PID=$!
    
    # 等待 FastAPI 启动
    echo "正在等待 FastAPI 启动……"
    sleep 5
    
    echo "正在 8501 端口启动 Streamlit……"
    streamlit run streamlit_app/app.py
    
    # Streamlit 退出时停止 FastAPI
    kill $FASTAPI_PID
}

run_fastapi() {
    echo "正在配置 FastAPI 服务……"
    
    # 检查 Python 虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "正在创建 Python 虚拟环境……"
        python -m venv venv
    fi
    
    # 激活虚拟环境
    echo "正在激活虚拟环境……"
    source venv/bin/activate
    
    # 安装依赖
    echo "正在安装依赖……"
    pip install -r requirements.txt
    
    # 运行 FastAPI 服务
    echo "正在 8000 端口启动 FastAPI……"
    uvicorn orchestrator.orchestrator:app --host 0.0.0.0 --port 8000
}

run_streamlit() {
    echo "正在配置 Streamlit 服务……"
    setup_secrets
    
    # 检查 Python 虚拟环境是否存在
    if [ ! -d "venv" ]; then
        echo "正在创建 Python 虚拟环境……"
        python -m venv venv
    fi
    
    # 激活虚拟环境
    echo "正在激活虚拟环境……"
    source venv/bin/activate
    
    # 安装依赖
    echo "正在安装依赖……"
    pip install -r requirements.txt
    
    # 运行 Streamlit 服务
    echo "正在 8501 端口启动 Streamlit……"
    streamlit run streamlit_app/app.py
}

# 处理命令行参数
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    --docker)
        run_docker
        ;;
    --local)
        run_local
        ;;
    --fastapi)
        run_fastapi
        ;;
    --streamlit)
        run_streamlit
        ;;
    --help)
        show_help
        ;;
    *)
        echo "未知选项：$1"
        show_help
        exit 1
        ;;
esac
