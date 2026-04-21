# 故障排除手册

## 概述

`troubleshooting/` 目录存储 Cloud Code 项目的故障排除文档。包括常见错误及解决方案、调试方法、日志分析等。

## 故障分类

### 1. 启动问题
- 服务无法启动
- 依赖加载失败
- 配置错误

### 2. 运行时问题
- API 调用失败
- 内存泄漏
- 性能问题

### 3. 集成问题
- 插件兼容性问题
- 第三方服务连接问题
- 环境配置问题

### 4. 数据问题
- 数据损坏
- 存储问题
- 备份恢复问题

### 5. 网络问题
- 连接超时
- 代理配置问题
- 防火墙限制

## 故障排除流程

### 步骤1：问题识别
1. **收集信息**
   - 错误消息
   - 发生时间
   - 操作步骤
   - 环境信息

2. **问题分类**
   - 确定问题类型
   - 评估影响范围
   - 确定优先级

### 步骤2：初步诊断
1. **检查日志**
   ```bash
   # 查看应用日志
   tail -f logs/cloud-code.log
   
   # 查看错误日志
   tail -f logs/error.log
   
   # 查看系统日志
   journalctl -u cloud-code -f
   ```

2. **验证状态**
   ```bash
   # 检查服务状态
   systemctl status cloud-code
   
   # 检查进程
   ps aux | grep cloud-code
   
   # 检查端口
   netstat -tulpn | grep :3000
   ```

### 步骤3：深入分析
1. **重现问题**
   - 确定复现步骤
   - 收集调试信息
   - 分析模式

2. **定位根本原因**
   - 代码分析
   - 配置检查
   - 环境验证

### 步骤4：解决方案
1. **制定方案**
   - 临时解决方案
   - 永久解决方案
   - 预防措施

2. **实施验证**
   - 实施解决方案
   - 验证效果
   - 监控恢复

## 常见问题及解决方案

### 问题1：服务无法启动

#### 症状
```bash
Error: Cannot find module 'some-package'
# 或
Error: listen EADDRINUSE: address already in use :::3000
```

#### 解决方案
```bash
# 检查依赖
bun install --frozen-lockfile

# 检查端口占用
lsof -i :3000
# 或
netstat -tulpn | grep :3000

# 更换端口
export PORT=3001
bun run dev
```

#### 预防措施
- 使用固定端口范围
- 添加端口检查逻辑
- 完善错误提示

### 问题2：API 调用失败

#### 症状
```bash
Error: Failed to connect to API server
# 或
Error: Invalid API key
```

#### 解决方案
```bash
# 测试网络连接
curl -v https://api.anthropic.com/v1/messages

# 检查 API 密钥
echo $ANTHROPIC_API_KEY

# 验证配置
cat config/default.json | grep apiKey
```

#### 调试步骤
1. 检查网络连接
2. 验证 API 密钥
3. 检查防火墙设置
4. 查看代理配置

### 问题3：内存泄漏

#### 症状
- 内存使用持续增长
- 响应变慢
- 进程崩溃

#### 解决方案
```bash
# 监控内存使用
pm2 monit

# 生成堆快照
bun --inspect dist/cli.js

# 分析内存泄漏
node --inspect-brk --expose-gc dist/cli.js
```

#### 常见原因
- 未释放的事件监听器
- 循环引用
- 大对象缓存

### 问题4：插件兼容性问题

#### 症状
```bash
Error: Plugin 'claude-mem' requires native binary
# 或
Error: MCP server failed to start
```

#### 解决方案
```bash
# 检查插件配置
cat ~/.claude/plugins/cache/*/package.json

# 验证包装脚本
./claude.cmd --version

# 检查 PATH
echo $PATH
where claude.cmd
```

#### 参考文档
- [claude-mem 插件解决方案](../solutions/claude-mem-binary-fix/README.md)

### 问题5：数据损坏

#### 症状
- 读取数据失败
- 校验和错误
- 备份恢复失败

#### 解决方案
```bash
# 检查数据文件
ls -la ~/.claude/

# 验证数据完整性
bun run scripts/check-data.js

# 从备份恢复
tar -xzf backup-20240419.tar.gz -C ~/
```

#### 预防措施
- 定期备份
- 数据验证
- 版本控制

### 问题6：Windows CMD窗口行为问题

#### 症状
- 双击BAT文件运行程序后窗口立即关闭
- 无法查看程序输出和错误信息
- `pause`命令不起作用

#### 解决方案
```bash
# 正确使用方法：手动打开CMD窗口
# 1. 打开CMD或Windows Terminal
# 2. 切换到项目目录
cd /d "C:\path\to\project"
# 3. 运行BAT文件
TUI启动器.bat
```

#### 详细指南
- [Windows CMD窗口行为问题排查指南](./windows-cmd-window-behavior.md)

#### 技术原理
- 双击BAT文件由资源管理器使用`cmd.exe /c`启动
- `/c`参数强制命令执行后终止窗口
- 无法通过修改BAT文件改变这一行为

### 问题6：Windows CMD窗口行为问题

#### 症状
- 双击BAT文件运行程序后窗口立即关闭
- 无法查看程序输出和错误信息
- `pause`命令不起作用

#### 解决方案
```bash
# 正确使用方法：手动打开CMD窗口
# 1. 打开CMD或Windows Terminal
# 2. 切换到项目目录
cd /d "C:\path\to\project"
# 3. 运行BAT文件
TUI启动器.bat
```

#### 详细指南
- [Windows CMD窗口行为问题排查指南](./windows-cmd-window-behavior.md)

#### 技术原理
- 双击BAT文件由资源管理器使用`cmd.exe /c`启动
- `/c`参数强制命令执行后终止窗口
- 无法通过修改BAT文件改变这一行为

## 调试工具和技巧

### 日志分析
#### 日志级别
```typescript
// 设置日志级别
import logger from './utils/logger';

logger.debug('Debug message');    // 开发调试
logger.info('Info message');      // 一般信息
logger.warn('Warning message');   // 警告
logger.error('Error message');    // 错误
```

#### 日志搜索
```bash
# 搜索特定错误
grep -i "error" logs/cloud-code.log

# 按时间范围搜索
sed -n '/2026-04-19 10:00/,/2026-04-19 11:00/p' logs/cloud-code.log

# 统计错误次数
grep -c "ERROR" logs/cloud-code.log
```

### 性能分析
#### CPU 分析
```bash
# 生成 CPU 分析文件
node --prof dist/cli.js

# 分析结果
node --prof-process isolate-0xnnnnnnnnnnnn-v8.log > profile.txt
```

#### 内存分析
```bash
# 生成堆快照
bun --inspect --inspect-brk dist/cli.js

# 使用 Chrome DevTools 分析
chrome://inspect
```

### 网络调试
```bash
# 跟踪网络请求
curl -v https://api.example.com

# 测试连接延迟
ping api.example.com

# 检查 DNS 解析
nslookup api.example.com

# 使用代理调试
export HTTP_PROXY=http://proxy:8080
export HTTPS_PROXY=http://proxy:8080
```

## 紧急恢复流程

### 服务不可用
#### 步骤1：快速恢复
```bash
# 重启服务
pm2 restart cloud-code

# 或强制重启
pm2 delete cloud-code
pm2 start dist/cli.js --name "cloud-code"
```

#### 步骤2：降级方案
```bash
# 启用维护模式
echo "MAINTENANCE_MODE=true" >> .env

# 显示维护页面
pm2 start maintenance-server.js
```

#### 步骤3：回滚部署
```bash
# 回滚到上一个版本
git checkout v1.0.0
bun install
bun run build
pm2 restart cloud-code
```

### 数据恢复
#### 备份恢复
```bash
# 停止服务
pm2 stop cloud-code

# 恢复备份
tar -xzf backup-$(date +%Y%m%d).tar.gz -C ~/

# 启动服务
pm2 start cloud-code
```

#### 数据修复
```bash
# 运行数据修复脚本
bun run scripts/repair-data.js

# 验证数据完整性
bun run scripts/validate-data.js
```

## 预防措施

### 监控告警
#### 关键指标监控
- 服务可用性
- 响应时间
- 错误率
- 资源使用率

#### 告警配置
```yaml
# alert-rules.yml
rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status="500"}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
```

### 健康检查
```typescript
// 健康检查端点
app.get('/health', (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    checks: {
      database: checkDatabase(),
      api: checkApiConnection(),
      memory: checkMemoryUsage()
    }
  };
  
  const isHealthy = Object.values(health.checks).every(check => check.healthy);
  res.status(isHealthy ? 200 : 503).json(health);
});
```

### 容错设计
#### 重试机制
```typescript
async function callWithRetry(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * Math.pow(2, i)); // 指数退避
    }
  }
}
```

#### 熔断器模式
```typescript
class CircuitBreaker {
  constructor(failureThreshold = 5, resetTimeout = 60000) {
    this.failureCount = 0;
    this.lastFailureTime = null;
    this.state = 'CLOSED';
    this.failureThreshold = failureThreshold;
    this.resetTimeout = resetTimeout;
  }
  
  async call(fn) {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.resetTimeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await fn();
      this.reset();
      return result;
    } catch (error) {
      this.recordFailure();
      throw error;
    }
  }
}
```

## 故障报告模板

### 问题报告
```markdown
## 问题描述
[简要描述问题]

## 环境信息
- 操作系统: [Windows/macOS/Linux]
- 版本: [Cloud Code 版本]
- 运行模式: [开发/生产]
- 相关配置: [如有]

## 复现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

## 预期行为
[期望的结果]

## 实际行为
[实际的结果，包括错误信息]

## 已尝试的解决方案
- [方案1]
- [方案2]

## 附加信息
[日志片段、截图等]
```

### 解决方案记录
```markdown
## 问题总结
[问题根本原因]

## 解决方案
[实施的解决方案]

## 验证结果
[如何验证解决方案有效]

## 预防措施
[未来如何预防类似问题]

## 相关文档
- [文档链接]
- [代码变更]
```

## 相关资源

### 项目文档
- [部署指南](../deployment/README.md)
- [开发指南](../development/README.md)
- [技术解决方案](../solutions/README.md)

### 外部工具
- **日志分析**: ELK Stack, Splunk
- **监控告警**: Prometheus, Grafana
- **调试工具**: Chrome DevTools, Wireshark

### 参考书籍
- 《Site Reliability Engineering》
- 《The Practice of System and Network Administration》
- 《Debugging》

---

**良好的故障排除能力是系统稳定性的重要保障。建立完善的故障排除流程和文档，有助于快速定位和解决问题，提高系统可用性。**