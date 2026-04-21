---
name: test-stop-rule
enabled: false
event: stop
conditions:
  - field: reason
    operator: regex_match
    pattern: .*
action: warn
---

**Stop规则测试触发成功！**

检测到Claude Code尝试停止。

这是一个测试规则，用于验证Hookify插件的Stop事件是否正常工作。