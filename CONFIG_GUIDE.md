# 配置指南 - 自定义 API 和内容板块

本项目支持灵活的配置系统，可以自定义数据源、API 接口和内容板块。

## 🎯 快速开始

### 方式一：使用环境变量（推荐）

最简单的方式是在 `.env` 文件中配置：

```bash
# 启用新能源汽车板块
ENABLED_CATEGORIES=new_energy_vehicle

# 启用多个板块（逗号分隔）
ENABLED_CATEGORIES=new_energy_vehicle,entertainment

# 自定义热榜数量
HOT_LIST_LIMIT=30
```

### 方式二：修改配置文件

编辑 `config.yaml` 文件，修改 `enabled` 字段：

```yaml
content_categories:
  new_energy_vehicle:
    enabled: true  # 改为 true 启用
    name: "新能源汽车"
    keywords: [...]
```

## 📋 预设内容板块

### 1. 综合热榜（默认）
- **ID**: `all`
- **说明**: 显示所有热门内容，不过滤
- **适用场景**: 获取全面的热点信息

### 2. 新能源汽车 🚗
- **ID**: `new_energy_vehicle`
- **关键词**: 新能源、电动车、特斯拉、比亚迪、蔚来、理想、小鹏、问界、充电桩、电池、续航、自动驾驶
- **适用场景**: 关注新能源汽车行业动态

**启用方法**:
```bash
# .env 文件
ENABLED_CATEGORIES=new_energy_vehicle
```

### 3. 娱乐八卦 🎬
- **ID**: `entertainment`
- **关键词**: 电影、电视剧、明星、综艺、音乐、演唱会、偶像、娱乐、八卦、影视
- **适用场景**: 关注娱乐圈动态

**启用方法**:
```bash
ENABLED_CATEGORIES=entertainment
```

### 4. 科技资讯 💻
- **ID**: `technology`
- **关键词**: 科技、AI、人工智能、手机、电脑、芯片、5G、苹果、华为、小米、互联网、APP
- **适用场景**: 关注科技行业资讯

**启用方法**:
```bash
ENABLED_CATEGORIES=technology
```

### 5. 财经资讯 💰
- **ID**: `finance`
- **关键词**: 股市、基金、投资、经济、金融、理财、A股、港股、美股、房价、GDP
- **适用场景**: 关注财经金融信息

**启用方法**:
```bash
ENABLED_CATEGORIES=finance
```

## 🔧 自定义板块

### 创建自己的板块

编辑 `config.yaml`，添加新的板块：

```yaml
content_categories:
  # 自定义：游戏板块
  gaming:
    enabled: true
    name: "游戏资讯"
    keywords:
      - "游戏"
      - "电竞"
      - "王者荣耀"
      - "和平精英"
      - "原神"
      - "Steam"
      - "Switch"
    description: "游戏相关热点"
```

然后在 `.env` 中启用：

```bash
ENABLED_CATEGORIES=gaming
```

### 关键词匹配规则

- 只要热榜标题**包含任意一个关键词**，就会被筛选出来
- 关键词不区分大小写
- 支持中英文关键词
- 如果 `keywords` 为空数组 `[]`，则不过滤，显示所有内容

## 🌐 自定义数据源

### 添加新的 API

编辑 `config.yaml` 的 `data_sources` 部分：

```yaml
data_sources:
  # 添加微博热搜
  weibo:
    enabled: true
    name: "微博热搜"
    apis:
      - url: "https://weibo.com/ajax/side/hotSearch"
        type: "hot_search"
        description: "综合热搜"

  # 添加知乎热榜
  zhihu:
    enabled: true
    name: "知乎热榜"
    apis:
      - url: "https://www.zhihu.com/api/v4/creators/rank/hot"
        type: "hot"
        description: "热榜"
```

### 使用环境变量选择数据源

```bash
# 只使用抖音
ENABLED_DATA_SOURCES=douyin

# 使用多个数据源（会依次尝试）
ENABLED_DATA_SOURCES=douyin,weibo,zhihu
```

## 📝 配置示例

### 示例 1：专注新能源汽车

```bash
# .env 文件
ENABLED_CATEGORIES=new_energy_vehicle
HOT_LIST_LIMIT=30
SCRAPE_INTERVAL_HOURS=2
```

**效果**: 每2小时抓取 Top30 新能源汽车相关热点

### 示例 2：娱乐+科技双板块

```bash
# .env 文件
ENABLED_CATEGORIES=entertainment,technology
HOT_LIST_LIMIT=20
```

**效果**: 抓取娱乐和科技相关的 Top20 热点

### 示例 3：完全自定义

创建自己的 `config.yaml`：

```yaml
content_categories:
  my_interests:
    enabled: true
    name: "我关注的话题"
    keywords:
      - "Python"
      - "AI"
      - "创业"
      - "投资"
      - "健身"
    description: "个人兴趣相关"
```

```bash
# .env 文件
ENABLED_CATEGORIES=my_interests
```

## ⚙️ 显示配置

### 自定义消息格式

编辑 `config.yaml` 的 `display` 部分：

```yaml
display:
  # 是否显示数据来源（如"抖音热榜"）
  show_source: true

  # 是否显示热度值
  show_hot_value: true

  # 是否显示标签（如 [热]、[新]）
  show_label: true

  # 标题格式（支持变量）
  # {source} - 数据源名称
  # {category} - 板块名称
  # {count} - 热榜数量
  # {time} - 时间戳
  title_format: "📊 {source} - {category} Top{count}"
```

### 标题格式示例

```yaml
# 简洁版
title_format: "{source} Top{count}"
# 效果：抖音热榜 Top20

# 详细版
title_format: "📊 {source} - {category} ({time})"
# 效果：📊 抖音热榜 - 新能源汽车 (2024-01-23 10:00:00)

# 仅板块
title_format: "{category} 热点 Top{count}"
# 效果：新能源汽车 热点 Top20
```

## 🔄 配置优先级

1. **环境变量** (`.env` 文件) - 最高优先级
2. **配置文件** (`config.yaml`)
3. **默认配置** (代码内置)

**推荐做法**:
- 在 `config.yaml` 中定义所有可用的板块和数据源
- 在 `.env` 中通过 `ENABLED_CATEGORIES` 快速切换启用哪些板块

## 📊 GitHub Actions 配置

在 GitHub Actions 中使用自定义配置：

1. 进入仓库的 `Settings` → `Secrets and variables` → `Actions`

2. 添加新的 Secret：
   - Name: `ENABLED_CATEGORIES`
   - Value: `new_energy_vehicle`

3. 或者直接编辑 `.github/workflows/scrape-and-notify.yml`：

```yaml
- name: 运行抓取任务
  env:
    FEISHU_WEBHOOK_URL: ${{ secrets.FEISHU_WEBHOOK_URL }}
    ENABLED_CATEGORIES: new_energy_vehicle  # 添加这行
    HOT_LIST_LIMIT: 30  # 可选
  run: |
    python run_once.py
```

## ❓ 常见问题

### Q: 如何知道板块关键词是否有效？

查看运行日志，会显示过滤前后的数量：

```
INFO - 板块 '新能源汽车' 过滤后: 5/20 条
```

这表示从 20 条热榜中筛选出了 5 条相关内容。

### Q: 为什么没有筛选出任何内容？

可能原因：
1. 关键词太具体，试试更宽泛的关键词
2. 当前热榜中确实没有相关内容
3. 关键词拼写错误

### Q: 可以同时启用多个板块吗？

不建议。目前每次只推送一个板块的内容。如果需要多个板块，建议：
- 创建多个 GitHub Actions 工作流
- 或在本地运行时分别配置

### Q: 如何恢复默认配置？

```bash
# .env 文件
ENABLED_CATEGORIES=all  # 或留空
```

或删除 `config.yaml`，程序会使用内置默认配置。

## 🚀 进阶技巧

### 技巧 1：根据时间切换板块

创建多个工作流，在不同时间推送不同板块：

```yaml
# .github/workflows/morning-tech.yml
schedule:
  - cron: '0 1 * * *'  # 每天早上9点（北京时间）
env:
  ENABLED_CATEGORIES: technology
```

```yaml
# .github/workflows/evening-entertainment.yml
schedule:
  - cron: '0 10 * * *'  # 每天晚上6点（北京时间）
env:
  ENABLED_CATEGORIES: entertainment
```

### 技巧 2：组合关键词

将多个相关主题合并为一个自定义板块：

```yaml
my_tech_finance:
  enabled: true
  name: "科技金融"
  keywords:
    - "AI"
    - "区块链"
    - "金融科技"
    - "数字货币"
    - "投资"
```

### 技巧 3：排除某些内容

虽然配置系统不支持排除关键词，但可以通过精心设计关键词列表来达到类似效果。

例如，只关注特定品牌的新能源车：

```yaml
tesla_only:
  enabled: true
  name: "特斯拉专题"
  keywords:
    - "特斯拉"
    - "Tesla"
    - "马斯克"
    - "Model"
```

## 📚 更多资源

- [主 README](../README.md) - 项目总体说明
- [GitHub Actions 指南](./GITHUB_ACTIONS_GUIDE.md) - 部署指南
- [config.yaml](../config.yaml) - 完整配置文件示例

---

如有疑问，请提交 Issue 或查看项目文档。
