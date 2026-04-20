---
name: test-echo-rule
enabled: false
event: bash
pattern: echo.*test
action: warn
---

**测试规则触发成功！**

这是一个测试规则，用于验证 Hookify 插件是否正常工作。

规则匹配包含 "echo" 和 "test" 的 Bash 命令。