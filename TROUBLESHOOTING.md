# 🔧 网页版故障排除指南

## 问题：点击刷新后数据没有更新

### ✅ 已实施的解决方案

我们已经在代码中添加了以下缓存清除机制：

1. **HTTP 缓存控制 Meta 标签**
   ```html
   <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
   <meta http-equiv="Pragma" content="no-cache">
   <meta http-equiv="Expires" content="0">
   ```

2. **强制不缓存的请求头**
   ```javascript
   fetch('data/hot_list.json', {
       headers: {
           'Cache-Control': 'no-cache, no-store, must-revalidate',
           'Pragma': 'no-cache'
       },
       cache: 'no-store'
   })
   ```

3. **时间戳 + 随机数缓存破坏**
   - 每次请求都会添加唯一的参数：`?v=1706088000000_abc123`

4. **双时间戳显示**
   - **数据更新时间**：热榜数据的抓取时间
   - **加载时间**：网页加载数据的当前时间
   - 如果这两个时间相差很远，说明缓存生效了

### 🔍 如何判断数据是否真的更新了

访问网页后，查看页面上方的信息框：

```
⏰ 数据更新: 2026-01-24 14:33:51  ← 这是数据的抓取时间
🔄 加载时间: 2026-01-28 15:45:20  ← 这是你当前加载的时间
📊 数据来源: 抖音热榜
```

- **如果"加载时间"是当前时间** → 说明网页成功加载了
- **如果"数据更新"时间很旧** → 说明 GitHub Actions 还没有运行，数据确实是旧的

### 🚀 强制刷新的方法

#### 方法 1：硬刷新（清除浏览器缓存）

**Windows/Linux:**
- `Ctrl + F5` 或 `Ctrl + Shift + R`

**Mac:**
- `Command + Shift + R`

**移动端:**
1. 长按刷新按钮
2. 选择"硬刷新"或"清空缓存并硬刷新"

#### 方法 2：隐私/无痕模式

1. 打开浏览器的隐私浏览模式（Incognito/Private）
2. 访问网页链接
3. 这样不会使用任何缓存

#### 方法 3：清除浏览器缓存

**Chrome/Edge:**
1. 按 `F12` 打开开发者工具
2. 右键点击刷新按钮
3. 选择"清空缓存并硬性重新加载"

**Firefox:**
1. 按 `Ctrl + Shift + Delete`
2. 选择"缓存"
3. 点击"立即清除"

### ⏰ 数据更新频率

GitHub Actions 工作流每小时自动运行一次，抓取最新数据：

- **工作流文件**: `.github/workflows/update-web-data.yml`
- **执行频率**: `0 * * * *` (每小时的第 0 分钟)
- **查看执行记录**: GitHub 仓库 → Actions 标签 → "更新网页热榜数据"

### 📍 检查 GitHub Pages 设置

确保 GitHub Pages 已正确配置：

1. 访问仓库：`https://github.com/wanghaiping220-collab/douyin-Trend`
2. 点击 **Settings** → **Pages**
3. 确认配置：
   - **Source**: `gh-pages` 分支
   - **Folder**: `/ (root)`
4. 页面顶部应显示：
   ```
   ✅ Your site is live at https://wanghaiping220-collab.github.io/douyin-Trend/
   ```

### 🔄 手动触发数据更新

如果想立即更新数据（不等一小时）：

1. 进入仓库的 **Actions** 标签
2. 选择 **"更新网页热榜数据"** 工作流
3. 点击 **"Run workflow"** 按钮
4. 选择分支（通常是 `main` 或当前分支）
5. 点击绿色的 **"Run workflow"** 按钮
6. 等待 1-2 分钟，工作流完成后：
   - 数据会自动更新
   - 自动部署到 GitHub Pages
7. 然后用 **Ctrl+F5** 硬刷新网页

### 🌐 GitHub Pages 缓存延迟

GitHub Pages 使用 CDN，可能会有缓存延迟：

- **正常延迟**: 1-5 分钟
- **最长可能**: 10-15 分钟

**解决方法**：
1. 等待 5-10 分钟
2. 使用硬刷新（Ctrl+F5）
3. 或使用隐私浏览模式

### 🐛 仍然看不到更新？

#### 1. 检查工作流是否成功运行

进入 **Actions** 标签，查看最近的运行记录：

- ✅ 绿色勾号 = 成功
- ❌ 红色叉号 = 失败（点击查看日志）
- ⏱️ 黄色圆圈 = 运行中

#### 2. 检查 gh-pages 分支的数据文件

1. 切换到 `gh-pages` 分支
2. 查看 `data/hot_list.json` 文件
3. 检查文件的 `update_time` 字段

#### 3. 检查浏览器控制台

按 `F12` 打开开发者工具，查看：

- **Console 标签**: 是否有 JavaScript 错误
- **Network 标签**:
  - 找到 `hot_list.json` 请求
  - 查看响应内容
  - 确认状态码是 200

#### 4. 验证 JSON 数据

直接访问 JSON 文件查看原始数据：

```
https://wanghaiping220-collab.github.io/douyin-Trend/data/hot_list.json
```

在浏览器中打开这个链接，应该能看到 JSON 格式的热榜数据。

### 💡 最佳实践

1. **定期检查 Actions**：确保工作流正常运行
2. **使用硬刷新**：每次想看最新数据时使用 `Ctrl+F5`
3. **查看时间戳**：通过页面上显示的双时间戳判断数据新鲜度
4. **手动触发**：重大新闻时可手动触发工作流立即更新

### 📞 获取帮助

如果以上方法都无法解决问题，请检查：

1. GitHub Actions 的执行日志
2. 浏览器的开发者工具控制台
3. 网络连接是否正常

---

**提示**：大部分刷新问题都是浏览器缓存导致的，使用 `Ctrl+F5` 硬刷新通常能解决！
