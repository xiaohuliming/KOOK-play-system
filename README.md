<div align="center">

![banner](https://capsule-render.vercel.app/api?type=waving&color=0:11998e,100:38ef7d&height=170&section=header&text=Peiwan%20Admin&fontSize=46&fontColor=ffffff)

# 🎮 陪玩 / 电竞工作室 后台管理系统

**Web 管理端 + KOOK 群机器人深度打通** · 派单、结算、钱包、会员、播报、数据统计 全流程一体化

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![KOOK](https://img.shields.io/badge/KOOK-Bot-53B9F3?style=flat-square)
![Responsive](https://img.shields.io/badge/响应式-移动端适配-38ef7d?style=flat-square)
![WeChat](https://img.shields.io/badge/微信-ToDoHaCambiado-07C160?style=flat-square&logo=wechat&logoColor=white)

> 🔒 **源码不公开，本仓库仅作效果展示** · 承接 **部署 / 二次开发 / 定制开发**

</div>

---

## ✨ 功能亮点

<table>
<tr>
<td width="50%" valign="top">

**🎯 派单与订单**
- 常规陪玩 / 护航 / 代练 分区派单
- 申报 → 确认 → 结算 → 退款 全流程
- 订单冻结 / 解冻，超时自动确认

**💰 钱包与财务**
- 充值、赠金、消费、提现审核
- 多币种余额与冻结额实时对账
- 收支明细一键导出 Excel

**👑 会员体系（VIP）**
- 按经验值自动升级，等级折扣自动生效
- 升级播报 + 专属权益

</td>
<td width="50%" valign="top">

**🤖 群机器人集成**
- `/钱包` `/结单` `/提现` `/游戏` 等指令
- 充值 / 礼物 / 升级 / 订单 自动私信 + 频道播报

**🎁 礼物 & 运营工具**
- 送礼下单、冠名播报、礼物图缓存
- 抽奖（普通 / 互动）、打卡、聊天与挂机统计
- 身份标签、权限分级、操作日志

**🎨 体验**
- 多主题一键换肤 + 暗色模式
- 全站响应式，移动端适配

</td>
</tr>
</table>

## 🧩 系统架构

```mermaid
flowchart LR
    Boss[👤 老板] --> Web
    Player[🎮 陪玩] --> Web
    Staff[🎧 客服] --> Web[Web 管理端]
    KOOK[💬 KOOK 群] <--> Bot[🤖 KOOK 机器人]
    Web -->|下单 / 结算 / 钱包| DB[(🗄 MySQL)]
    Bot --> DB
    Sched[⏰ 定时任务] --> DB
    Web -. 充值·礼物·升级 播报 / 私信 .-> Bot
```

> 三进程分离部署（Web / 定时任务 / 机器人），自动化部署 + 数据库迁移管理，稳定可扩展。

## 🎬 效果演示

> 录一段「派单 → 结算 → 到账」的操作 GIF 放这里最直观（脱敏后）。

![演示](screenshots/demo.gif)

### 界面截图

| 派单大厅 | 订单结算 |
| :---: | :---: |
| ![派单](screenshots/dispatch.png) | ![订单](screenshots/orders.png) |

| 钱包 / 提现 | 会员等级 |
| :---: | :---: |
| ![钱包](screenshots/wallet.png) | ![VIP](screenshots/vip.png) |

| 数据统计 | 机器人播报 |
| :---: | :---: |
| ![统计](screenshots/stats.png) | ![播报](screenshots/broadcast.png) |

## 🤝 承接服务

| 服务 | 说明 |
| :--- | :--- |
| 🚀 **部署上线** | 从零把系统跑起来：服务器环境、数据库、机器人、自动部署一条龙 |
| 🔧 **二次开发** | 在现有系统上加功能、改逻辑、对接你的业务玩法 |
| 🎨 **定制开发** | 按你的需求从零定制陪玩 / 电竞 / 社群运营后台 |
| 🛠 **长期维护** | 按需维护、答疑、迭代升级 |

## 📮 联系方式

<div align="center">

### 加微信详谈 · 备注「后台系统」

# 🟢 ToDoHaCambiado

![WeChat](https://img.shields.io/badge/微信-ToDoHaCambiado-07C160?style=for-the-badge&logo=wechat&logoColor=white)

> 报价与周期视需求而定，欢迎带着你的想法来聊。

![footer](https://capsule-render.vercel.app/api?type=waving&color=0:38ef7d,100:11998e&height=90&section=footer)

</div>
