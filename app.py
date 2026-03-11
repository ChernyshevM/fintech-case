# ============================================================================
# app.py — Интерактивный дашборд: Анализ оттока клиентов банка
# ============================================================================
# Запуск: streamlit run app.py

# 1️⃣ ИМПОРТ БИБЛИОТЕК
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import streamlit as st
import warnings

warnings.filterwarnings("ignore")

# Настройка страницы (должна быть первой командой streamlit)
st.set_page_config(
    page_title="🏦 Анализ оттока клиентов",
    page_icon="📊",
    layout="wide",  # Широкий макет для дашборда
)


# 2️⃣ ЗАГРУЗКА ДАННЫХ (кэшируем, чтобы не грузить каждый раз)
@st.cache_data
def load_data():
    """Загружает и предварительно обрабатывает данные"""
    data_path = Path(
        r"C:\Users\User\Documents\MyPetProjects\fintech-case\data\processed\customers_clean.csv"
    )
    df = pd.read_csv(data_path)

    # Добавляем полезные признаки для фильтрации
    df["age_group"] = pd.cut(
        df["age"], bins=[18, 30, 45, 60, 100], labels=["18-30", "31-45", "46-60", "60+"]
    )
    df["balance_group"] = pd.cut(
        df["balance"],
        bins=[-1, df["balance"].median(), df["balance"].max()],
        labels=["Низкий", "Высокий"],
    )
    return df


# Загружаем данные
df = load_data()

# 3️⃣ БОКОВАЯ ПАНЕЛЬ: ФИЛЬТРЫ
st.sidebar.header("🔍 Фильтры")

# Фильтр по возрастной группе
age_filter = st.sidebar.multiselect(
    "Возрастная группа:",
    options=df["age_group"].cat.categories.tolist(),
    default=df["age_group"].cat.categories.tolist(),
)

# Фильтр по активности
activity_filter = st.sidebar.multiselect(
    "Активность:",
    options=[0, 1],
    default=[0, 1],
    format_func=lambda x: "Неактивен" if x == 0 else "Активен",
)

# Фильтр по количеству продуктов
products_filter = st.sidebar.multiselect(
    "Количество продуктов:",
    options=sorted(df["products_number"].unique()),
    default=sorted(df["products_number"].unique()),
)

# Применяем фильтры к данным
filtered_df = df[
    (df["age_group"].isin(age_filter))
    & (df["active_member"].isin(activity_filter))
    & (df["products_number"].isin(products_filter))
]

# Останавливаем выполнение, если данных нет после фильтрации
if filtered_df.empty:
    st.warning("⚠️ Нет данных для отображения с выбранными фильтрами")
    st.stop()

# 4️⃣ ЗАГОЛОВОК И КЛЮЧЕВЫЕ МЕТРИКИ
st.title("🏦 Дашборд: Анализ оттока клиентов банка")
st.markdown("Интерактивная визуализация ключевых инсайтов по оттоку клиентов")

# Расчёт метрик для отображения
total_clients = len(filtered_df)
churned_clients = filtered_df["churn"].sum()
churn_rate = churned_clients / total_clients * 100

# Отображение метрик в 3 колонки
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Всего клиентов", f"{total_clients:,}")
with col2:
    st.metric("Ушло клиентов", f"{int(churned_clients):,}")
with col3:
    st.metric(
        "Churn Rate",
        f"{churn_rate:.1f}%",
        delta=f"{churn_rate - df['churn'].mean()*100:+.1f}%",
        delta_color="inverse",
    )  # Красный если выше среднего

st.divider()

# 5️⃣ ВКЛАДКИ ДЛЯ РАЗНЫХ РАЗДЕЛОВ АНАЛИЗА
tab1, tab2, tab3 = st.tabs(["📊 Обзор", "👤 Возраст", "📦 Продукты"])

# ▼▼▼ ВКЛАДКА 1: ОБЗОР ▼▼▼
with tab1:
    st.subheader("📈 Распределение оттока")

    # График 1: Pie chart оттока
    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            names=["Остался", "Ушёл"],
            values=[
                (1 - filtered_df["churn"].mean()) * 100,
                filtered_df["churn"].mean() * 100,
            ],
            color=["Остался", "Ушёл"],
            color_discrete_map={"Остался": "#2ecc71", "Ушёл": "#e74c3c"},
            hole=0.4,
        )
        fig_pie.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig_pie, width="stretch")

    with col2:
        churn_by_activity = filtered_df.groupby("active_member")["churn"].mean() * 100

        # Динамические метки для оси X на основе отфильтрованных данных
        x_labels = churn_by_activity.index.map({0: "Неактивен", 1: "Активен"})
        color_map = {0: "#e74c3c", 1: "#2ecc71"}

        fig_bar = px.bar(
            x=x_labels,  # ✅ Динамические подписи вместо статического списка
            y=churn_by_activity.values,
            labels={"x": "Статус", "y": "Churn Rate, %"},
            color=churn_by_activity.index.map(color_map),
        )
        fig_bar.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig_bar.update_layout(showlegend=False, height=300, xaxis_title="")
        st.plotly_chart(fig_bar, width="stretch")

    # График 3: Тепловая карта взаимодействия возраст × активность
    st.subheader("🔥 Взаимодействие: Возраст × Активность")

    # Проверка: если данных нет после фильтрации — показываем сообщение
    if (
        not filtered_df.empty
        and len(filtered_df["active_member"].unique()) > 0
        and len(filtered_df["age_group"].dropna().unique()) > 0
    ):
        pivot = (
            pd.pivot_table(
                filtered_df,
                values="churn",
                index="active_member",
                columns="age_group",
                aggfunc="mean",
            )
            * 100
        )

        y_labels = pivot.index.map({0: "Неактивен", 1: "Активен"})

        fig_heatmap = px.imshow(
            pivot,
            labels=dict(x="Возрастная группа", y="Активность", color="Churn Rate, %"),
            x=pivot.columns.astype(str),
            y=y_labels,  # ✅ Используем динамические метки
            color_continuous_scale="YlOrRd",
            text_auto=".1f",
        )
        fig_heatmap.update_layout(height=300)
        st.plotly_chart(fig_heatmap, width="stretch")
    else:
        st.warning("⚠️ Нет данных для отображения тепловой карты с выбранными фильтрами")

# ▼▼▼ ВКЛАДКА 2: ВОЗРАСТ ▼▼▼
with tab2:
    st.subheader("👤 Анализ оттока по возрасту")

    # График 1: Распределение возраста с KDE
    fig_age_dist = px.histogram(
        filtered_df,
        x="age",
        color="churn",
        barmode="overlay",
        nbins=30,
        histnorm="probability density",
        color_discrete_map={0: "#2ecc71", 1: "#e74c3c"},
        opacity=0.5,
    )
    # Добавляем линии средних значений
    mean_stayed = filtered_df[filtered_df["churn"] == 0]["age"].mean()
    mean_churned = filtered_df[filtered_df["churn"] == 1]["age"].mean()
    fig_age_dist.add_vline(
        x=mean_stayed,
        line_dash="dash",
        line_color="#2ecc71",
        annotation_text=f"Остался: {mean_stayed:.1f}",
    )
    fig_age_dist.add_vline(
        x=mean_churned,
        line_dash="dash",
        line_color="#e74c3c",
        annotation_text=f"Ушёл: {mean_churned:.1f}",
    )
    fig_age_dist.update_layout(bargap=0.1, height=400)
    st.plotly_chart(fig_age_dist, width="stretch")

    # График 2: Churn Rate по возрастным группам
    st.subheader("📊 Churn Rate по возрастным группам")
    churn_by_age = filtered_df.groupby("age_group", observed=True)["churn"].mean() * 100

    fig_age_bar = px.bar(
        x=churn_by_age.index.astype(str),
        y=churn_by_age.values,
        labels={"x": "Возрастная группа", "y": "Churn Rate, %"},
        color=churn_by_age.values,
        color_continuous_scale="RdYlGn_r",  # Красный = высокий риск
    )
    fig_age_bar.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    fig_age_bar.update_layout(showlegend=False, height=350, xaxis_title="")
    st.plotly_chart(fig_age_bar, width="stretch")

    # Ключевой инсайт
    st.info(
        "🎯 **Инсайт**: Клиенты 46–60 лет имеют максимальный отток (51%). Особенно высок риск у неактивных клиентов этого возраста (69.7%)."
    )

# ▼▼▼ ВКЛАДКА 3: ПРОДУКТЫ ▼▼▼
with tab3:
    st.subheader("📦 Отток по количеству продуктов")

    # Подготовка данных
    churn_by_products = filtered_df.groupby("products_number")["churn"].agg(
        ["mean", "count"]
    )
    churn_by_products["churn_rate_%"] = churn_by_products["mean"] * 100

    # График: столбцы с размером выборки
    fig_products = go.Figure()

    fig_products.add_trace(
        go.Bar(
            x=churn_by_products.index.astype(str),
            y=churn_by_products["churn_rate_%"],
            text=[
                f"{row['churn_rate_%']:.1f}%<br>n={int(row['count'])}"
                for _, row in churn_by_products.iterrows()
            ],
            textposition="outside",
            marker_color=["#3498db", "#2ecc71", "#e74c3c", "#9b59b6"][
                : len(churn_by_products)
            ],
            hovertemplate="<b>%{x} продукт(ов)</b><br>Churn: %{y:.1f}%<br>Клиентов: %{text}<extra></extra>",
        )
    )

    fig_products.update_layout(
        xaxis_title="Количество продуктов",
        yaxis_title="Churn Rate, %",
        height=400,
        hovermode="x unified",
    )
    st.plotly_chart(fig_products, width="stretch")

    # Инсайт
    st.warning(
        "⚠️ **Внимание**: Группы 3+ продукта малочисленны (266 и 60 клиентов). Высокий churn может быть статистическим шумом."
    )

# 6️⃣ РАЗДЕЛ: БИЗНЕС-РЕКОМЕНДАЦИИ
st.divider()
st.subheader("🎯 Приоритетные рекомендации для бизнеса")

rec1, rec2, rec3 = st.columns(3)

with rec1:
    st.markdown("### 🔴 Приоритет 1")
    st.markdown("**Сегмент: 46–60 лет + неактивен**")
    st.markdown("- Триггер: 30 дней неактивности → персонализированный контакт")
    st.markdown("- Канал: телефон / email")

with rec2:
    st.markdown("### 🟡 Приоритет 2")
    st.markdown("**Онбординг для 45+**")
    st.markdown("- Упрощённый интерфейс")
    st.markdown("- Видео-гайд «Первые 5 минут»")

with rec3:
    st.markdown("### 🟢 Приоритет 3")
    st.markdown("**Удержание активности**")
    st.markdown("- Персонализированные уведомления о кэшбэке")
    st.markdown("- Простые цели: «1 оплата = бонус»")
    st.markdown("- Метрика: % активных клиентов 45+")

# 7️⃣ ФУТЕР: ЭКСПОРТ И ССЫЛКИ
st.divider()
col_export, col_info = st.columns([1, 2])

with col_export:
    # Кнопка экспорта отфильтрованных данных
    csv = filtered_df.to_csv(index=False, encoding="utf-8")
    st.download_button(
        label="📥 Скачать отфильтрованные данные (CSV)",
        data=csv,
        file_name="filtered_churn_data.csv",
        mime="text/csv",
    )

with col_info:
    st.markdown(
        """
    **📋 О проекте**  
    Пет-проект по анализу оттока клиентов финтех-сервиса.  
    🔗 [GitHub репозиторий](#) | 📧 [Связаться со мной](https://t.me/chernyshevm)  
    *Создано с ❤️ для портфолио аналитика данных*
    """
    )
