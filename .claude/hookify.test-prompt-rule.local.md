---
name: test-prompt-rule
enabled: false
event: prompt
conditions:
  - field: user_prompt
    operator: contains
    pattern: test
action: warn
---

**Prompt规则测试触发成功！**

检测到用户输入包含"test"。

这是一个测试规则，用于验证Hookify插件的UserPromptSubmit事件是否正常工作。