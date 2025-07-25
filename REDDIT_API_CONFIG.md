# Reddit API配置说明

要在项目中使用Reddit搜索功能，您需要在.env文件中配置以下环境变量：

```
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=news_agent by u/yourusername
```

获取这些凭据的步骤：

1. 访问 https://www.reddit.com/prefs/apps
2. 点击"创建应用"或"create app"
3. 填写应用名称，例如"news_agent"
4. 选择应用类型为"脚本"（script）
5. 填写重定向URI，可以使用默认值 http://localhost:8080
6. 创建应用后，您将获得CLIENT_ID（应用ID）和CLIENT_SECRET（密钥）
7. 将这些值添加到您的.env文件中

注意：
- REDDIT_USER_AGENT是可选的，默认值为"news_agent by u/yourusername"
- 请确保不要将这些凭据提交到代码仓库中