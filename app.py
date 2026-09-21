# app.py
import streamlit as st
import requests
import pandas as pd

# ----------------------------------------------------------------------------
# 1. НАСТРОЙКА СТРАНИЦЫ
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Брусника — проверка контрагента",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ----------------------------------------------------------------------------
# 2. API КЛЮЧ (определяем сразу, чтобы был доступен везде ниже)
# ----------------------------------------------------------------------------
api_key = st.secrets.get("FOCUS_API_KEY", "")
if not api_key:
    st.warning("⚠️ API ключ Контур.Фокуса не настроен. Добавьте `FOCUS_API_KEY` в secrets приложения.")

# ЦВЕТА
BG_COLOR = "#f8f7f4"
WHITE = "#ffffff"
DARK = "#1e1e1e"
GRAY = "#6b6b6b"
LIGHT_GRAY = "#f0eeea"
BORDER_COLOR = "rgba(0, 0, 0, 0.05)"
GOLD = "#b89b7b"
GREEN = "#1d6b2e"
RED = "#b33a3a"
ORANGE = "#b8681a"
BLUE = "#1e5a8a"

# CSS
st.markdown(f"""
<style>
    .stApp {{ background-color: {BG_COLOR}; font-family: 'Inter', sans-serif; }}
    .main > div {{ padding: 0; max-width: 900px; margin: 0 auto; }}
    #MainMenu, footer, .stDeployButton, header {{ visibility: hidden; }}

    .header {{
        background: {WHITE}; padding: 20px 24px 12px;
        border-bottom: 1px solid {BORDER_COLOR};
        display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
    }}
    .logo {{ display: flex; align-items: center; gap: 10px; color: {DARK}; }}
    .logo-icon {{ width: 36px; height: 36px; background: {DARK}; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: {WHITE}; font-weight: 700; font-size: 18px; }}
    .logo-text {{ font-weight: 600; font-size: 22px; letter-spacing: -0.3px; }}
    .logo-text span {{ font-weight: 300; color: {GRAY}; }}
    .header-tag {{ font-size: 14px; color: {GRAY}; background: {LIGHT_GRAY}; padding: 6px 16px; border-radius: 40px; }}

    .hero {{ padding: 48px 24px 32px; }}
    .hero h1 {{ font-size: 36px; font-weight: 400; letter-spacing: -0.4px; margin-bottom: 8px; line-height: 1.2; color: {DARK}; }}
    .hero h1 strong {{ font-weight: 600; }}
    .hero .sub {{ font-size: 18px; color: #4a4a4a; margin-bottom: 32px; }}

    .search-card {{
        background: {WHITE}; border-radius: 24px; padding: 36px 40px;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.04); border: 1px solid {BORDER_COLOR};
        margin-bottom: 24px;
    }}

    .participant-block {{
        background: {LIGHT_GRAY}; border-radius: 16px; padding: 18px 22px; margin-bottom: 14px;
        border-left: 4px solid {GOLD};
    }}
    .participant-title {{ font-weight: 600; font-size: 16px; color: {DARK}; margin-bottom: 10px; }}

    .stTextInput > div > div > input {{
        border-radius: 10px; border: 1px solid #dcdcdc; padding: 10px 16px; font-size: 15px;
    }}
    .stNumberInput > div > div > input {{
        border-radius: 10px; border: 1px solid #dcdcdc; padding: 10px 16px; font-size: 15px;
    }}
    .stButton > button {{
        border-radius: 10px !important; font-weight: 500 !important;
        font-size: 15px !important; border: none !important; height: 46px;
    }}
    .stButton > button[kind="primary"] {{
        background: {DARK} !important; color: {WHITE} !important;
    }}
    .stButton > button[kind="primary"]:hover {{ background: #333 !important; }}
    .stButton > button[kind="secondary"] {{
        background: {WHITE} !important; color: {DARK} !important;
        border: 1px solid #dcdcdc !important;
    }}
    .stButton > button[kind="secondary"]:hover {{ background: {LIGHT_GRAY} !important; }}

    .results-card {{
        background: {WHITE}; border-radius: 24px; padding: 32px 36px;
        border: 1px solid {BORDER_COLOR}; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
    }}
    .winner-card {{ border-left: 6px solid {GREEN}; }}
    .reserve-card {{ border-left: 6px solid {BLUE}; }}
    .other-card {{ border-left: 6px solid {GRAY}; opacity: 0.95; }}

    .company-name {{ font-size: 22px; font-weight: 600; color: {DARK}; }}
    .company-inn {{ font-size: 15px; color: {GRAY}; margin-top: 2px; }}

    .result-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 14px 28px; margin-top: 18px;
    }}
    .result-item {{ border-bottom: 1px solid {LIGHT_GRAY}; padding-bottom: 8px; }}
    .result-item .label {{ font-size: 11px; color: {GRAY}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; }}
    .result-item .value {{ font-size: 17px; font-weight: 500; color: {DARK}; }}

    .score-badge {{
        display: inline-block; padding: 4px 14px; border-radius: 20px;
        font-size: 14px; font-weight: 600; background: #e6f0e6; color: {GREEN};
    }}
    .score-badge.reserve {{ background: #e0ecf5; color: {BLUE}; }}
    .score-badge.other {{ background: {LIGHT_GRAY}; color: {GRAY}; }}

    .footer {{
        margin-top: 40px; padding: 24px; border-top: 1px solid {BORDER_COLOR};
        background: {WHITE}; text-align: center; font-size: 14px; color: {GRAY};
    }}

    @media (max-width: 640px) {{
        .result-grid {{ grid-template-columns: 1fr; }}
        .search-card {{ padding: 24px 20px; }}
        .results-card {{ padding: 24px 20px; }}
    }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 3. ШАПКА И ЗАГОЛОВОК
# ----------------------------------------------------------------------------
st.markdown("""
<div class="header">
    <div class="logo">
        <div class="logo-icon">Б</div>
        <div class="logo-text">Брусника <span>· проверка</span></div>
    </div>
    <span class="header-tag">Сравнение участников тендера</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>Сравнение <strong>участников тендера</strong></h1>
    <p class="sub">Оценка надежности и ценовых предложений по данным ФНС и Контур.Фокуса</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 4. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ
# ----------------------------------------------------------------------------
if 'participants' not in st.session_state:
    st.session_state.participants = [
        {"inn": "", "price": 0.0},
        {"inn": "", "price": 0.0},
    ]

if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

if 'run_analysis' not in st.session_state:
    st.session_state.run_analysis = False

# ----------------------------------------------------------------------------
# 5. ФУНКЦИИ РАБОТЫ С API
# ----------------------------------------------------------------------------
def fetch_kontur_data(inn, api_key):
    """Собирает данные из всех необходимых методов Контур.Фокуса."""
    result = {
        'inn': inn, 'name': 'Неизвестно', 'revenue': 0, 'employees': 0,
        'yellow_statements': 0, 'red_statements': 0, 'risk_text': [],
        'scoring_score': 0, 'max_debt': 0, 'cred_day': 0, 'equity': 0, 'status': 'OK'
    }

    if not api_key:
        result['status'] = 'No API Key'
        return result

    try:
        # 1. /api3/req — Название
        r = requests.get("https://focus-api.kontur.ru/api3/req",
                         params={"key": api_key, "inn": inn}, timeout=15)
        if r.status_code == 200 and r.json():
            req = r.json()[0]
            result['name'] = req.get('UL', {}).get('legalName', {}).get('short', 'Неизвестно')

        # 2. /api3/accountingReports — Выручка
        r = requests.get("https://focus-api.kontur.ru/api3/accountingReports",
                         params={"key": api_key, "inn": inn}, timeout=15)
        buh_forms = []
        if r.status_code == 200 and r.json():
            data = r.json()
            if data and len(data) > 0:
                buh_forms = data[0].get('buhForms', [])
                years = sorted([f.get('year') for f in buh_forms if f.get('year')], reverse=True)
                if years:
                    latest = next((f for f in buh_forms if f.get('year') == years[0]), None)
                    if latest:
                        for item in latest.get('form2', []):
                            if item.get('code') == 2110:
                                result['revenue'] = item.get('endValue', 0)
                                break

        # 3. /api3/legalAnalytics — Штат
        r = requests.get("https://focus-api.kontur.ru/api3/legalAnalytics",
                         params={"key": api_key, "inn": inn}, timeout=15)
        if r.status_code == 200 and r.json():
            data = r.json()
            if data and len(data) > 0:
                analytics = data[0]
                emp = analytics.get('employees', [])
                if emp:
                    result['employees'] = emp[-1].get('count', 0) if isinstance(emp, list) else emp.get('count', 0)

        # 4. /api3/briefReport — Жёлтые и красные записи
        r = requests.get("https://focus-api.kontur.ru/api3/briefReport",
                         params={"key": api_key, "inn": inn}, timeout=15)
        if r.status_code == 200 and r.json():
            data = r.json()
            brief = data[0] if isinstance(data, list) else data
            yellow = brief.get('yellowStatements', [])
            red = brief.get('redStatements', [])
            result['yellow_statements'] = len(yellow)
            result['red_statements'] = len(red)
            for y in yellow:
                result['risk_text'].append(f"⚠️ {y.get('text', '')}")
            for rd in red:
                result['risk_text'].append(f"🔴 {rd.get('text', '')}")

        # 5. /api3/scoring — Скоринг
        r = requests.get("https://focus-api.kontur.ru/api3/scoring",
                         params={"key": api_key, "inn": inn, "model": "FinState"}, timeout=15)
        if r.status_code == 200 and r.json():
            data = r.json()
            if data and len(data) > 0:
                result['scoring_score'] = data[0].get('score', 0)

        # 6-8. Расчёты из бухотчётности
        if buh_forms:
            years = sorted([f.get('year') for f in buh_forms if f.get('year')], reverse=True)
            last_year = years[0] if years else None

            def get_val(form, code, vtype='endValue'):
                for item in form:
                    if item.get('code') == code:
                        return item.get(vtype, 0)
                return 0

            if last_year:
                latest = next((f for f in buh_forms if f.get('year') == last_year), None)
                if latest:
                    f1 = latest.get('form1', [])
                    f2 = latest.get('form2', [])

                    eV_1230 = get_val(f1, 1230)
                    eV_2110 = get_val(f2, 2110)
                    eV_1520 = get_val(f1, 1520)
                    eV_1600 = get_val(f1, 1600)
                    eV_1400 = get_val(f1, 1400)
                    eV_1500 = get_val(f1, 1500)

                    NDS = 22
                    K1 = 1 + NDS / 100
                    K2 = 0.8

                    result['max_debt'] = max(0, int(((eV_1230 + eV_2110 * K1 * K2) - 0) / 12 * 0.6))

                    if eV_2110 > 0:
                        result['cred_day'] = int(((eV_1520 + eV_1520) / 2) / eV_2110 * 365)

                    result['equity'] = eV_1600 - (eV_1400 + eV_1500)

        return result
    except Exception as e:
        result['status'] = f'Error: {str(e)}'
        return result


def calculate_scores(df):
    """Рассчитывает баллы для каждой компании (топ-1 = +2, топ-2 = +1)."""
    df['score'] = 0
    df['score_details'] = [[] for _ in range(len(df))]

    # 1. Наименьшая доля суммы тендера к выручке
    df['revenue_ratio'] = df.apply(lambda r: (r['price'] / r['revenue'] * 100) if r['revenue'] > 0 else 999, axis=1)
    s = df['revenue_ratio'].sort_values().index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 2
        df.loc[s[0], 'score_details'].append("Доля тендера к выручке: +2")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 1
        df.loc[s[1], 'score_details'].append("Доля тендера к выручке: +1")

    # 2. Наибольший аванс
    s = df['max_debt'].sort_values(ascending=False).index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 2
        df.loc[s[0], 'score_details'].append("Наибольший аванс: +2")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 1
        df.loc[s[1], 'score_details'].append("Наибольший аванс: +1")

    # 3. Наибольшее превышение аванса к 10% от тендера
    df['advance_excess'] = df.apply(lambda r: (r['max_debt'] / (r['price'] * 0.1) * 100) if r['price'] > 0 else 0, axis=1)
    s = df['advance_excess'].sort_values(ascending=False).index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 2
        df.loc[s[0], 'score_details'].append("Превышение аванса к 10%: +2")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 1
        df.loc[s[1], 'score_details'].append("Превышение аванса к 10%: +1")

    # 4. Отсутствие жёлтых/красных записей
    for idx, row in df.iterrows():
        if row['yellow_statements'] == 0 and row['red_statements'] == 0:
            df.loc[idx, 'score'] += 2
            df.loc[idx, 'score_details'].append("Нет рисковых записей: +2")

    # 5. Наибольший штат
    s = df['employees'].sort_values(ascending=False).index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 2
        df.loc[s[0], 'score_details'].append("Наибольший штат: +2")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 1
        df.loc[s[1], 'score_details'].append("Наибольший штат: +1")

    # 6. Наибольший скоринг
    s = df['scoring_score'].sort_values(ascending=False).index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 2
        df.loc[s[0], 'score_details'].append("Наилучший скоринг: +2")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 1
        df.loc[s[1], 'score_details'].append("Наилучший скоринг: +1")

    # 7. Наименьшая оборачиваемость (если > 0)
    df['cred_day_pos'] = df['cred_day'].apply(lambda x: x if x > 0 else 9999)
    s = df['cred_day_pos'].sort_values().index.tolist()
    valid = [i for i in s if df.loc[i, 'cred_day_pos'] < 9999]
    if len(valid) >= 1:
        df.loc[valid[0], 'score'] += 2
        df.loc[valid[0], 'score_details'].append("Наименьшая оборачиваемость: +2")
    if len(valid) >= 2:
        df.loc[valid[1], 'score'] += 1
        df.loc[valid[1], 'score_details'].append("Наименьшая оборачиваемость: +1")

    # 8. Наибольшие чистые активы
    s = df['equity'].sort_values(ascending=False).index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 2
        df.loc[s[0], 'score_details'].append("Наибольшие чистые активы: +2")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 1
        df.loc[s[1], 'score_details'].append("Наибольшие чистые активы: +1")

    # 9. Наименьшая цена
    s = df['price'].sort_values().index.tolist()
    if len(s) >= 1:
        df.loc[s[0], 'score'] += 6
        df.loc[s[0], 'score_details'].append("Наименьшая цена: +6")
    if len(s) >= 2:
        df.loc[s[1], 'score'] += 3
        df.loc[s[1], 'score_details'].append("Наименьшая цена: +3")

    return df

# ----------------------------------------------------------------------------
# 6. ДИНАМИЧЕСКАЯ ФОРМА ВВОДА УЧАСТНИКОВ
# ----------------------------------------------------------------------------
st.markdown('<div class="search-card">', unsafe_allow_html=True)
st.markdown("### 👥 Участники тендера")
st.markdown("Добавьте всех участников — ИНН и ценовое предложение для каждого.")

# Отрисовка блоков участников
for i, participant in enumerate(st.session_state.participants):
    st.markdown('<div class="participant-block">', unsafe_allow_html=True)

    col_title, col_del = st.columns([5, 1])
    with col_title:
        st.markdown(f'<div class="participant-title">Участник {i + 1}</div>', unsafe_allow_html=True)
    with col_del:
        # Кнопка удаления доступна, только если участников больше двух
        if len(st.session_state.participants) > 2:
            if st.button("✕", key=f"del_{i}", help="Удалить участника"):
                st.session_state.participants.pop(i)
                st.session_state.analysis_result = None
                st.rerun()

    col_inn, col_price = st.columns([1, 1])
    with col_inn:
        inn_val = st.text_input(
            "ИНН",
            value=participant["inn"],
            max_chars=12,
            placeholder="10 или 12 цифр",
            key=f"inn_{i}"
        )
        st.session_state.participants[i]["inn"] = inn_val

    with col_price:
        price_val = st.number_input(
            "Ценовое предложение (руб.)",
            value=float(participant["price"]),
            min_value=0.0,
            step=1000.0,
            format="%.2f",
            key=f"price_{i}"
        )
        st.session_state.participants[i]["price"] = price_val

    st.markdown('</div>', unsafe_allow_html=True)

# Кнопки управления
col_add, col_check = st.columns([1, 2])

with col_add:
    if st.button("➕ Добавить участника", use_container_width=True, key="add_participant"):
        st.session_state.participants.append({"inn": "", "price": 0.0})
        st.session_state.analysis_result = None
        st.rerun()

with col_check:
    if st.button("🚀 Отправить на проверку", use_container_width=True, type="primary", key="submit_check"):
        errors = []
        for idx, p in enumerate(st.session_state.participants):
            if not p["inn"] or len(p["inn"]) not in [10, 12] or not p["inn"].isdigit():
                errors.append(f"Участник {idx + 1}: некорректный ИНН")
            if p["price"] <= 0:
                errors.append(f"Участник {idx + 1}: не указана цена")

        if not api_key:
            errors.append("API ключ Контур.Фокуса не настроен")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            st.session_state.run_analysis = True
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 7. ЗАПУСК АНАЛИЗА
# ----------------------------------------------------------------------------
if st.session_state.run_analysis:
    st.session_state.run_analysis = False

    with st.spinner("Запрос данных из Контур.Фокуса..."):
        rows = []
        for p in st.session_state.participants:
            data = fetch_kontur_data(p['inn'], api_key)
            data['price'] = p['price']
            rows.append(data)

        df = pd.DataFrame(rows)
        df = calculate_scores(df)
        df = df.sort_values('score', ascending=False).reset_index(drop=True)
        st.session_state.analysis_result = df

# ----------------------------------------------------------------------------
# 8. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ
# ----------------------------------------------------------------------------
if st.session_state.analysis_result is not None:
    df = st.session_state.analysis_result

    st.markdown("---")
    st.markdown("## 📊 Результаты сравнения")

    # Итоговая таблица
    display_cols = ['name', 'inn', 'price', 'revenue', 'employees', 'scoring_score',
                    'max_debt', 'cred_day', 'equity', 'yellow_statements', 'red_statements', 'score']
    display_df = df[display_cols].copy()
    display_df.columns = ['Компания', 'ИНН', 'Цена', 'Выручка', 'Штат',
                          'Скоринг', 'Аванс', 'Оборач.', 'Чистые активы', 'Жёлтых', 'Красных', 'Баллы']

    st.dataframe(display_df.style.format({
        'Цена': '{:,.0f}', 'Выручка': '{:,.0f}',
        'Аванс': '{:,.0f}', 'Чистые активы': '{:,.0f}'
    }), use_container_width=True, hide_index=True)

    # Функция отрисовки карточки участника
    def render_card(row, position_label, css_class, badge_class):
        risk_html = ""
        if row['risk_text']:
            risk_html = f"""
            <div style="margin-top: 14px; padding-top: 12px; border-top: 1px solid {LIGHT_GRAY};">
                <div style="font-size: 12px; color: {GRAY}; text-transform: uppercase; margin-bottom: 6px;">Рисковые записи</div>
                <div style="font-size: 14px; color: {DARK}; line-height: 1.5;">{'<br>'.join(row['risk_text'][:5])}</div>
            </div>
            """

        st.markdown(f"""
        <div class="results-card {css_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div class="company-name">{position_label} {row['name']}</div>
                    <div class="company-inn">ИНН {row['inn']}</div>
                </div>
                <div class="score-badge {badge_class}">Баллы: {row['score']}</div>
            </div>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">Ценовое предложение</div>
                    <div class="value">{row['price']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Выручка (посл. период)</div>
                    <div class="value">{row['revenue']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Сумма допустимого аванса</div>
                    <div class="value">{row['max_debt']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Оборачиваемость</div>
                    <div class="value">{row['cred_day']} дн.</div>
                </div>
                <div class="result-item">
                    <div class="label">Чистые активы</div>
                    <div class="value">{row['equity']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Скоринг / Штат</div>
                    <div class="value">{row['scoring_score']} / {row['employees']} чел.</div>
                </div>
            </div>
            <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid {LIGHT_GRAY};">
                <strong>Детализация баллов:</strong><br>
                <span style="font-size: 14px; color: #4a4a4a;">{' | '.join(row['score_details']) if row['score_details'] else 'Нет начислений'}</span>
            </div>
            {risk_html}
        </div>
        """, unsafe_allow_html=True)

    # Лучший кандидат
    winner = df.iloc[0]
    render_card(winner, "🏆", "winner-card", "")

    # Резервный
    if len(df) > 1:
        reserve = df.iloc[1]
        render_card(reserve, "🔄", "reserve-card", "reserve")

    # Остальные участники
    if len(df) > 2:
        st.markdown("### Остальные участники")
        for idx in range(2, len(df)):
            row = df.iloc[idx]
            render_card(row, f"#{idx + 1}", "other-card", "other")

# ----------------------------------------------------------------------------
# 9. ПОДВАЛ
# ----------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    © 2026 Брусника · Проверка контрагентов
</div>
""", unsafe_allow_html=True)
