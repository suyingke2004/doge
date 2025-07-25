# 内容交付系统配置说明

内容交付系统允许用户将生成的新闻通讯通过邮件发送或导出为PDF文件。

## 邮件发送功能

### 配置SendGrid

1. 注册SendGrid账户并获取API密钥：
   - 访问 https://sendgrid.com/
   - 注册账户并完成验证
   - 在控制台创建API密钥（Settings > API Keys）

2. 配置环境变量：
   在`.env`文件中添加以下内容：
   ```
   SENDGRID_API_KEY=your_sendgrid_api_key_here
   FROM_EMAIL=your_verified_sender_email@example.com
   ```

### 使用邮件发送功能

用户可以通过以下方式请求发送邮件：
- "请将这份新闻通讯通过邮件发送给我"
- "请将内容发送到我的邮箱xxx@example.com"
- "我想通过邮件接收这份报告"

## PDF导出功能

### 系统要求

PDF导出功能依赖于`weasyprint`库，该库需要系统中安装`wkhtmltopdf`工具。

在Ubuntu/Debian系统上安装：
```bash
sudo apt-get install wkhtmltopdf
```

在CentOS/RHEL系统上安装：
```bash
sudo yum install wkhtmltopdf
```

在macOS上安装：
```bash
brew install wkhtmltopdf
```

### 使用PDF导出功能

用户可以通过以下方式请求导出PDF：
- "请将这份新闻通讯导出为PDF"
- "我想将内容保存为PDF文件"
- "请生成这份报告的PDF版本"

## 工具说明

### Send_Email工具
- 功能：将内容通过邮件发送给指定收件人
- 参数：
  - `to_email`：收件人邮箱地址
  - `subject`：邮件主题
  - `content`：邮件内容

### Export_PDF工具
- 功能：将内容导出为PDF文件
- 参数：
  - `content`：要导出的内容（支持Markdown格式）
  - `filename`：导出的PDF文件名（可选，默认为newsletter.pdf）

## 注意事项

1. 邮件发送功能需要有效的SendGrid API密钥和已验证的发件人邮箱
2. PDF导出功能需要系统中安装wkhtmltopdf工具
3. 导出的PDF文件存储在临时目录中，用户需要及时下载保存