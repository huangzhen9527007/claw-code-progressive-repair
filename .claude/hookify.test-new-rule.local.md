---
name: test-new-hookify-rule
enabled: true
event: bash
pattern: ls.*-la
action: warn
---

**新的Hookify测试规则触发成功！**

检测到包含"ls -la"的Bash命令。

这是一个新的测试规则，用于验证Hookify插件是否动态加载规则。