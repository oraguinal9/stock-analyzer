#!/bin/bash
# 股票分析助手 - 服务器部署脚本
# 适用：Ubuntu 20.04+ / Debian 11+

set -e

echo "=========================================="
echo "  股票分析助手 - 一键部署脚本"
echo "=========================================="

# 检查是否 root
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行：sudo ./deploy.sh"
    exit 1
fi

# 安装 Docker
if ! command -v docker &> /dev/null; then
    echo "[1/5] 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
else
    echo "[1/5] Docker 已安装"
fi

# 安装 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "[2/5] 安装 Docker Compose..."
    apt-get update && apt-get install -y docker-compose
else
    echo "[2/5] Docker Compose 已安装"
fi

# 克隆代码（如果还没有）
if [ ! -d "/opt/stock-analyzer" ]; then
    echo "[3/5] 下载代码..."
    mkdir -p /opt/stock-analyzer
    # 这里可以改成你的 GitHub 仓库
    # git clone <your-repo> /opt/stock-analyzer
    # 暂时从本地复制
    echo "请手动上传代码到 /opt/stock-analyzer"
else
    echo "[3/5] 代码已存在"
fi

cd /opt/stock-analyzer

# 创建 .env 文件
if [ ! -f ".env" ]; then
    echo "[4/5] 创建配置文件..."
    cp .env.example .env
    echo "请编辑 .env 文件填入 API Key"
else
    echo "[4/5] 配置文件已存在"
fi

# 启动服务
echo "[5/5] 启动服务..."
docker-compose up -d --build

echo ""
echo "=========================================="
echo "  部署完成！"
echo "  访问地址：http://$(hostname -I | awk '{print $1}'):8000"
echo "=========================================="
echo ""
echo "常用命令："
echo "  查看日志：docker-compose logs -f"
echo "  重启服务：docker-compose restart"
echo "  停止服务：docker-compose down"
