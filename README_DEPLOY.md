# 📦 股票分析助手 - 部署指南

## 方式一：Docker 部署（推荐）

### 1. 准备环境

```bash
# 安装 Docker（Ubuntu/Debian）
curl -fsSL https://get.docker.com | sh

# 安装 Docker Compose
apt-get install -y docker-compose
```

### 2. 部署

```bash
# 上传代码到服务器
cd /opt/stock-analyzer

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入 API Key
nano .env

# 一键启动
docker-compose up -d --build
```

### 3. 访问

```
http://你的服务器IP:8000
```

### 4. 常用命令

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 更新代码
git pull
docker-compose up -d --build
```

---

## 方式二：直接部署

### 1. 安装 Python 3.11+

```bash
# Ubuntu
apt-get update
apt-get install -y python3 python3-pip python3-venv

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 后台运行

```bash
# 使用 systemd（推荐）
cat > /etc/systemd/system/stock-analyzer.service << EOF
[Unit]
Description=Stock Analyzer
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/stock-analyzer
Environment="PATH=/opt/stock-analyzer/venv/bin"
ExecStart=/opt/stock-analyzer/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable stock-analyzer
systemctl start stock-analyzer
```

---

## 方式三：PaaS 平台（最简单）

### Railway

1. 注册 https://railway.app
2. 连接 GitHub 仓库
3. 自动部署，无需配置

### Zeabur

1. 注册 https://zeabur.com
2. 导入项目
3. 添加环境变量 `EM_API_KEY` 和 `QWEN_API_KEY`

---

## 域名和 HTTPS

### 1. Nginx 反向代理

```bash
# 安装 Nginx
apt-get install -y nginx

# 配置
cp nginx.conf /etc/nginx/nginx.conf
nginx -t
systemctl restart nginx
```

### 2. 免费 SSL 证书

```bash
# 安装 Certbot
apt-get install -y certbot python3-certbot-nginx

# 获取证书
certbot --nginx -d your-domain.com
```

---

## 环境变量

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `EM_API_KEY` | 东方财富妙想 API Key | 是 |
| `QWEN_API_KEY` | 千问 AI API Key | 否 |
| `HOST` | 监听地址 | 默认 0.0.0.0 |
| `PORT` | 监听端口 | 默认 8000 |

---

## 故障排查

### 服务启动失败

```bash
# 查看日志
docker-compose logs web

# 检查端口占用
netstat -tlnp | grep 8000
```

### API 请求失败

- 检查服务器能否访问外网
- 确认 API Key 有效
- 查看 `data/logs/` 目录下的日志

### 内存不足

```bash
# 限制内存
docker-compose up -d --build --force-recreate
```

---

## 性能优化

- **生产环境** 建议使用 Gunicorn + Uvicorn workers
- **数据库** 大量用户时切换到 PostgreSQL
- **缓存** Redis 缓存热点数据
- **CDN** 静态文件上 CDN 加速

---

## 安全建议

1. 配置防火墙只开放必要端口
2. 使用 HTTPS 加密传输
3. 定期更新依赖
4. 设置 API 请求限流
5. 添加用户认证系统
