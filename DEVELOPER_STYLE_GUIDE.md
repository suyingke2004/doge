# Google Developer Documentation Style Guide

This document outlines the key principles of the Google Developer Documentation Style Guide. For the full guide, please refer to [the official documentation](https://developers.google.com/style).

## Key Principles

*   **Audience:** Write for a global, technical audience.
*   **Voice and Tone:** Use an accessible, inclusive, and consistent voice. The tone should be professional and helpful.
*   **Tense and Voice:** Prefer the active voice and present tense.
*   **Clarity:** Prioritize clarity above all else. It's acceptable to break the rules for the sake of clarity, as long as the writing remains consistent.

## Formatting and Punctuation

*   Follow the specific rules for formatting, punctuation, and linking outlined in the guide.
*   Pay close attention to the guidelines for documenting computer interfaces, such as APIs and command-line syntax.

## Style Hierarchy

1.  **Project-specific style guide:** If a project has its own style guide, it should be followed first.
2.  **Google Developer Documentation Style Guide:** This guide should be followed next.
3.  **Third-party style guides:** If a specific issue is not covered by the above, refer to a third-party resource like the Chicago Manual of Style.

## Inclusivity

*   Use gender-neutral language.
*   Avoid ableist or offensive terms.

## 开发环境

请在开始开发前，确保您已经激活了名为 `news_agent` 的 Conda 环境。

```bash
conda activate news_agent
```

## 测试规范

所有测试用例应使用 pytest 编写，并放置在 `tests` 文件夹下。

1. 所有功能模块都应有对应的测试用例
2. 测试用例应覆盖正常流程和异常情况
3. 使用 pytest 作为测试框架
4. 测试文件命名应以 `test_` 开头
5. 测试函数命名应以 `test_` 开头
6. 使用 fixtures 管理测试依赖
7. 对外部服务（如API）的测试应使用 mock 或模拟数据
8. 断言应明确且具有描述性

通过以下命令运行所有测试：

```bash
python -m pytest tests/ -v
```

或运行特定测试文件：

```bash
python -m pytest tests/test_file.py -v
```