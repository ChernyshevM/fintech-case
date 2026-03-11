# setup_project.py
import os
from pathlib import Path

# Базовая директория проекта
BASE_DIR = Path(r"C:\Users\User\Documents\MyPetProjects\fintech-case")

# Структура папок
folders = [
    "data/raw",
    "data/processed",
    "notebooks",
    "src",
    "docs/screenshots",
    "models",
    "tests",
]

# Структура файлов (пустые файлы-заглушки)
files = [
    "src/__init__.py",
    "src/data_loader.py",
    "src/metrics.py",
    "src/utils.py",
    "notebooks/.gitkeep",
    "docs/.gitkeep",
    "requirements.txt",
    "README.md",
    ".gitignore",
]


def create_project_structure():
    """Создаёт структуру папок и файлов проекта"""

    # Создаём папки
    for folder in folders:
        path = BASE_DIR / folder
        path.mkdir(parents=True, exist_ok=True)
        print(f"✅ Создана папка: {path}")

    # Создаём файлы
    for file in files:
        path = BASE_DIR / file
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        print(f"✅ Создан файл: {path}")

    # Заполняем requirements.txt
    requirements_content = """pandas==2.0.3
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
plotly==5.15.0
scipy==1.11.1
streamlit==1.25.0
jupyter==1.0.0
"""
    with open(BASE_DIR / "requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)

    # Заполняем .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# Jupyter
.ipynb_checkpoints/

# Data
data/raw/*.csv
data/processed/*.csv
!data/raw/.gitkeep
!data/processed/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/
"""
    with open(BASE_DIR / ".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)

    # Заполняем README.md
    readme_content = """# 🏦 Анализ оттока клиентов банка (Bank Customer Churn)

## 📌 Описание проекта
End-to-end аналитический проект по выявлению факторов оттока клиентов банка.
Включает расчёт метрик (Churn, LTV, Retention), проверку гипотез и интерактивный дашборд.

## 🎯 Цель
Выявить ключевые факторы оттока и сформулировать рекомендации для бизнеса.

## 📁 Структура проекта
# fintech-case/
├── data/
│ ├── raw/ # Исходные данные
│ └── processed/ # Очищенные данные
├── notebooks/
│ ├── 01_eda.ipynb # Первичный анализ
│ ├── 02_metrics.ipynb # Метрики и гипотезы
│ └── 03_dashboard.ipynb# Подготовка дашборда
├── src/
│ ├── data_loader.py # Загрузка данных
│ ├── metrics.py # Функции метрик
│ └── utils.py # Утилиты
├── app.py # Streamlit дашборд
├── requirements.txt
└── README.md

# """
    with open(BASE_DIR / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)


if __name__ == "__main__":
    create_project_structure()
