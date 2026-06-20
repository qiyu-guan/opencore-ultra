```markdown
# 🚀 OpenCore Ultra v5.0

> **AIBox · qiyu** 作品  
> *让每个人都能安全、专业地维护自己的 Android 设备*

---

## 📖 产品概述

OpenCore Ultra v5.0 是一个专业级 Android 设备维护工具，集成了 **50+ 项核心功能**，覆盖从小白救砖到极客调校的完整场景。无论是刷机、备份、Root 还是救砖，都能一站式完成。

**一句话定位**：让每个人都能安全、专业地维护自己的 Android 设备。

---

## 🎯 核心功能体系

### 一、设备与连接管理

| 功能 | 说明 |
|------|------|
| 智能设备检测 | 自动识别 ADB / Fastboot / EDL 三种模式 |
| 多设备支持 | 同时管理多台 Android 设备 |
| 驱动管理 | 一键安装 ADB/Fastboot/USB 驱动 |
| 设备信息读取 | 型号、序列号、Bootloader 锁状态、分区表 |

### 二、备份与恢复

| 功能 | 说明 |
|------|------|
| 字库级备份 | 整颗 eMMC/UFS 闪存完整备份（救砖必备） |
| 分区备份 | 选择性备份 boot/system/vendor/data 等分区 |
| 应用备份 | 无需 Root，备份已安装的应用 + 数据 |
| 个人数据备份 | 联系人、短信、通话记录、WiFi 配置 |
| 压缩加密 | 备份文件自动压缩（tar.gz），支持加密 |

### 三、多模式刷写引擎

| 模式 | 说明 |
|------|------|
| Fastboot 线刷 | 支持 flash-all 脚本，全自动刷机 |
| EDL 9008 深度刷写 | 高通芯片救砖专用，硬砖也能救 |
| Recovery 卡刷 | 自动推送刷机包并进入 Recovery |
| MTK SP Flash 兼容 | 支持联发科芯片 Scatter 文件刷写 |
| 三星 Odin 兼容 | 支持 BL/AP/CP/CSC 分区刷写 |
| 单分区刷写 | 任意刷写 boot/recovery/logo/modem 等分区 |

### 四、Root 与系统修改

| 功能 | 说明 |
|------|------|
| Magisk Boot 修补 | 一键修补 boot.img，获取 Root |
| Magisk 模块管理 | 在线浏览、下载、安装 Magisk 模块 |
| LSPosed 支持 | 安装和管理 Xposed 模块 |
| 系统挂载读写 | 挂载 system/vendor 分区为可读写 |
| build.prop 编辑器 | 可视化修改系统属性 |
| SELinux 切换 | 一键切换 enforcing/permissive |

### 五、救砖与安全擦除

| 功能 | 说明 |
|------|------|
| EDL 深度救砖 | 高通 9008 模式全自动救砖流程 |
| FRP 锁清除 | 谷歌账户验证辅助清除（需合法授权） |
| 安全擦除 | 符合 DoD 标准的多重覆写擦除 |
| 引导加载程序管理 | 解锁/回锁 Bootloader 向导 |
| 防回滚保护警告 | ARB（Anti-Rollback）风险提示 |

### 六、定制与美化

| 功能 | 说明 |
|------|------|
| OpenGApps 刷入 | 一键刷入谷歌服务框架 |
| 开机动画更换 | 自定义开机动画和 Logo |
| 字体/Emoji 替换 | 一键更换系统字体 |
| 去广告 Hosts | 自动更新去广告规则 |
| DPI/分辨率调整 | 可视化调整屏幕密度和分辨率 |

---

## 💻 双界面设计

### 命令行界面 (CLI)

```

主菜单:

1. 检测设备
2. 备份分区
3. 字库备份/恢复
4. 刷机 (Fastboot)
5. 救砖模式 (EDL)
6. 固件管理
7. Root/系统修改
8. 安全擦除
9. 切换至图形界面 (GUI)
10. 退出

```

- **优点**：轻量、快速、可在 Termux 中运行
- **适合**：Termux 用户、极客、远程操作

### 图形界面 (GUI)

- 基于 Tkinter 构建
- 鼠标点击操作，直观易用
- 适合：Windows 电脑用户、刷机新手

### 一键切换

- CLI 中输入 `9` → 启动 GUI
- GUI 中点击「切换至命令行」→ 回到 CLI

---

## 🛠️ 技术架构

### 模块化设计

```

opencore-ultra/
├── core/           # 核心功能模块
│   ├── device.py   # 设备检测与管理
│   ├── backup.py   # 备份与恢复
│   ├── flash.py    # 刷写引擎
│   ├── firmware.py # 固件下载与校验
│   ├── root.py     # Root 与模块管理
│   ├── system.py   # 系统修改
│   └── rescue.py   # 救砖与安全擦除
├── ui/
│   ├── cli.py      # 命令行界面
│   └── gui.py      # 图形界面
└── tools/          # ADB/Fastboot/EDL 工具

```

### 跨平台支持

| 平台 | 运行方式 |
|------|----------|
| Windows | 直接运行 EXE 文件 |
| Linux (x86_64) | 运行 ELF 可执行文件 |
| macOS | 运行 Mach-O 可执行文件 |
| Termux (Android) | 运行 Python 源码 |

---

## 🎯 目标用户

| 用户类型 | 使用场景 |
|----------|----------|
| 刷机小白 | 图形界面 + 一键操作，安全刷机 |
| 数码极客 | 命令行 + 高级功能，深度定制 |
| 维修工程师 | EDL 救砖 + 字库备份，专业修复 |
| Termux 用户 | 在手机上直接维护 Android 设备 |

---

## 🔒 安全特性

1. **刷机前确认**：显示分区大小、镜像大小，输入 `yes` 确认
2. **备份优先**：建议先备份再刷机，防止数据丢失
3. **防回滚警告**：识别 ARB 风险并提示
4. **错误恢复**：操作失败时提供明确的错误信息和解决建议
5. **日志记录**：所有操作记录到 `opencore_ultra.log`

---

## 📦 获取方式

### GitHub 仓库

```bash
git clone https://github.com/qiyu-guan/opencore-ultra.git
```

直接下载 EXE

访问 GitHub Releases 页面，下载对应平台的预编译版本。

Termux 运行

```bash
pkg install python git
git clone https://github.com/qiyu-guan/opencore-ultra.git
cd opencore-ultra
pip install requests
python opencore_tool.py
```

---

📈 版本对比

功能 普通刷机工具 OpenCore Ultra v5.0
分区备份 ❌ ✅
字库级备份 ❌ ✅
EDL 救砖 ❌ ✅
Magisk 修补 ❌ ✅
双界面 ❌ ✅
跨平台 ❌ ✅
50+ 功能 ❌ ✅
开源免费 ❌ ✅

---

🏆 为什么选择 OpenCore Ultra？

1. 功能最全：覆盖从刷机到救砖的完整场景
2. 小白可用：图形界面 + 详细提示，新手也能上手
3. 极客必备：命令行 + 高级功能，满足深度定制
4. 跨平台：Windows/Linux/macOS/Termux 全覆盖
5. 开源免费：MIT 协议，可自由使用和修改
6. 持续更新：GitHub 活跃维护，功能不断扩展

---

📜 许可证

MIT License

---

🙏 致谢

· AIBox · 称号
· qiyu · 作者
· Built with Python ❤️
· Open source community

---

OpenCore Ultra v5.0 – 让每个人都能专业地维护自己的 Android 设备！

```
