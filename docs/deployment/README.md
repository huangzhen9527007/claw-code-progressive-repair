# 部署指南

## 概述

`deployment/` 目录存储 Cloud Code 项目的部署相关文档。包括环境要求、部署步骤、配置说明、监控和维护指南。

## 部署分类

### 1. 开发环境部署
- 本地开发环境搭建
- 依赖安装
- 开发工具配置

### 2. 测试环境部署
- 测试环境配置
- 自动化测试部署
- 集成测试环境

### 3. 生产环境部署
- 生产服务器配置
- 高可用部署
- 安全配置

### 4. 容器化部署
- Docker 镜像构建
- Kubernetes 部署
- 容器编排配置

### 5. 云平台部署
- 各云平台部署指南
- 云服务配置
- 成本优化建议

## 当前部署文档

### [开发环境部署指南](./development-environment.md)（待创建）
描述如何搭建本地开发环境。

### [生产环境部署指南](./production-environment.md)（待创建）
描述生产环境的部署配置。

### [Docker 部署指南](./docker-deployment.md)（待创建）
描述如何使用 Docker 部署 Cloud Code。

## 部署流程

### 1. 环境准备
#### 系统要求
- **操作系统**: Windows 10/11, macOS, Linux
- **运行时**: Bun 1.0+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘空间**: 最低 500MB

#### 依赖安装
```bash
# 安装 Bun
curl -fsSL https://bun.sh/install | bash

# 验证安装
bun --version
```

### 2. 代码获取
```bash
# 克隆项目
git clone https://github.com/your-org/cloud-code.git
cd cloud-code

# 安装依赖
bun install
```

### 3. 构建项目
```bash
# 开发构建
bun run dev

# 生产构建
bun run build
```

### 4. 配置管理
#### 环境变量
```bash
# .env 文件示例
ANTHROPIC_API_KEY=your_api_key_here
OPENAI_COMPAT_API_URL=https://api.openai.com/v1
WECHAT_BRIDGE_ENABLED=true
```

#### 配置文件
- `config/default.json` - 默认配置
- `config/production.json` - 生产配置
- `config/development.json` - 开发配置

### 5. 启动服务
```bash
# 开发模式
bun run dev

# 生产模式
bun run start

# 使用 PM2 进程管理
pm2 start dist/cli.js --name "cloud-code"
```

## 配置说明

### 核心配置项

#### API 配置
```json
{
  "api": {
    "provider": "anthropic",
    "anthropic": {
      "apiKey": "${ANTHROPIC_API_KEY}",
      "baseUrl": "https://api.anthropic.com"
    },
    "openaiCompat": {
      "enabled": true,
      "baseUrl": "https://api.openai.com/v1"
    }
  }
}
```

#### WeChat Bridge 配置
```json
{
  "wechat": {
    "enabled": false,
    "ilink": {
      "appId": "your_app_id",
      "appSecret": "your_app_secret"
    },
    "storage": {
      "path": "~/.wechat-bridge"
    }
  }
}
```

#### 日志配置
```json
{
  "logging": {
    "level": "info",
    "file": {
      "enabled": true,
      "path": "logs/cloud-code.log",
      "maxSize": "10m",
      "maxFiles": "10"
    },
    "console": {
      "enabled": true
    }
  }
}
```

### 环境特定配置

#### 开发环境
- 启用调试日志
- 禁用生产安全检查
- 使用模拟数据

#### 测试环境
- 启用完整测试
- 使用测试 API 密钥
- 隔离的数据存储

#### 生产环境
- 启用安全配置
- 性能优化设置
- 监控和告警配置

## 监控和维护

### 健康检查
```bash
# 健康检查端点
curl http://localhost:3000/health

# 响应示例
{
  "status": "healthy",
  "timestamp": "2026-04-19T09:20:00Z",
  "version": "1.0.0",
  "uptime": "3d 5h 30m"
}
```

### 日志管理
#### 日志位置
- 应用日志: `logs/cloud-code.log`
- 访问日志: `logs/access.log`
- 错误日志: `logs/error.log`

#### 日志轮转
```bash
# 使用 logrotate 配置
/var/log/cloud-code/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
```

### 性能监控
#### 关键指标
- 请求响应时间
- 内存使用情况
- CPU 使用率
- 并发连接数

#### 监控工具
- Prometheus + Grafana
- Datadog
- New Relic
- 自定义监控脚本

### 备份和恢复
#### 数据备份
```bash
# 备份配置和数据
tar -czf backup-$(date +%Y%m%d).tar.gz \
  ~/.claude \
  ~/.wechat-bridge \
  config/
```

#### 恢复流程
1. 停止服务
2. 恢复备份数据
3. 验证数据完整性
4. 重启服务

## 故障排除

### 常见问题

#### 启动失败
**问题**: 服务无法启动
**解决**:
```bash
# 检查端口占用
netstat -tulpn | grep :3000

# 检查日志
tail -f logs/cloud-code.log

# 验证依赖
bun install --frozen-lockfile
```

#### 内存泄漏
**问题**: 内存使用持续增长
**解决**:
```bash
# 监控内存使用
pm2 monit

# 生成堆快照
bun --inspect dist/cli.js

# 分析内存使用
node --inspect-brk dist/cli.js
```

#### API 连接问题
**问题**: 无法连接 API 服务
**解决**:
```bash
# 测试网络连接
curl -v https://api.anthropic.com/v1/messages

# 检查防火墙
sudo ufw status

# 验证 API 密钥
echo $ANTHROPIC_API_KEY
```

### 紧急恢复
#### 服务重启
```bash
# 优雅重启
pm2 restart cloud-code

# 强制重启
pm2 delete cloud-code && pm2 start dist/cli.js
```

#### 回滚部署
```bash
# 回滚到上一个版本
git checkout previous-version
bun install
bun run build
pm2 restart cloud-code
```

## 安全考虑

### 安全配置
- 使用 HTTPS
- 设置防火墙规则
- 定期更新依赖
- 安全审计日志

### 访问控制
- API 密钥管理
- 用户认证和授权
- 速率限制
- IP 白名单

### 数据安全
- 加密敏感数据
- 安全存储凭证
- 数据备份加密
- 安全删除策略

## 扩展部署

### 高可用部署
- 负载均衡配置
- 多实例部署
- 故障转移策略
- 数据同步机制

### 自动扩缩容
- 基于指标的自动扩缩
- 成本优化策略
- 资源预留配置

### 多区域部署
- 地理分布部署
- 数据复制策略
- 区域故障转移

## 相关资源

### 项目文档
- [架构设计](../architecture/README.md)
- [API 文档](../api/README.md)
- [开发指南](../development/README.md)

### 外部工具
- Bun 文档
- PM2 文档
- Docker 文档
- Kubernetes 文档

### 最佳实践
- 12-Factor App
- 云原生应用设计
- DevOps 实践

## 更新日志

### 2026-04-19
- 创建部署指南框架
- 定义部署分类和流程
- 添加配置说明和监控指南

---

**部署是应用生命周期的重要环节。详细的部署文档有助于确保应用在不同环境中的稳定运行和可维护性。**