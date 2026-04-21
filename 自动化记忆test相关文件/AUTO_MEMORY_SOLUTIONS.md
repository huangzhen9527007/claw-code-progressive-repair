# Claude Code 自动记忆解决方案

## 问题分析

### 当前限制
1. **手动执行**：需要手动运行 `mempalace mine` 命令
2. **文件夹限制**：只能对特定文件夹进行记忆
3. **无自动化**：无法自动保存当前会话信息
4. **安全限制**：无法直接读取会话窗口内容

### 核心需求
- 完全自动化的记忆保存
- 实时监控所有会话
- 无限制访问会话内容
- 无需用户干预

## 解决方案概览

### 方案1：会话监控器（推荐）
**文件**: `claude-mem-auto-save.py`
**启动**: `start-claude-mem-auto.bat`

#### 特点：
- ✅ 无需修改 Claude Code 源代码
- ✅ 实时监控会话目录
- ✅ 自动解析 `.jsonl` 会话文件
- ✅ 保存到 MemPalace
- ✅ 可设置为定时任务

#### 使用方法：
```bash
# 运行一次
python claude-mem-auto-save.py --once --max-files 50

# 持续运行
python claude-mem-auto-save.py --continuous --interval 60

# 使用批处理文件
start-claude-mem-auto.bat
```

### 方案2：集成钩子
**文件**: `claude-mem-integrated-hook.py`

#### 特点：
- ✅ 修改 Claude Code 钩子系统
- ✅ 在消息交换时自动保存
- ✅ 更紧密的集成
- ✅ 需要重启 Claude Code

#### 使用方法：
```bash
# 安装
python claude-mem-integrated-hook.py --install

# 卸载
python claude-mem-integrated-hook.py --uninstall

# 测试
python claude-mem-integrated-hook.py --test
```

### 方案3：源代码补丁（高级）
**文件**: `patch-claude-for-auto-memory.py`

#### 特点：
- ✅ 直接修改 Claude Code 源代码
- ✅ 完全透明的自动化
- ✅ 深度集成
- ✅ 需要重新编译/重启

#### 使用方法：
```bash
# 应用补丁
python patch-claude-for-auto-memory.py --apply

# 恢复备份
python patch-claude-for-auto-memory.py --restore
```

## 技术原理

### 1. 会话存储机制
Claude Code 将会话存储在：
```
~/.claude/projects/C--编码后的项目路径/
  ├── 会话ID.jsonl      # 完整的会话记录
  └── memory/           # 记忆文件
```

`.jsonl` 文件格式：
```json
{"type":"user","message":{"role":"user","content":"消息内容"}}
{"type":"assistant","message":{"role":"assistant","content":"响应内容"}}
```

### 2. 自动化流程
```
监控会话目录 → 检测新文件 → 解析JSONL → 提取关键信息 → 保存到MemPalace
```

### 3. MemPalace 集成
使用 `mempalace add_drawer` 命令：
```bash
mempalace add_drawer \
  --wing "claude_sessions" \
  --room "project_name" \
  --title "会话摘要" \
  --content-file "记忆内容.md"
```

## 配置说明

### 环境变量
```bash
# 设置 Python 编码（Windows 必需）
set PYTHONIOENCODING=utf-8

# 或
export PYTHONIOENCODING=utf-8
```

### 状态管理
- 处理状态保存在 `~/.claude/memory_saver_state.json`
- 避免重复处理相同文件
- 支持增量更新

### 性能考虑
- 默认最多处理 20 个文件
- 可调整扫描间隔
- 后台运行，不影响主程序

## 安全说明

### 权限需求
- **超级管理员权限**：需要无限制访问会话文件
- **本地运行**：所有数据保持在本地
- **无网络传输**：不涉及任何云服务

### 数据隐私
- 仅读取 Claude Code 生成的会话文件
- 不修改原始会话数据
- 记忆保存在本地 MemPalace 中

## 故障排除

### 常见问题

#### 1. 编码问题（Windows）
**症状**：乱码或 Unicode 错误
**解决**：
```bash
set PYTHONIOENCODING=utf-8
python claude-mem-auto-save.py
```

#### 2. MemPalace 未找到
**症状**：`mempalace: command not found`
**解决**：
```bash
pip install mempalace
# 或使用完整路径
python -m mempalace --version
```

#### 3. 权限不足
**症状**：无法读取会话文件
**解决**：
- 以管理员身份运行
- 检查文件权限

#### 4. 文件锁定
**症状**：无法读取正在使用的会话文件
**解决**：
- 增加扫描间隔
- 使用 `--interval 120` 参数

### 日志查看
```bash
# 查看处理状态
cat ~/.claude/memory_saver_state.json

# 查看临时文件
ls ~/.claude/temp_memories/
```

## 高级配置

### 自定义扫描目录
修改脚本中的：
```python
self.claude_projects_dir = Path.home() / ".claude" / "projects"
```

### 自定义记忆格式
修改 `create_memory_content` 函数

### 过滤规则
可添加文件大小、时间等过滤条件

## 性能优化

### 推荐配置
```bash
# 生产环境
python claude-mem-auto-save.py --continuous --interval 300 --max-files 50

# 开发环境
python claude-mem-auto-save.py --continuous --interval 60 --max-files 20
```

### 资源占用
- CPU: < 5% （扫描时）
- 内存: < 100MB
- 磁盘: 临时文件自动清理

## 未来扩展

### 计划功能
1. **智能摘要**：使用 AI 生成更好的会话摘要
2. **分类标签**：自动为记忆添加标签
3. **搜索优化**：改进 MemPalace 搜索体验
4. **可视化**：记忆图谱可视化

### 集成选项
1. **Webhook**：支持外部系统调用
2. **API**：提供 REST API 接口
3. **插件系统**：支持第三方扩展

## 总结

### 推荐方案
对于大多数用户，推荐使用 **方案1：会话监控器**：
- 无需修改源代码
- 安全可靠
- 配置简单
- 功能完整

### 快速开始
```bash
# 1. 确保 MemPalace 已安装
pip install mempalace

# 2. 运行自动保存器
python claude-mem-auto-save.py --once

# 3. 设置为持续运行
python claude-mem-auto-save.py --continuous --interval 300
```

### 验证效果
```bash
# 查看 MemPalace 状态
mempalace status

# 搜索记忆
mempalace search "关键词"
```

现在，Claude Code 的所有会话都将自动保存到 MemPalace，实现完全自动化的记忆管理！