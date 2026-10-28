# Ghost Light · 英语排练场

为想登上百老汇的演员做的英语学习 App：台词跟读打分、AI 对手戏、剧场词汇，以及可以持续更新的剧本库。

## 剧本库

| 剧目 | 作者 | 名场景（逐句现代英语 + 中文 + 讲解 + 录音） |
|---|---|---|
| Romeo and Juliet 罗密欧与朱丽叶 | 莎士比亚 | 初遇·十四行诗之吻 / 阳台·名字有什么关系 |
| Hamlet 哈姆雷特 | 莎士比亚 | 生存还是毁灭 / 我曾经爱过你 |
| Macbeth 麦克白 | 莎士比亚 | 我已经干了 / 明天，明天，再一个明天 |
| A Midsummer Night's Dream 仲夏夜之梦 | 莎士比亚 | 选角会·波顿什么都想演 / 迫克的收场白 |
| The Seagull 海鸥 | 契诃夫 | 你为什么总穿黑衣服 / 我是一个演员 |

每部剧都附带完整原文，点任意一段台词由 AI 解释。所有剧本均为公有领域。

## 它是怎么更新的

```
你跟 Claude 说「加一部剧」
   → Claude 修改本仓库 app/content/（剧本包 + 名场景 + 录音）并推送
   → GitHub Actions 自动：① 发布在线剧本库（GitHub Pages） ② 打包新的 APK
   → 手机上的 App 下次打开「剧本」就能看到新剧，不用重装
```

只有 App 界面本身改了（比如加新功能），才需要下载新 APK 覆盖安装，学习进度会保留。

## 第一次设置（只做一次）

1. 在 GitHub 新建一个 **public** 仓库，名字叫 `ghost-light`（在线剧本库需要公开仓库才能免费托管）。
2. 把本文件夹的所有内容推送到这个仓库的 `main` 分支（或者把 GitHub 连接给 Claude，让 Claude 推送）。
3. 打开仓库的 **Settings → Pages**，把 **Source** 设为 **GitHub Actions**。
4. 打开 **Actions** 页面，等「Build app and publish library」跑完（约 5–8 分钟）。

## 安装到安卓手机

1. 在手机浏览器打开仓库的 **Releases → latest**，下载 `ghost-light.apk`。
2. 安装时如果提示「未知来源」，允许浏览器安装应用即可。
3. 第一次录音时允许麦克风权限。App 里可以直接对着手机说台词打分。

## AI 功能

AI 讲解、AI 对手戏、整剧逐段解释需要你自己的 Anthropic API Key：在 App 右上角 ⚙ 里填写（只保存在手机上），在 console.anthropic.com 申请，按用量付费。没有 Key 时，录音、跟读打分、名场景学习、对读排练、词汇都能正常使用。

## 文件结构

```
app/ghost-light.html     App 界面（与 claude.ai 上的网页版相同）
app/app-shim.js          安卓版专用：API Key 设置、AI 调用
app/content/             剧本库：catalog.json + packs/*.json + 名场景录音
app/audio/               跟读页和词汇的录音
tools/                   生成剧本包的脚本（原文 → JSON，名场景 study.json，录音）
scripts/                 打包脚本（生成 www/，修改安卓工程）
signing/                 安卓签名（保证新 APK 能覆盖安装旧版）
```

### 加新剧本（给 Claude 的备忘）

1. 原文放进 `tools/sources/`，在 `tools/build_packs.py` 里加解析和元数据。
2. 名场景写进 `tools/study.json`（每句 en / modern / zh / note，每个角色配一个声音）。
3. 把剧目 id 加进 `tools/library.json` 的 `order`。
4. 运行 `python tools/build_packs.py && python tools/finalize.py && python tools/make_audio.py <模型目录>`，然后推送。

现代戏剧注意版权：只收录公有领域作品（如契诃夫、易卜生、王尔德的早期英译本），受版权保护的现代剧本不能放进公开的剧本库。
