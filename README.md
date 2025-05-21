# English Learning App (英文跟读评分应用)

本项目是一个英文跟读评分应用，旨在帮助用户提高英语口语水平。

## 项目结构

```
english_learning_app/
├── backend/            # 后端 Flask 应用
│   ├── app/            # 应用核心代码
│   │   ├── __init__.py # 应用工厂
│   │   ├── config.py   # 配置文件
│   │   ├── models/     # SQLAlchemy 模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── word.py
│   │   │   └── recording.py
│   │   ├── routes/     # API 路由蓝本
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── words.py
│   │   │   └── records.py
│   │   └── services/   # 业务逻辑服务
│   │       ├── __init__.py
│   │       └── speech_evaluation_service.py # 语音评测服务
│   ├── run.py          # 应用启动脚本
│   └── requirements.txt # Python 依赖
├── frontend/           # 前端 Vue 应用 (使用 ElementPlus)
└── README.md           # 本文件
```

## 技术栈

*   **后端:** Python, Flask, SQLAlchemy
*   **前端:** Vue.js, ElementPlus
*   **数据库:** (待定, 例如 SQLite, PostgreSQL)
*   **语音识别/评分:** (待定, 可能使用第三方 API 或库)

## TODO

- [ ] 完成后端 API 接口实现
- [ ] 完成前端页面和组件开发
- [ ] 集成语音识别和评分功能
- [ ] 完善用户认证和授权
- [ ] 编写单元测试和集成测试

## 前端项目初始化 (Vue + ElementPlus)

请在 `frontend` 目录下执行以下命令初始化 Vue 项目：

```bash
# 确保已安装 Node.js 和 npm/yarn
cd english_learning_app/frontend

# 使用 Vite 创建 Vue 项目 (推荐)
npm create vite@latest . -- --template vue-ts
# 或者 yarn create vite . --template vue-ts

# 安装依赖
npm install
# 或者 yarn install

# 安装 ElementPlus
npm install element-plus
# 或者 yarn add element-plus

# (可选) 按需导入 ElementPlus 组件以减小打包体积，请参考 ElementPlus 官方文档
```

## 后端项目初始化与运行

```bash
cd english_learning_app/backend

# 创建并激活虚拟环境 (推荐)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# 安装依赖
pip install -r requirements.txt

# (如果使用数据库迁移，例如 Flask-Migrate)
# flask db init
# flask db migrate -m "Initial migration."
# flask db upgrade

# 运行应用
python run.py
```