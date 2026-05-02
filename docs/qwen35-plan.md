# 基于 Qwen3.5 的 MiniGeo 方案

## 模型选择

MiniGeo 默认使用 Qwen3.5-2B 作为主模型。

| 角色 | 模型 |
|---|---|
| 主模型 | Qwen3.5-2B |
| 轻量基线 | Qwen3.5-0.8B |
| 强基线 | Qwen3.5-4B |
| 教师模型 | Qwen3.5-27B 或 Qwen3.5-35B-A3B |
| Embedding | Qwen3-Embedding-0.6B |
| Reranker | Qwen3-Reranker-0.6B 或 bge-reranker |

## 为什么先用 Qwen3.5-2B

Qwen3.5-2B 适合作为第一阶段主模型：

- 能力强于 0.8B。
- 比 4B 或 9B 更容易运行。
- 更适合 Colab Pro。
- 支持 LoRA / QLoRA 微调。
- 有利于展示 RAG 和 Verifier 对可靠性的提升，而不是只依赖模型规模。

## 开发顺序

1. 已完成 MiniGeo-Bench、BM25 RAG baseline、模型 RAG 生成链路和本地 Verifier。
2. 已完成 Qwen3.5-4B 150 题模型服务结果、输出质量审计和 RAG + Verifier 离线后处理。
3. 下一步在 A100 上用最新 prompt / Verifier 链路重跑 Qwen3.5-4B smoke10、150 题和可选 300 题。
4. 启动真实 Qwen3-Embedding-0.6B 与 Qwen3-Reranker-0.6B，运行服务化检索消融。
5. 使用模型辅助 claim extraction 和 support classification 复判 Verifier 拦截样例。
6. 使用 LoRA / QLoRA 微调 Qwen3.5-2B。
7. 扩展 Agent 工具评测和最终 demo。

## LoRA / QLoRA 计划

第一轮微调配置：

| 设置 | 值 |
|---|---|
| Base model | Qwen3.5-2B |
| Method | QLoRA |
| Quantization | 4-bit |
| LoRA rank | 16 |
| Epochs | 1-3 |
| Data | 证据问答、拒答、SQL 格式样本 |

训练目标：

- 带引用回答。
- 证据不足时拒答。
- 遵循 JSON 输出 schema。
- 以受控格式生成 SQL。
- 减少无证据事实 claim。

## 评测假设

项目应验证以下假设：

1. Qwen3.5-2B + RAG 在引用问答上优于 Qwen3.5-2B。
2. MiniGeo-SFT 改善拒答和回答格式。
3. Verifier 降低 unsupported claim rate。
4. Qwen3.5-2B + RAG + Verifier 在可靠性指标上可接近或超过无 RAG 的 Qwen3.5-4B。
5. Agent 工作流在数据库支撑问题上优于纯 RAG。

## 主结果表

| 系统 | Acc | Citation Hit | Unsupported Claim | Abstention | SQL Exec | Latency |
|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5-0.8B | | | | | - | |
| Qwen3.5-2B | | | | | - | |
| Qwen3.5-2B + RAG | | | | | - | |
| MiniGeo-2B-SFT | | | | | - | |
| MiniGeo-2B-SFT + RAG | | | | | - | |
| MiniGeo-2B-SFT + RAG + Verifier | | | | | - | |
| Qwen3.5-4B + RAG | | 0.667 | | 0.767 | - | |
| Qwen3.5-4B + RAG + Verifier | | 0.667 | 0.017 | 0.767 | - | |
| MiniGeo-Agent | | | | | | |

## 简历表述

完成实现和评测后可使用：

> 构建 MiniGeo，一个基于 Qwen3.5 的地学可信问答与数据分析 Agent 系统；构建 MiniGeo-Bench，实现混合 RAG、引用验证、Qwen3.5-2B LoRA 微调，并评测答案准确率、引用命中率、幻觉率、拒答准确率和 SQL 执行准确率。
