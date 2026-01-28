# 📊 网页版热榜使用指南

这是一个无需服务器和域名的网页版热榜展示系统，完全部署在 GitHub Pages 上。

## ✨ 特性

- 🎨 **精美界面**：渐变紫色背景，动画卡片设计
- 📱 **响应式**：支持手机、平板、电脑访问
- 🔄 **自动更新**：每小时自动抓取最新数据
- ⚡ **实时刷新**：网页每 5 分钟自动刷新，也支持手动刷新
- 🚀 **免费部署**：完全基于 GitHub Pages，无需任何费用

## 🚀 快速开始

### 第一步：启用 GitHub Pages

1. 打开你的 GitHub 仓库页面
2. 点击顶部的 **Settings**（设置）标签
3. 在左侧菜单找到 **Pages**
4. 在 **Source**（来源）下拉菜单中选择 **`gh-pages`**
5. 点击 **Save**（保存）

### 第二步：等待部署

- 首次部署需要等待 1-2 分钟
- GitHub Actions 会自动运行工作流
- 你可以在 **Actions** 标签查看部署进度

### 第三步：访问网页

部署完成后，你的网页地址将是：

```
https://<你的用户名>.github.io/<仓库名>/
```

例如：
```
https://wanghaiping220-collab.github.io/New-repository/
```

## 📋 查看部署状态

### 方法 1：通过 Settings 查看

1. 进入仓库的 **Settings** > **Pages**
2. 部署成功后会显示绿色提示：
   ```
   ✅ Your site is live at https://...
   ```

### 方法 2：通过 Actions 查看

1. 点击仓库的 **Actions** 标签
2. 找到名为 **"更新网页热榜数据"** 的工作流
3. 查看最近一次运行的状态
   - ✅ 绿色勾号 = 成功
   - ❌ 红色叉号 = 失败（可点击查看日志）

## 🔧 工作原理

### 自动化流程

```
每小时触发
    ↓
抓取热榜数据
    ↓
保存为 JSON 文件 (docs/data/hot_list.json)
    ↓
提交到仓库
    ↓
自动部署到 GitHub Pages
    ↓
网页自动显示最新数据
```

### 文件结构

```
docs/
├── index.html              # 网页界面
└── data/
    └── hot_list.json       # 热榜数据（每小时更新）

scripts/
└── fetch_data_for_web.py   # 数据抓取脚本

.github/workflows/
└── update-web-data.yml     # 自动更新工作流
```

## 🎨 网页功能

### 自动刷新
- 网页每 5 分钟自动刷新一次
- 确保你总能看到最新数据

### 手动刷新
- 点击右上角的 **🔄 刷新** 按钮
- 立即加载最新数据

### 排名标识
- 🥇 第一名 - 金色
- 🥈 第二名 - 银色
- 🥉 第三名 - 铜色

### 热度显示
- 自动格式化热度值
- 例如：200000000 → 2.0亿
- 例如：10000 → 1.0万

### 标签显示
- 热门内容会显示 **[热]** 标签
- 红色背景突出显示

## ⚙️ 自定义配置

### 修改更新频率

编辑 `.github/workflows/update-web-data.yml`：

```yaml
on:
  schedule:
    - cron: '0 * * * *'  # 每小时更新
```

常用频率：
- 每小时：`'0 * * * *'`
- 每 30 分钟：`'*/30 * * * *'`
- 每天 8 点：`'0 0 * * *'`（注意：这是 UTC 时间）

### 修改显示数量

编辑 `scripts/fetch_data_for_web.py`：

```python
hot_list = scraper.fetch_hot_list(limit=20, category=category)
```

修改 `limit` 参数（建议 10-50 条）

### 修改内容板块

在 GitHub 仓库的 **Settings** > **Secrets and variables** > **Actions** > **Variables**：

添加变量：
- 名称：`CONTENT_CATEGORY`
- 值：`entertainment`（娱乐）、`technology`（科技）等

## 🐛 故障排除

### 问题 1：网页显示 404

**可能原因**：
- GitHub Pages 未启用
- 分支选择错误

**解决方法**：
1. 确认 Settings > Pages 中选择了 `gh-pages` 分支
2. 等待 1-2 分钟让 GitHub 部署生效

### 问题 2：数据显示为测试数据

**原因**：
- API 暂时不可用
- 系统自动使用测试数据确保网页可用

**说明**：
- 这是正常的降级处理
- 网页会显示"数据来源: 测试数据"
- 下次更新时会尝试获取真实数据

### 问题 3：工作流运行失败

**排查步骤**：
1. 进入 Actions 标签
2. 点击失败的工作流
3. 查看错误日志
4. 常见错误：
   - 权限问题：检查仓库的 Actions 权限设置
   - 依赖问题：检查 requirements.txt

## 📱 分享你的热榜

部署成功后，你可以：

1. **分享链接**：把网页链接分享给朋友
2. **添加书签**：在浏览器中收藏网页
3. **手机访问**：网页完全适配移动端
4. **嵌入其他网站**：使用 iframe 嵌入

## 🔗 相关链接

- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [项目主文档](../README.md)
- [配置指南](CONFIG_GUIDE.md)
- [GitHub Actions 指南](GITHUB_ACTIONS_GUIDE.md)

## 💡 提示

- 数据每小时自动更新，无需手动操作
- 网页完全静态，加载速度快
- 支持所有现代浏览器
- 数据永久保存在仓库中，可查看历史记录

---

🎉 **现在你拥有了一个完全免费、自动更新的热榜网页！**
