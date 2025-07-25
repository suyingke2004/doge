# 测试规范

所有测试用例应使用 pytest 编写，并放置在 `tests` 文件夹下。

## 测试原则

1. 所有功能模块都应有对应的测试用例
2. 测试用例应覆盖正常流程和异常情况
3. 使用 pytest 作为测试框架
4. 测试文件命名应以 `test_` 开头
5. 测试函数命名应以 `test_` 开头
6. 使用 fixtures 管理测试依赖
7. 对外部服务（如API）的测试应使用 mock 或模拟数据
8. 断言应明确且具有描述性

## 测试执行

通过以下命令运行所有测试：

```bash
python -m pytest tests/ -v
```

或运行特定测试文件：

```bash
python -m pytest tests/test_file.py -v
```