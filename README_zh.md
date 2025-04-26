# AI Manus

[English](README.md) | 中文

AI Manus 是一个通用的 AI Agent 系统，支持在沙盒环境中运行各种工具和操作。

用 AI Manus 开启你的智能体之旅吧！

## 示例

### Browser Use

* 任务：llm 最新论文

https://github.com/user-attachments/assets/8f7788a4-fbda-49f5-b836-949a607c64ac

### Code Use

* 任务：写一个复杂的 python 示例

https://github.com/user-attachments/assets/5cb2240b-0984-4db0-8818-a24f81624b04



## 环境要求

本项目主要依赖Docker进行开发与部署，需要安装较新版本的Docker：
- Docker 20.10+
- Docker Compose

模型能力要求：
- 兼容OpenAI接口
- 支持FunctionCall
- 支持Json Format输出

推荐使用Deepseek与GPT模型。


## 部署指南

推荐使用Docker Compose进行部署：

```yaml
services:
  frontend:
    image: simpleyyt/manus-frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    restart: unless-stopped
    networks:
      - manus-network
    environment:
      - BACKEND_URL=http://backend:8000

  backend:
    image: simpleyyt/manus-backend
    depends_on:
      - sandbox
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - manus-network
    environment:
      # OpenAI API base URL
      - API_BASE=https://api.openai.com/v1
      # OpenAI API key, replace with your own
      - API_KEY=sk-xxxx
      # LLM model name
      - MODEL_NAME=gpt-4o
      # LLM temperature parameter, controls randomness
      - TEMPERATURE=0.7 
      # Maximum tokens for LLM response
      - MAX_TOKENS=2000
      # Google Search API key for web search capability
      #- GOOGLE_SEARCH_API_KEY=
      # Google Custom Search Engine ID
      #- GOOGLE_SEARCH_ENGINE_ID=
      # Application log level
      - LOG_LEVEL=INFO
      # Docker image used for the sandbox
      - SANDBOX_IMAGE=simpleyyt/manus-sandbox
      # Prefix for sandbox container names
      - SANDBOX_NAME_PREFIX=sandbox
      # Time-to-live for sandbox containers in minutes
      - SANDBOX_TTL_MINUTES=30
      # Docker network for sandbox containers
      - SANDBOX_NETWORK=manus-network

  sandbox:
    image: simpleyyt/manus-sandbox
    command: /bin/sh -c "exit 0"  # prevent sandbox from starting, ensure image is pulled
    restart: "no"
    networks:
      - manus-network

networks:
  manus-network:
    name: manus-network
    driver: bridge
```

保存成`docker-compose.yml`文件，并运行

```shell
docker compose up -d
```

打开浏览器访问<http://localhost:5173>即可访问 Manus。

## 开发指南

### 项目结构

本项目由三个独立的子项目组成：

* `frontend`: manus 前端
* `backend`: Manus 后端
* `sandbox`: Manus 沙盒

### 环境准备

1. 复制配置文件：
```bash
cp .env.example .env
```

2. 修改配置文件：
```
# Model provider configuration
API_KEY=
API_BASE=https://api.openai.com/v1

# Model configuration
MODEL_NAME=gpt-4o
TEMPERATURE=0.7
MAX_TOKENS=2000

# Optional: Google search configuration
#GOOGLE_SEARCH_API_KEY=
#GOOGLE_SEARCH_ENGINE_ID=

# Sandbox configuration
SANDBOX_IMAGE=simpleyyt/manus-sandbox
SANDBOX_NAME_PREFIX=sandbox
SANDBOX_TTL_MINUTES=30
SANDBOX_NETWORK=manus-network

# Log configuration
LOG_LEVEL=INFO
```

### 开发调试

1. 下载项目：
```bash
git clone https://github.com/simpleyyt/ai-manus.git
cd ai-manus
```

2. 运行调试：
```bash
# 相当于 docker compose -f docker-compose-development.yaml up
./dev.sh up
```

各服务会以reload模式运行，代码改动会自动重新加载。暴露的端口如下：
- 5173: Web前端端口
- 8000: Server API服务端口
- 8080: Sandbox API服务端口
- 5900: Sandbox VNC端口
- 9222: Sandbox Chrome浏览器CDP端口

3. 当依赖变化时（requirements.txt或package.json），清理并重新构建：
```bash
# 清理所有相关资源
./dev.sh down -v

# 重新构建镜像
./dev.sh build

# 调试运行
./dev.sh up
```

### 镜像发布

```bash
export IMAGE_REGISTRY=your-registry-url
export IMAGE_TAG=latest

# 构建镜像
./run build

# 推送到相应的镜像仓库
./run push
```
