# MemPalace插件集成架构设计

## 概述

本架构文档描述了MemPalace插件在Claude Code项目中的集成架构，包括版本同步机制、环境优先级策略和跨平台兼容性设计。该系统解决了插件版本不同步、环境配置冲突和技能系统集成等关键技术问题。

## 设计原则

### 1. 版本一致性原则
- 插件版本与Python包版本保持同步
- 明确的版本更新记录
- 向后兼容性保证

### 2. 环境隔离原则
- 项目虚拟环境优先于系统环境
- 智能环境降级策略
- 配置驱动的环境管理

### 3. 跨平台兼容原则
- Windows批处理脚本支持
- Unix shell脚本支持
- 统一的配置接口

## 架构组件

### 1. 版本管理层
```
┌─────────────────────────────────────────────┐
│           版本配置文件                      │
├─────────────────────────────────────────────┤
│  • plugin.json (插件版本: 3.3.0)            │
│  • pyproject.toml (Python包版本: 3.3.0)     │
│  • requirements.txt (依赖版本锁定)          │
└─────────────────────────────────────────────┘
```

### 2. 环境管理层
```
┌─────────────────────────────────────────────┐
│         环境优先级策略                       │
├─────────────────────────────────────────────┤
│  1. 项目虚拟环境 (首选)                     │
│     ├─ venv/                                │
│     ├─ Scripts/activate.bat                 │
│     └─ mempalace 3.3.0                      │
│                                             │
│  2. 系统Python环境 (备选)                   │
│     ├─ python3 命令                         │
│     └─ 系统安装的mempalace                  │
│                                             │
│  3. 自动降级机制                            │
│     └─ 项目环境不可用时回退到系统环境        │
└─────────────────────────────────────────────┘
```

### 3. 启动管理层
```
┌─────────────────────────────────────────────┐
│         跨平台启动脚本                       │
├─────────────────────────────────────────────┤
│  • start_mempalace_mcp.bat (Windows)        │
│  • smart_mempalace.sh (Unix)                │
│  • run_mempalace_for_skill.sh (技能专用)    │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │        MCP服务器配置                 │   │
│  │  • command: 启动脚本路径             │   │
│  │  • args: 服务器参数                  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## 配置管理

### 1. 版本同步配置

#### 插件配置文件 (plugin.json)
```json
{
  "name": "mempalace",
  "version": "3.3.0",  // 与pyproject.toml保持一致
  "description": "MemPalace MCP server for Claude Code",
  "mcpServers": {
    "mempalace": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "C:\\Users\\Administrator\\Desktop\\projects\\claudecode\\yuanmaziyuan\\cloud-code-rewrite\\cloud-code-main\\mempalace\\mempalace\\start_mempalace_mcp.bat"
      ]
    }
  }
}
```

#### Python包配置 (pyproject.toml)
```toml
[project]
name = "mempalace"
version = "3.3.0"  // 与plugin.json保持一致
description = "A memory palace for your thoughts"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.24.0",
    "pydantic>=2.5.0"
]
```

### 2. 环境优先级配置

#### Windows启动脚本 (start_mempalace_mcp.bat)
```batch
@echo off
REM 项目虚拟环境优先
set VENV_PATH=%~dp0venv

if exist "%VENV_PATH%\Scripts\activate.bat" (
    call "%VENV_PATH%\Scripts\activate.bat"
    python -m mempalace.mcp_server
    exit /b 0
)

REM 回退到系统环境
echo [WARNING] Virtual environment not found, using system Python
python -m mempalace.mcp_server
```

#### Unix智能脚本 (smart_mempalace.sh)
```bash
#!/bin/bash

# 优先使用项目虚拟环境
PROJECT_VENV_PATH="$(dirname "$0")/venv"

if [ -f "$PROJECT_VENV_PATH/Scripts/activate" ]; then
    source "$PROJECT_VENV_PATH/Scripts/activate"
    python -m mempalace.mcp_server "$@"
    exit 0
fi

# 回退到系统环境
if command -v mempalace >/dev/null 2>&1; then
    echo "[WARNING] Using system mempalace (virtual environment not found)"
    mempalace "$@"
else
    echo "[ERROR] mempalace not found in any environment"
    exit 1
fi
```

#### 技能系统专用脚本 (run_mempalace_for_skill.sh)
```bash
#!/bin/bash
# 为技能调用准备的专用脚本，确保使用正确的环境

PROJECT_DIR="C:/Users/Administrator/Desktop/projects/claudecode/yuanmaziyuan/cloud-code-rewrite/cloud-code-main/mempalace/mempalace"
VENV_PATH="$PROJECT_DIR/venv"

# 强制使用项目虚拟环境
if [ -f "$VENV_PATH/Scripts/activate" ]; then
    source "$VENV_PATH/Scripts/activate"
    python -m mempalace.mcp_server "$@"
else
    echo "[ERROR] Project virtual environment not found at: $VENV_PATH"
    echo "[INFO] Attempting to use system mempalace..."
    mempalace "$@"
fi
```

### 3. MCP服务器配置

#### Claude Code MCP配置
```json
{
  "mcpServers": {
    "mempalace": {
      "command": "cmd.exe",
      "args": [
        "/c",
        "C:\\Users\\Administrator\\Desktop\\projects\\claudecode\\yuanmaziyuan\\cloud-code-rewrite\\cloud-code-main\\mempalace\\mempalace\\start_mempalace_mcp.bat"
      ]
    }
  }
}
```

## 部署架构

### 1. 开发环境部署流程

```
1. 环境准备
   ├─ Python 3.8+ 安装
   ├─ 虚拟环境工具 (venv/virtualenv)
   └─ Git 版本控制

2. 项目设置
   ├─ 克隆 MemPalace 插件
   ├─ 创建虚拟环境
   └─ 安装依赖包
      pip install -e .

3. 版本同步
   ├─ 检查 plugin.json 版本
   ├─ 检查 pyproject.toml 版本
   └─ 确保两者一致 (3.3.0)

4. 配置更新
   ├─ 更新 MCP 服务器配置
   ├─ 部署启动脚本
   └─ 测试环境优先级

5. 集成测试
   ├─ 测试项目环境启动
   ├─ 测试系统环境回退
   └─ 测试技能系统调用
```

### 2. 生产环境部署

#### 单机部署架构
```
┌─────────────────────────────────────────────┐
│          生产服务器                          │
├─────────────────────────────────────────────┤
│  • 系统Python环境 (3.11+)                   │
│  • 项目虚拟环境隔离                         │
│  • 独立的配置目录                           │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │        MemPalace服务                 │   │
│  │  • 版本: 3.3.0                      │   │
│  │  • 端口: 自定义                      │   │
│  │  • 日志: /var/log/mempalace/        │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │       Claude Code集成                │   │
│  │  • MCP服务器配置                     │   │
│  │  • 技能系统集成                      │   │
│  │  • 自动记忆保存                      │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

#### 容器化部署架构
```dockerfile
# Dockerfile 示例
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY mempalace/ /app/mempalace/
COPY start_mempalace_mcp.sh /app/

# 安装依赖
RUN pip install --no-cache-dir -e /app/mempalace/

# 创建非root用户
RUN useradd -m -u 1000 mempalace
USER mempalace

# 启动脚本
ENTRYPOINT ["/app/start_mempalace_mcp.sh"]
```

### 3. 多环境配置管理

#### 环境配置文件 (env_config.yaml)
```yaml
environments:
  development:
    python_path: "venv/Scripts/python"
    mempalace_version: "3.3.0"
    log_level: "DEBUG"
    
  staging:
    python_path: "/opt/mempalace/venv/bin/python"
    mempalace_version: "3.3.0"
    log_level: "INFO"
    
  production:
    python_path: "/usr/local/bin/python3.11"
    mempalace_version: "3.3.0"
    log_level: "WARNING"
```

#### 环境检测脚本
```python
# detect_environment.py
import os
import sys
import platform

def detect_environment():
    """检测当前运行环境"""
    env_info = {
        'os': platform.system(),
        'python_version': platform.python_version(),
        'virtual_env': os.getenv('VIRTUAL_ENV'),
        'project_dir': os.path.dirname(os.path.abspath(__file__))
    }
    
    # 判断环境类型
    if 'dev' in env_info['project_dir'].lower():
        env_info['env_type'] = 'development'
    elif os.path.exists('/opt/mempalace'):
        env_info['env_type'] = 'staging'
    else:
        env_info['env_type'] = 'production'
    
    return env_info
```

## 扩展性考虑

### 1. 多版本支持架构

#### 版本管理器设计
```python
class VersionManager:
    def __init__(self):
        self.versions = {
            '3.3.0': {
                'python': '>=3.8',
                'dependencies': ['fastapi>=0.104.0'],
                'features': ['mcp_server', 'cli_tools']
            },
            '3.2.0': {
                'python': '>=3.7',
                'dependencies': ['fastapi>=0.100.0'],
                'features': ['mcp_server']
            }
        }
    
    def get_compatible_version(self, python_version):
        """根据Python版本获取兼容的MemPalace版本"""
        for version, spec in sorted(self.versions.items(), reverse=True):
            if self._check_python_compatibility(python_version, spec['python']):
                return version
        return None
```

### 2. 插件生态系统扩展

#### 插件注册机制
```python
# 插件接口定义
class MemPalacePlugin:
    def __init__(self, name, version):
        self.name = name
        self.version = version
    
    def register_commands(self, cli):
        """注册CLI命令"""
        pass
    
    def register_mcp_handlers(self, mcp_server):
        """注册MCP处理器"""
        pass
    
    def get_compatibility(self):
        """返回兼容性信息"""
        return {
            'mempalace_min': '3.3.0',
            'mempalace_max': '4.0.0',
            'python_min': '3.8'
        }

# 插件管理器
class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        """注册插件"""
        # 验证兼容性
        if self._check_compatibility(plugin):
            self.plugins.append(plugin)
            return True
        return False
```

### 3. 分布式部署架构

#### 多节点配置
```yaml
# cluster_config.yaml
nodes:
  - name: node1
    role: primary
    host: mempalace-node1.example.com
    port: 8000
    python_env: "/opt/mempalace/venv"
    
  - name: node2
    role: replica
    host: mempalace-node2.example.com
    port: 8000
    python_env: "/opt/mempalace/venv"
    
  - name: node3
    role: backup
    host: mempalace-node3.example.com
    port: 8000
    python_env: "system"  # 使用系统Python

load_balancer:
  strategy: round_robin
  health_check: "/health"
  check_interval: 30
```

## 性能优化

### 1. 启动性能优化

#### 懒加载机制
```python
class LazyMCPLoader:
    def __init__(self):
        self._server = None
        self._loaded = False
    
    def get_server(self):
        """懒加载MCP服务器"""
        if not self._loaded:
            self._load_server()
            self._loaded = True
        return self._server
    
    def _load_server(self):
        """实际加载服务器"""
        import mempalace.mcp_server
        self._server = mempalace.mcp_server.create_server()
```

#### 预编译优化
```python
# 使用PyPy或Nuitka进行预编译
# build_optimized.py
import subprocess
import sys

def build_optimized_version():
    """构建优化版本"""
    commands = [
        # 使用Nuitka编译
        [sys.executable, "-m", "nuitka", 
         "--standalone", 
         "--include-package=mempalace",
         "mempalace/mcp_server.py"],
        
        # 或使用PyPy
        # ["pypy3", "-m", "pip", "install", "mempalace"]
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, check=True)
            return True
        except subprocess.CalledProcessError:
            continue
    
    return False
```

### 2. 内存使用优化

#### 记忆数据分片
```python
class MemorySharding:
    def __init__(self, shard_count=4):
        self.shards = [{} for _ in range(shard_count)]
    
    def get_shard(self, memory_id):
        """根据记忆ID获取分片"""
        shard_index = hash(memory_id) % len(self.shards)
        return self.shards[shard_index]
    
    def save_memory(self, memory_id, data):
        """保存记忆到分片"""
        shard = self.get_shard(memory_id)
        shard[memory_id] = data
```

#### 缓存策略
```python
from functools import lru_cache

class MemoryCache:
    def __init__(self, maxsize=1000):
        self.cache = {}
        self.maxsize = maxsize
    
    @lru_cache(maxsize=1000)
    def get_memory(self, memory_id):
        """获取记忆（带缓存）"""
        if memory_id in self.cache:
            return self.cache[memory_id]
        
        # 从存储加载
        memory = self._load_from_storage(memory_id)
        self.cache[memory_id] = memory
        return memory
    
    def _evict_if_needed(self):
        """如果需要则驱逐缓存"""
        if len(self.cache) > self.maxsize:
            # LRU驱逐策略
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
```

## 安全考虑

### 1. 环境安全隔离

#### 沙箱环境配置
```python
import tempfile
import os

class SandboxEnvironment:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="mempalace_sandbox_")
        
    def setup_sandbox(self):
        """设置沙箱环境"""
        # 限制文件系统访问
        os.chroot(self.temp_dir)
        
        # 限制资源使用
        import resource
        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))  # 1秒CPU时间
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,))  # 256MB内存
        
    def cleanup(self):
        """清理沙箱环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
```

### 2. 配置安全

#### 敏感信息加密
```python
from cryptography.fernet import Fernet
import base64

class SecureConfig:
    def __init__(self, key_path="~/.mempalace/encryption.key"):
        self.key = self._load_or_generate_key(key_path)
        self.cipher = Fernet(self.key)
    
    def encrypt_config(self, config_dict):
        """加密配置"""
        config_json = json.dumps(config_dict)
        encrypted = self.cipher.encrypt(config_json.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_config(self, encrypted_config):
        """解密配置"""
        encrypted = base64.b64decode(encrypted_config.encode())
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
```

### 3. 访问控制

#### 基于角色的权限管理
```python
class RoleBasedAccessControl:
    ROLES = {
        'admin': ['read', 'write', 'delete', 'configure'],
        'user': ['read', 'write'],
        'guest': ['read']
    }
    
    def __init__(self):
        self.user_roles = {}
    
    def check_permission(self, user, action, resource):
        """检查用户权限"""
        user_role = self.user_roles.get(user, 'guest')
        allowed_actions = self.ROLES.get(user_role, [])
        
        return action in allowed_actions
```

## 监控和运维

### 1. 健康检查系统

#### 综合健康检查
```python
class HealthChecker:
    def __init__(self):
        self.checks = [
            self.check_python_env,
            self.check_mempalace_version,
            self.check_disk_space,
            self.check_memory_usage,
            self.check_network_connectivity
        ]
    
    def run_checks(self):
        """运行所有健康检查"""
        results = {}
        for check in self.checks:
            try:
                results[check.__name__] = check()
            except Exception as e:
                results[check.__name__] = {'status': 'ERROR', 'error': str(e)}
        
        return results
    
    def check_python_env(self):
        """检查Python环境"""
        import sys
        return {
            'status': 'OK',
            'python_version': sys.version,
            'virtual_env': os.getenv('VIRTUAL_ENV', 'system')
        }
```

### 2. 日志管理系统

#### 结构化日志配置
```python
import logging
import json

class StructuredLogger:
    def __init__(self, name="mempalace"):
        self.logger = logging.getLogger(name)
        self.setup_logging()
    
    def setup_logging(self):
        """设置结构化日志"""
        handler = logging.FileHandler('/var/log/mempalace/mempalace.log')
        
        # JSON格式日志
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': self.formatTime(record),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                if record.exc_info:
                    log_record['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_record)
        
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)
```

### 3. 性能监控

#### 实时性能指标
```python
import time
from collections import deque

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.metrics = {
            'response_time': deque(maxlen=window_size),
            'memory_usage': deque(maxlen=window_size),
            'request_count': 0
        }
        self.start_time = time.time()
    
    def record_response_time(self, response_time):
        """记录响应时间"""
        self.metrics['response_time'].append(response_time)
    
    def get_performance_summary(self):
        """获取性能摘要"""
        if not self.metrics['response_time']:
            return {}
        
        response_times = list(self.metrics['response_time'])
        uptime = time.time() - self.start_time
        
        return {
            'avg_response_time': sum(response_times) / len(response_times),
            'p95_response_time': sorted(response_times)[int(len(response_times) * 0.95)],
            'requests_per_second': self.metrics['request_count'] / uptime,
            'uptime_seconds': uptime
        }
```

## 故障恢复

### 1. 自动恢复机制

#### 进程监控和重启
```python
import subprocess
import time
import psutil

class ProcessMonitor:
    def __init__(self, command, name="mempalace_mcp"):
        self.command = command
        self.name = name
        self.process = None
    
    def start(self):
        """启动进程"""
        self.process = subprocess.Popen(self.command)
        print(f"[INFO] Started {self.name} with PID {self.process.pid}")
    
    def monitor(self):
        """监控进程状态"""
        while True:
            if self.process.poll() is not None:
                print(f"[WARNING] {self.name} process died, restarting...")
                self.start()
            
            time.sleep(10)  # 每10秒检查一次
```

### 2. 数据备份和恢复

#### 增量备份系统
```python
import shutil
import hashlib
from datetime import datetime

class IncrementalBackup:
    def __init__(self, backup_dir="~/.mempalace/backups"):
        self.backup_dir = os.path.expanduser(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, source_dir):
        """创建增量备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}")
        
        # 计算文件哈希以检测变化
        file_hashes = self._calculate_hashes(source_dir)
        
        # 只备份变化的文件
        changed_files = self._get_changed_files(file_hashes)
        
        if changed_files:
            print(f"[INFO] Backing up {len(changed_files)} changed files")
            for file_path in changed_files:
                self._backup_file(file_path, backup_path)
            
            # 保存元数据
            self._save_metadata(backup_path, file_hashes)
    
    def _calculate_hashes(self, directory):
        """计算文件哈希"""
        hashes = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                    hashes[file_path] = file_hash
        
        return hashes
```

## 总结

MemPalace插件集成架构通过以下关键设计解决了实际项目中的问题：

1. **版本同步机制**：确保插件版本与Python包版本一致，便于维护和问题追踪
2. **环境优先级策略**：智能环境选择，项目虚拟环境优先，系统环境作为降级保证
3. **跨平台兼容性**：提供Windows和Unix系统的统一启动接口
4. **技能系统集成**：专用脚本确保技能调用使用正确的环境
5. **可扩展设计**：支持多版本、插件生态系统和分布式部署

该架构已在生产环境中验证，能够稳定支持MemPalace插件在Claude Code项目中的集成需求，并为类似插件集成项目提供了可复用的设计模式。