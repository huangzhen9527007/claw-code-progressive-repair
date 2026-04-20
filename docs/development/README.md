# 开发指南

## 概述

`development/` 目录存储 Cloud Code 项目的开发相关文档。包括开发环境搭建、代码规范、测试指南、贡献流程等。

## 开发资源

### 1. 环境搭建
- 开发工具安装
- 依赖管理
- 环境配置

### 2. 代码规范
- 代码风格指南
- 命名规范
- 目录结构

### 3. 测试指南
- 单元测试
- 集成测试
- 端到端测试

### 4. 调试技巧
- 调试工具使用
- 常见问题调试
- 性能调试

### 5. 贡献流程
- 代码提交规范
- Pull Request 流程
- 代码审查指南

## 当前开发文档

### [开发环境搭建](./environment-setup.md)（待创建）
详细描述开发环境的搭建步骤。

### [代码规范指南](./coding-standards.md)（待创建）
项目的代码规范和最佳实践。

### [测试策略](./testing-strategy.md)（待创建）
项目的测试方法和策略。

## 开发环境

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Linux
- **Node.js**: 18.x 或更高版本（通过 Bun 管理）
- **Bun**: 1.0.x 或更高版本
- **Git**: 2.30+ 版本控制
- **编辑器**: VS Code 推荐，支持 TypeScript 和 React

### 工具安装
```bash
# 安装 Bun
curl -fsSL https://bun.sh/install | bash

# 验证安装
bun --version

# 安装 Git（如未安装）
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Linux: sudo apt install git
```

### 项目设置
```bash
# 克隆项目
git clone https://github.com/your-org/cloud-code.git
cd cloud-code

# 安装依赖
bun install

# 验证安装
bun run dev --help
```

### 开发工具配置
#### VS Code 扩展推荐
- TypeScript 和 JavaScript 语言功能
- ESLint
- Prettier
- React 相关扩展
- GitLens

#### 编辑器配置
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "files.exclude": {
    "**/.git": true,
    "**/.DS_Store": true,
    "**/node_modules": true,
    "**/dist": true
  }
}
```

## 代码规范

### 语言规范
#### TypeScript
- 使用严格模式
- 明确的类型定义
- 避免使用 `any` 类型
- 使用接口定义数据结构

#### JavaScript/React
- 使用函数组件和 Hooks
- 避免类组件
- 使用 PropTypes 或 TypeScript
- 组件拆分合理

### 代码风格
#### 命名规范
- **变量和函数**: camelCase
- **类和类型**: PascalCase  
- **常量**: UPPER_SNAKE_CASE
- **文件命名**: kebab-case

#### 代码格式
- 使用 2 空格缩进
- 行宽限制 100 字符
- 使用单引号
- 尾随逗号

#### 示例代码
```typescript
// 好的示例
interface UserProfile {
  id: string;
  name: string;
  email: string;
}

function formatUserName(user: UserProfile): string {
  return `${user.name} <${user.email}>`;
}

const MAX_RETRY_COUNT = 3;

// 不好的示例
function FormatUserName(user: any): string {
  return user.name + ' <' + user.email + '>';
}
```

### 目录结构规范
```
src/
├── components/     # React 组件
├── services/      # 业务服务
├── utils/         # 工具函数
├── types/         # TypeScript 类型定义
├── hooks/         # 自定义 Hooks
└── entrypoints/   # 入口文件
```

### 提交规范
#### 提交消息格式
```
类型(范围): 简要描述

详细描述（可选）

关联问题: #123
```

#### 提交类型
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具

#### 示例
```
feat(api): 添加 OpenAI 兼容 API 支持

- 实现 OpenAI 格式请求适配
- 添加流式响应支持
- 更新相关文档

关联问题: #45
```

## 测试指南

### 测试类型
#### 单元测试
- 测试单个函数或组件
- 使用 Jest 和 React Testing Library
- 覆盖核心业务逻辑

#### 集成测试
- 测试模块间交互
- 模拟外部依赖
- 验证数据流

#### 端到端测试
- 测试完整用户流程
- 使用 Playwright 或 Cypress
- 验证关键业务路径

### 测试文件结构
```
__tests__/
├── unit/          # 单元测试
├── integration/   # 集成测试
└── e2e/          # 端到端测试
```

### 测试示例
```typescript
// 单元测试示例
import { formatUserName } from '../utils/formatter';

describe('formatUserName', () => {
  it('应该正确格式化用户名', () => {
    const user = { name: '张三', email: 'zhangsan@example.com' };
    expect(formatUserName(user)).toBe('张三 <zhangsan@example.com>');
  });

  it('应该处理空值情况', () => {
    expect(formatUserName(null)).toBe('');
  });
});
```

### 测试运行
```bash
# 运行所有测试
bun test

# 运行特定测试文件
bun test __tests__/unit/formatter.test.ts

# 运行测试并生成覆盖率报告
bun test --coverage
```

## 调试技巧

### 开发调试
```bash
# 启用调试模式
bun run dev --debug

# 使用 Node.js 调试器
bun --inspect src/entrypoints/cli.tsx
```

### 浏览器调试
- 使用 React DevTools
- 使用 Redux DevTools（如使用）
- 网络请求监控

### 性能调试
```bash
# 内存分析
bun --inspect --inspect-brk src/entrypoints/cli.tsx

# CPU 分析
node --prof dist/cli.js
```

### 日志调试
```typescript
// 开发环境日志
import debug from 'debug';
const log = debug('cloud-code:api');

log('API request: %o', request);
```

## 贡献流程

### 1. 准备工作
- Fork 项目仓库
- 创建特性分支
- 设置开发环境

### 2. 开发工作
- 遵循代码规范
- 编写测试用例
- 更新相关文档

### 3. 提交代码
- 编写清晰的提交消息
- 确保测试通过
- 更新 CHANGELOG（如需要）

### 4. 创建 Pull Request
- 描述变更内容
- 关联相关问题
- 提供测试结果

### 5. 代码审查
- 响应审查意见
- 进行必要修改
- 等待合并

### 代码审查指南
#### 审查重点
- 代码正确性
- 测试覆盖
- 性能影响
- 安全考虑
- 文档更新

#### 审查意见
- 具体明确，避免模糊
- 提供改进建议
- 尊重开发者
- 关注代码而非个人

## 开发工具和脚本

### 常用脚本
```bash
# 开发模式
bun run dev

# 构建项目
bun run build

# 代码检查
bun run lint

# 代码格式化
bun run format

# 类型检查
bun run type-check
```

### 自动化工具
- **Husky**: Git hooks
- **lint-staged**: 暂存文件检查
- **Commitizen**: 提交消息规范

## 学习资源

### 项目相关
- [项目架构](../architecture/README.md)
- [API 文档](../api/README.md)
- [部署指南](../deployment/README.md)
- [PATH 环境变量配置指南](./path-configuration-guide.md)
- [PATH 环境变量配置指南](./path-configuration-guide.md)

### 技术栈
- **Bun**: https://bun.sh/docs
- **TypeScript**: https://www.typescriptlang.org/docs
- **React**: https://react.dev/learn
- **Commander.js**: https://github.com/tj/commander.js

### 最佳实践
- React 最佳实践
- TypeScript 高级技巧
- CLI 工具开发
- 测试驱动开发

### 开发文档
- [PATH 环境变量配置指南](./path-configuration-guide.md)
- [文档系统操作指南](./documentation-system-operations-guide.md)
- [文档系统触发提示词指南](./trigger-prompt-examples-guide.md)

## 问题解决

### 常见问题
#### 依赖安装失败
```bash
# 清理缓存
bun clean

# 重新安装
bun install --force
```

#### 类型检查错误
```bash
# 检查类型错误
bun run type-check

# 生成类型定义
bun run build:types
```

#### 测试失败
```bash
# 运行特定测试查看详细输出
bun test --verbose

# 更新测试快照
bun test --updateSnapshot
```

### 寻求帮助
- 查看项目文档
- 搜索现有问题
- 创建新的 Issue
- 参与社区讨论

---

**良好的开发实践是项目成功的关键。遵循规范、编写测试、保持代码质量，共同构建优秀的项目。**