# 抖音热榜定时推送到飞书

这个项目可以定时抓取抖音热榜数据，并通过 Webhook 推送到飞书群聊。

## 功能特性

- ⏰ 定时抓取抖音热榜（默认每小时一次）
- 📊 获取最新的热门话题和热度值
- 🤖 自动推送到飞书群聊
- 💬 支持多种消息格式（文本、富文本、交互式卡片）
- 📝 完整的日志记录
- 🐳 支持 Docker 部署
- 🚀 支持 GitHub Actions 自动化运行
- ⚙️ 可自定义执行频率

## 项目结构

```
.
├── main.py                        # 主程序入口（本地/Docker运行）
├── run_once.py                    # 单次执行脚本（GitHub Actions）
├── douyin_scraper.py              # 抖音热榜抓取模块
├── feishu_notifier.py             # 飞书通知模块
├── requirements.txt               # Python 依赖
├── .env.example                   # 环境变量示例
├── .gitignore                     # Git 忽略文件
├── Dockerfile                     # Docker 镜像配置
├── docker-compose.yml             # Docker Compose 配置
├── .github/
│   └── workflows/
│       ├── scrape-and-notify.yml  # GitHub Actions 工作流
│       └── README.md              # 工作流说明文档
├── docs/
│   └── GITHUB_ACTIONS_GUIDE.md    # GitHub Actions 完整指南
└── README.md                      # 项目说明
```

## 部署方式对比

| 部署方式 | 优点 | 缺点 | 适用场景 |
|---------|------|------|---------|
| **GitHub Actions** ⭐推荐 | 免费、无需服务器、配置简单 | 依赖 GitHub、有执行时间限制 | 个人使用、轻量级定时任务 |
| **Docker 部署** | 稳定、可控、适合生产环境 | 需要服务器资源 | 企业使用、需要高可用性 |
| **本地运行** | 开发调试方便 | 需要保持程序运行、不适合长期使用 | 开发测试、快速验证 |

## 快速开始

### 前置要求

- Python 3.8+（本地/Docker 运行需要）
- 飞书机器人 Webhook URL
- GitHub 账号（使用 GitHub Actions 需要）

### 获取飞书 Webhook URL

1. 在飞书群聊中，点击右上角设置按钮
2. 选择「群机器人」->「添加机器人」
3. 选择「自定义机器人」
4. 设置机器人名称和描述
5. 复制生成的 Webhook URL

### 安装和配置

#### 方法一：本地运行

1. **克隆项目**

```bash
git clone <your-repo-url>
cd New-repository
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的飞书 Webhook URL
# FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url
```

4. **运行程序**

```bash
python main.py
```

#### 方法二：Docker 部署

1. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，填入配置
```

2. **使用 Docker Compose 启动**

```bash
docker-compose up -d
```

3. **查看日志**

```bash
docker-compose logs -f
```

4. **停止服务**

```bash
docker-compose down
```

#### 方法三：GitHub Actions 自动化运行 ⭐推荐

这是最简单的方式，无需自己的服务器，利用 GitHub Actions 免费的运行时间。

**优势：**
- 完全免费
- 无需服务器
- 自动运行，无需维护
- 可视化的执行日志
- 支持手动触发

**步骤：**

1. **Fork 本项目到你的 GitHub 账号**

2. **配置 GitHub Secrets**

进入你的仓库设置：`Settings` → `Secrets and variables` → `Actions` → `New repository secret`

添加以下 Secret：
- Name: `FEISHU_WEBHOOK_URL`
- Value: 你的飞书机器人 Webhook URL

3. **自定义执行频率（可选）**

编辑 `.github/workflows/scrape-and-notify.yml` 文件中的 `cron` 表达式。

默认配置是每小时执行一次：
```yaml
schedule:
  - cron: '0 * * * *'
```

常用频率示例：
```yaml
# 每2小时执行一次
- cron: '0 */2 * * *'

# 每天早上9点、中午12点、下午6点执行（UTC时间，需要转换）
- cron: '0 1,4,10 * * *'  # 对应北京时间 9点、12点、18点

# 工作日每天早上9点执行
- cron: '0 1 * * 1-5'  # UTC 1点 = 北京时间 9点
```

**⚠️ 时区注意事项：**
GitHub Actions 使用 UTC 时间，中国时区（UTC+8）需要减去8小时。
- 北京时间 9:00 → UTC 1:00 → `cron: '0 1 * * *'`
- 北京时间 18:00 → UTC 10:00 → `cron: '0 10 * * *'`

详细的 Cron 配置说明请查看：[.github/workflows/README.md](.github/workflows/README.md)

**📖 完整的图文教程：**
👉 [GitHub Actions 部署完整指南](docs/GITHUB_ACTIONS_GUIDE.md) - 包含详细步骤说明、常见问题排查、时区转换表等

4. **启用 GitHub Actions**

- 进入仓库的 `Actions` 标签页
- 如果显示被禁用，点击 "I understand my workflows, go ahead and enable them"
- 选择工作流 "抓取抖音热榜并推送到飞书"
- 点击 "Enable workflow"

5. **手动触发测试（可选）**

在 Actions 页面，选择工作流，点击 "Run workflow" 按钮手动触发一次，验证配置是否正确。

6. **查看执行日志**

在 `Actions` 标签页可以查看每次执行的详细日志。

## 配置说明

在 `.env` 文件中可以配置以下参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook URL | 必填 |
| `SCRAPE_INTERVAL_HOURS` | 抓取间隔（小时） | 1 |
| `LOG_LEVEL` | 日志级别（DEBUG/INFO/WARNING/ERROR） | INFO |

## 测试模块

### 测试抖音热榜抓取

```bash
python douyin_scraper.py
```

### 测试飞书消息发送

```bash
# 需要先配置 .env 文件
python feishu_notifier.py
```

## 消息格式示例

程序会发送类似以下格式的消息到飞书群：

```
📊 抖音热榜 Top10 (2024-01-22 10:00:00)

🥇 热门话题1 [热] 🔥1.2亿
🥈 热门话题2 🔥8500万
🥉 热门话题3 [新] 🔥6200万
4. 热门话题4 🔥4800万
...
```

## 常见问题

### 1. 如何修改抓取间隔？

编辑 `.env` 文件中的 `SCRAPE_INTERVAL_HOURS` 参数。

### 2. 为什么收不到消息？

- 检查 Webhook URL 是否正确
- 检查网络连接是否正常
- 查看日志文件 `douyin_hot_scraper.log` 获取详细错误信息

### 3. GitHub Actions 没有按时执行？

GitHub Actions 可能会有几分钟的延迟，这是正常现象。如果长时间未执行：
- 检查工作流是否已启用
- 检查仓库是否为公开仓库（私有仓库有免费额度限制）
- 查看 Actions 页面是否有错误信息

### 4. 如何修改 GitHub Actions 的执行频率？

编辑 `.github/workflows/scrape-and-notify.yml` 文件中的 `cron` 表达式。注意时区转换（GitHub Actions 使用 UTC 时间）。

详细说明请查看：[.github/workflows/README.md](.github/workflows/README.md)

### 5. GitHub Actions 执行失败怎么办？

- 检查 Secrets 中的 `FEISHU_WEBHOOK_URL` 是否配置正确
- 在 Actions 页面查看详细的错误日志
- 确认飞书 Webhook URL 是否有效

### 6. 如何在后台运行（本地部署）？

**使用 screen 或 tmux：**

```bash
screen -S douyin-scraper
python main.py
# 按 Ctrl+A 然后按 D 离开 screen
```

**使用 systemd（Linux）：**

创建服务文件 `/etc/systemd/system/douyin-scraper.service`：

```ini
[Unit]
Description=Douyin Hot List Scraper
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/New-repository
ExecStart=/usr/bin/python3 /path/to/New-repository/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable douyin-scraper
sudo systemctl start douyin-scraper
```

## 开发说明

### 项目依赖

- `requests`: HTTP 请求库
- `schedule`: 任务调度库
- `python-dotenv`: 环境变量管理
- `pyyaml`: YAML 配置文件支持

### 添加新功能

1. 修改 `douyin_scraper.py` 添加新的抓取功能
2. 修改 `feishu_notifier.py` 添加新的消息格式
3. 在 `main.py` 中集成新功能

## 注意事项

- 请遵守抖音的使用条款和 robots.txt
- 不要过于频繁地请求，建议间隔至少 1 小时
- 抖音 API 可能会变化，如遇问题请及时更新
- 确保服务器网络稳定，能够访问抖音和飞书 API

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.1.0 (2024-01-22)

- 新增 GitHub Actions 支持
- 可自定义执行频率（通过修改 cron 表达式）
- 新增单次执行脚本 `run_once.py`
- 新增详细的 GitHub Actions 配置文档
- 优化错误处理和日志输出

### v1.0.0 (2024-01-22)

- 初始版本发布
- 支持定时抓取抖音热榜
- 支持推送到飞书群
- 支持 Docker 部署
