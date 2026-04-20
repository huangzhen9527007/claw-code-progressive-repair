# MemPalace 插件集成架构

## 概述

MemPalace 是一个结构化记忆系统，通过 MCP (Model Context Protocol) 服务器与 Claude Code 集成。本架构文档描述了 MemPalace 插件的集成设计、配置管理和优化策略。

## 架构设计

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Code 客户端                        │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐ │
│  │                 MCP 客户端协议层                       │ │
│  │  • 工具调用 (tool calls)                              │ │
│  │  • 资源访问 (resource access)                         │ │
│  │  • 消息传递 (message passing)                         │ │
│  └───────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    MemPalace 插件层                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  房间管理   │  │  记忆抽屉   │  │  知识图谱管理        │ │
│  │  (Rooms)    │  │  (Drawers)  │  │  (Knowledge Graph)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    MemPalace 存储层                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  YAML配置   │  │  文件存储   │  │  索引和元数据        │ │
│  │  (Config)   │  │  (Storage)  │  │  (Index/Metadata)   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 组件关系

1. **客户端层**
   - **Claude Code**: 主应用程序，通过 MCP 协议与插件通信
   - **MCP 客户端**: 处理工具调用和资源访问的标准协议实现

2. **插件层**
   - **房间管理**: 逻辑分类单元，组织相关记忆抽屉
   - **记忆抽屉**: 实际存储记忆的容器，包含多个记忆项
   - **知识图谱**: 记忆之间的关系网络，支持智能查询

3. **存储层**
   - **YAML 配置**: 定义房间结构和插件行为
   - **文件存储**: 实际记忆数据的持久化存储
   - **索引系统**: 快速检索的元数据和索引

## 设计原则

### 1. 模块化设计
- **独立组件**: 房间、抽屉、知识图谱作为独立模块
- **清晰接口**: 标准化的 API 和协议接口
- **可替换性**: 支持存储后端的灵活替换

### 2. 可扩展性
- **插件架构**: 通过 MCP 协议轻松集成新功能
- **配置驱动**: 行为通过配置文件定义，无需代码修改
- **水平扩展**: 支持分布式存储和查询

### 3. 数据一致性
- **事务支持**: 重要操作的原子性保证
- **版本控制**: 记忆数据的版本管理
- **完整性检查**: 数据存储的完整性验证

### 4. 性能优化
- **缓存策略**: 热点数据的智能缓存
- **批量操作**: 减少 I/O 操作的批处理
- **异步处理**: 非阻塞的长时间操作

## 配置管理

### 1. MemPalace 配置文件

#### 基本结构
```yaml
# ~/.mempalace/palace/claude_sessions/mempalace.yaml
wing: claude_sessions          # 翼（逻辑分区）
rooms:                         # 房间列表
  - name: general              # 房间名称
    description: Files that don't fit other rooms
    keywords: []               # 关键词列表
```

#### 简化配置策略
```yaml
# 推荐：简化配置，只使用 general 房间
wing: claude_sessions
rooms:
  - name: general
    description: General Claude sessions storage
    keywords: []
```

### 2. 路径编码规则

#### Windows 路径编码
```
原始路径: C:\Users\Administrator\Desktop\projects\claudecode\yuanmaziyuan\cloud-code-rewrite\cloud-code-main
编码后: c__users_administrator_desktop_projects_claudecode_yuanmaziyuan_cloud_code_rewrite_cloud_code_main
```

#### 编码算法
```python
def encode_path(path: str) -> str:
    # 1. 转换为小写
    path = path.lower()
    # 2. 替换特殊字符
    path = path.replace(':', '__').replace('\\', '_').replace('/', '_')
    # 3. 移除连续下划线
    path = re.sub(r'_+', '_', path)
    # 4. 移除首尾下划线
    return path.strip('_')
```

### 3. Claude Code 集成配置

#### MCP 服务器配置
```json
{
  "mcpServers": {
    "mempalace": {
      "command": "npx",
      "args": ["-y", "@mempalace/mcp-server@latest"],
      "env": {
        "MEMPALACE_DATA_DIR": "~/.mempalace"
      }
    }
  }
}
```

#### 环境变量配置
```bash
# Windows 环境变量
set MEMPALACE_DATA_DIR=%USERPROFILE%\.mempalace
set MEMPALACE_LOG_LEVEL=info

# 启动 MemPalace 服务器
npx -y @mempalace/mcp-server@latest
```

## 集成架构

### 1. 启动流程

#### 顺序启动
```
1. Claude Code 启动
2. 加载 MCP 配置
3. 启动 MemPalace MCP 服务器
4. 建立客户端-服务器连接
5. 验证插件功能
```

#### 错误处理
```python
def start_mempalace_integration():
    try:
        # 1. 检查配置
        config = load_mcp_config()
        
        # 2. 启动服务器
        server_process = start_mcp_server(config)
        
        # 3. 建立连接
        client = connect_to_server(server_process)
        
        # 4. 功能验证
        if not verify_plugin_functionality(client):
            raise IntegrationError("Plugin verification failed")
            
        return client
        
    except Exception as e:
        log_error(f"MemPalace integration failed: {e}")
        fallback_to_local_storage()
```

### 2. 数据流设计

#### 记忆保存流程
```
Claude Code 会话结束
    ↓
转换为结构化记忆格式
    ↓
选择目标房间（默认: general）
    ↓
创建或更新记忆抽屉
    ↓
保存到 MemPalace 存储
    ↓
更新知识图谱索引
    ↓
返回保存结果
```

#### 记忆查询流程
```
用户查询请求
    ↓
解析查询意图
    ↓
搜索房间和抽屉
    ↓
检索相关记忆
    ↓
应用知识图谱关系
    ↓
排序和过滤结果
    ↓
返回格式化响应
```

### 3. 版本同步机制

#### 插件版本管理
```json
{
  "dependencies": {
    "@mempalace/mcp-server": "^0.3.0",
    "claude-mem": "^0.1.0"
  },
  "versionConstraints": {
    "minNodeVersion": "18.0.0",
    "recommendedNpmVersion": "10.0.0"
  }
}
```

#### 版本检测和升级
```python
def check_and_update_versions():
    current_version = get_current_mempalace_version()
    latest_version = fetch_latest_version()
    
    if current_version != latest_version:
        log_info(f"Updating MemPalace from {current_version} to {latest_version}")
        
        # 备份当前配置
        backup_configuration()
        
        # 执行升级
        upgrade_mempalace(latest_version)
        
        # 验证升级结果
        verify_upgrade_success()
        
        # 清理备份
        cleanup_backup()
```

## 优化策略

### 1. 配置简化

#### 房间配置优化
```yaml
# 优化前：多个特定路径房间
rooms:
  - name: c__users_administrator_desktop_projects_claudecode_yuanmaziyuan_cloud_code_rewrite_cloud_code_main
  - name: c__users_administrator__claude_mem_observer_sessions
  - name: general

# 优化后：单一通用房间
rooms:
  - name: general
    description: All Claude Code sessions
    keywords: [claude, code, session, memory]
```

#### 优势分析
- **减少复杂性**: 简化配置管理
- **提高性能**: 减少房间切换开销
- **增强通用性**: 适应不同项目结构
- **避免编码问题**: 消除路径编码不一致性

### 2. 性能优化

#### 存储优化
```python
class OptimizedMemPalaceStorage:
    def __init__(self):
        self.cache = LRUCache(maxsize=1000)  # 内存缓存
        self.batch_queue = []                # 批量操作队列
        self.index = InvertedIndex()         # 倒排索引
        
    def save_memory(self, memory):
        # 1. 添加到批量队列
        self.batch_queue.append(memory)
        
        # 2. 批量达到阈值时持久化
        if len(self.batch_queue) >= 10:
            self.flush_batch()
            
        # 3. 更新缓存和索引
        self.cache[memory.id] = memory
        self.index.update(memory)
```

#### 查询优化
```python
def optimized_query(query, limit=50):
    # 1. 查询缓存
    cached = query_cache.get(query)
    if cached:
        return cached[:limit]
    
    # 2. 并行搜索
    with ThreadPoolExecutor() as executor:
        room_futures = {
            executor.submit(search_room, room, query): room
            for room in active_rooms
        }
        
        # 3. 合并结果
        results = []
        for future in as_completed(room_futures):
            results.extend(future.result())
    
    # 4. 排序和截断
    results.sort(key=lambda x: x.relevance, reverse=True)
    results = results[:limit]
    
    # 5. 更新缓存
    query_cache[query] = results
    
    return results
```

### 3. 可靠性优化

#### 错误恢复机制
```python
class ResilientMemPalaceClient:
    def __init__(self):
        self.primary_server = None
        self.backup_storage = LocalStorage()
        self.retry_policy = ExponentialBackoffRetry()
        
    def save_with_fallback(self, memory):
        try:
            # 尝试主服务器
            return self.primary_server.save(memory)
        except ServerError as e:
            log_warning(f"Primary server failed: {e}")
            
            # 回退到本地存储
            backup_id = self.backup_storage.save(memory)
            
            # 计划重试
            self.schedule_retry(memory)
            
            return backup_id
```

#### 数据完整性检查
```python
def verify_data_integrity():
    checks = [
        check_configuration_validity(),
        check_storage_consistency(),
        check_index_integrity(),
        check_backup_availability()
    ]
    
    issues = []
    for check_name, check_result in checks:
        if not check_result.success:
            issues.append({
                'check': check_name,
                'issue': check_result.issue,
                'severity': check_result.severity
            })
    
    return IntegrityReport(issues=issues)
```

## 扩展性设计

### 1. 插件功能扩展

#### 新工具集成
```typescript
// 扩展 MemPalace 工具集
interface ExtendedMemPalaceTools {
  // 基础工具
  mempalace_search: (query: string) => Promise<SearchResult[]>;
  mempalace_save: (memory: Memory) => Promise<string>;
  
  // 扩展工具
  mempalace_analyze: (options: AnalyzeOptions) => Promise<AnalysisResult>;
  mempalace_export: (format: ExportFormat) => Promise<ExportResult>;
  mempalace_backup: (destination: string) => Promise<BackupResult>;
}
```

#### 自定义房间类型
```yaml
rooms:
  - name: code_reviews
    type: specialized
    description: Code review sessions and feedback
    schema:
      required_fields: [project, reviewer, date]
      optional_fields: [rating, comments, follow_up]
    indexing:
      full_text: true
      vector_embedding: true
```

### 2. 存储后端扩展

#### 多存储支持
```python
class StorageAdapterFactory:
    @staticmethod
    def create_adapter(config: StorageConfig):
        adapter_type = config.get('type', 'filesystem')
        
        if adapter_type == 'filesystem':
            return FileSystemAdapter(config)
        elif adapter_type == 'sqlite':
            return SQLiteAdapter(config)
        elif adapter_type == 'postgresql':
            return PostgreSQLAdapter(config)
        elif adapter_type == 's3':
            return S3Adapter(config)
        else:
            raise ValueError(f"Unsupported adapter type: {adapter_type}")
```

#### 混合存储策略
```python
class HybridStorage:
    def __init__(self, hot_config, cold_config):
        self.hot_storage = create_adapter(hot_config)   # 热数据：内存/SSD
        self.cold_storage = create_adapter(cold_config) # 冷数据：HDD/云存储
        
    def save(self, memory):
        # 新数据存入热存储
        hot_id = self.hot_storage.save(memory)
        
        # 异步备份到冷存储
        asyncio.create_task(self.backup_to_cold(memory))
        
        return hot_id
    
    async def backup_to_cold(self, memory):
        await self.cold_storage.save(memory)
```

### 3. 查询语言扩展

#### 高级查询语法
```python
# 基础查询
query = "project:cloud-code AND date:2024-*"

# 扩展查询语法
extended_query = """
FROM rooms:general
WHERE type IN ('session', 'conversation')
  AND date >= '2024-01-01'
  AND relevance > 0.7
  AND (tags CONTAINS 'architecture' OR content LIKE '%memory%')
ORDER BY date DESC, relevance DESC
LIMIT 20
"""

# 自然语言查询
nl_query = "Find all architecture discussions from last month about memory systems"
```

#### 查询优化器
```python
class QueryOptimizer:
    def optimize(self, query):
        # 1. 语法解析
        ast = self.parse_query(query)
        
        # 2. 重写优化
        ast = self.rewrite_for_performance(ast)
        
        # 3. 执行计划生成
        plan = self.generate_execution_plan(ast)
        
        # 4. 成本估算
        cost = self.estimate_cost(plan)
        
        return OptimizedQuery(ast=ast, plan=plan, cost=cost)
```

## 监控和运维

### 1. 健康监控

#### 监控指标
```python
class MemPalaceMetrics:
    def __init__(self):
        self.metrics = {
            'request_rate': Counter(),
            'response_time': Histogram(),
            'error_rate': Counter(),
            'cache_hit_rate': Gauge(),
            'storage_usage': Gauge(),
            'memory_usage': Gauge()
        }
    
    def collect_metrics(self):
        return {
            name: metric.collect()
            for name, metric in self.metrics.items()
        }
```

#### 告警规则
```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 0.05  # 错误率超过5%
    severity: warning
    action: notify_slack
    
  - name: storage_critical
    condition: storage_usage > 0.9  # 存储使用超过90%
    severity: critical
    action: cleanup_old_data
    
  - name: slow_response
    condition: p95_response_time > 1000  # 95%响应时间超过1秒
    severity: warning
    action: scale_up
```

### 2. 日志管理

#### 结构化日志
```python
import structlog

logger = structlog.get_logger()

def save_memory(memory):
    with logger.bind(
        operation="save_memory",
        memory_id=memory.id,
        room=memory.room
    ):
        try:
            result = storage.save(memory)
            logger.info("memory_saved", result=result)
            return result
        except Exception as e:
            logger.error("save_failed", error=str(e))
            raise
```

#### 日志聚合
```python
class LogAggregator:
    def __init__(self):
        self.buffer = []
        self.flush_interval = 60  # 60秒
        
    def add_log(self, log_entry):
        self.buffer.append(log_entry)
        
        if len(self.buffer) >= 1000:
            self.flush()
    
    def flush(self):
        if self.buffer:
            # 发送到日志服务
            send_to_log_service(self.buffer)
            self.buffer.clear()
```

### 3. 备份和恢复

#### 备份策略
```python
class BackupManager:
    def __init__(self):
        self.full_backup_interval = 24 * 3600  # 每天
        self.incremental_interval = 3600       # 每小时
        self.retention_days = 30               # 保留30天
    
    def schedule_backups(self):
        # 全量备份
        schedule.every().day.at("02:00").do(self.full_backup)
        
        # 增量备份
        schedule.every().hour.do(self.incremental_backup)
        
        # 清理旧备份
        schedule.every().day.at("03:00").do(self.cleanup_old_backups)
```

#### 恢复流程
```python
def disaster_recovery():
    # 1. 识别故障
    fault = diagnose_fault()
    
    # 2. 选择恢复点
    recovery_point = select_recovery_point(fault)
    
    # 3. 恢复数据
    restore_data(recovery_point)
    
    # 4. 验证恢复
    verify_recovery()
    
    # 5. 重新启动服务
    restart_services()
```

## 安全考虑

### 1. 数据安全

#### 加密存储
```python
class EncryptedStorage:
    def __init__(self, encryption_key):
        self.cipher = AES.new(encryption_key, AES.MODE_GCM)
    
    def save_encrypted(self, data):
        # 加密数据
        ciphertext, tag = self.cipher.encrypt_and_digest(
            json.dumps(data).encode()
        )
        
        # 存储加密数据
        storage.save({
            'ciphertext': base64.b64encode(ciphertext).decode(),
            'tag': base64.b64encode(tag).decode(),
            'nonce': base64.b64encode(self.cipher.nonce).decode()
        })
```

#### 访问控制
```python
class AccessController:
    def __init__(self):
        self.policies = load_access_policies()
    
    def check_access(self, user, resource, action):
        # 检查RBAC策略
        for policy in self.policies:
            if policy.matches(user, resource, action):
                return policy.allows()
        
        # 默认拒绝
        return False
```

### 2. 网络安全

#### 传输安全
```python
class SecureTransport:
    def __init__(self):
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
    
    def secure_request(self, request):
        # TLS加密传输
        with socket.create_connection(
            (request.host, request.port)
        ) as sock:
            with self.ssl_context.wrap_socket(
                sock, server_hostname=request.host
            ) as ssock:
                return ssock.send(request.data)
```

## 演进规划

### 短期目标 (1-3个月)
1. **稳定性提升**: 优化插件启动和连接稳定性
2. **配置简化**: 完善简化配置的最佳实践
3. **性能基准**: 建立性能基准和监控指标

### 中期目标 (3-6个月)
1. **高级功能**: 实现知识图谱和智能分析
2. **多用户支持**: 添加多用户隔离和共享功能
3. **云集成**: 支持云存储和跨设备同步

### 长期目标 (6-12个月)
1. **AI增强**: 集成AI自动分类和摘要生成
2. **生态系统**: 建立插件市场和扩展生态系统
3. **企业级功能**: 添加审计、合规和企业集成

## 相关文档

### 项目文档
- [MemPalace配置简化经验](../../../记忆系统知识分析报告.md)
- [claude-mem插件版本同步](../../../记忆知识整理实施计划.md)

### 技术参考
- [MemPalace MCP 服务器 GitHub](https://github.com/mempalace/mcp-server)
- [MCP 协议规范](https://spec.modelcontextprotocol.io/)
- [Claude Code 插件开发指南](https://docs.anthropic.com/claude/code/plugins)

### 最佳实践
- [简化配置指南](./simplified-configuration-guide.md) (待创建)
- [性能优化手册](./performance-optimization.md) (待创建)
- [故障排除指南](./troubleshooting-guide.md) (待创建)

---

**架构维护说明**: 本架构文档应随 MemPalace 插件版本更新而更新。任何架构变更都应记录变更日志，并评估对现有配置的兼容性影响。