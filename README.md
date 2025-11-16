## Hormone Cycle Companion（激素周期伴侣）

Hormone Cycle Companion 是一款基于 Flask 的轻量级应用，面向中文用户帮助观察生理周期。输入最近一次月经日期、平均周期长度等信息后，系统会估算当前周期日、所处阶段、激素相对水平，并给出针对女性本人或伴侣的沟通建议。

### 功能特点
- 简化的 28 天激素曲线模型，包含雌激素、孕激素、LH 与睾酮的相对趋势。
- 根据阶段切换的中文症状提示与关怀建议，可选择温和或俏皮语气。
- 响应式前端界面，表单提交后异步展示结果，适合手机端使用。
- 提供 JSON API，便于整合到其他工具或小程序中。

### 安装步骤
1. 克隆本仓库并进入目录。
2. （可选）创建 Python 3.9+ 虚拟环境。
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 运行应用
推荐使用自动化入口，一步完成虚拟环境创建、依赖安装与启动：
```bash
python run.py
```

如需手动运行：
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

### API 说明
`POST /api/evaluate`

请求 JSON 参数：
- `last_date` (string) – 上次月经开始日期，格式 `YYYY-MM-DD`
- `cycle_length` (int) – 平均周期长度（建议 20–40）
- `menses_days` (int) – 经期持续天数（建议 1–10）
- `target_date` (string) – 想要观察/预测的日期（`YYYY-MM-DD`，留空则默认当天）
- `role` (string) – `self` / `partner` / `other`，用于确定建议视角
- `tone` (string) – `gentle` 或 `playful`，调整文案风格

响应 JSON：
```json
{
  "cycle_day": 12,
  "cycle_length": 28,
  "phase": "卵泡期",
  "phase_key": "follicular",
  "hormones": {"estrogen": 62, "progesterone": 18, "LH": 11, "testosterone": 22},
  "symptoms": ["体力恢复", "专注度提升", "心情平稳", "对新事物好奇"],
  "advice": {"headline": "...", "items": ["..."]},
  "observed_date": "2024-06-01"
}
```
若参数缺失或格式错误，会返回 `{"error": "...错误信息..."}`，HTTP 状态码 400。

### 截图占位
请在此处添加界面截图，例如 `docs/screenshot.png`。

### 许可证
本项目以 MIT License 发布，详见 [LICENSE](LICENSE)。
