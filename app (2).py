# app.py
import streamlit as st
import requests
import pandas as pd
import numpy as np
import time

# ----------------------------------------------------------------------------
# 1. НАСТРОЙКА СТРАНИЦЫ
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Брусника — проверка контрагента",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# CSS (оставляем ваш стиль, добавляем немного для новых элементов)
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
    .logo {{ display: flex; align-items: center; gap: 10px; text-decoration: none; color: {DARK}; }}
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
        margin-bottom: 32px;
    }}
    
    /* Стили для формы */
    .stTextInput > div > div > input {{
        border-radius: 12px; border: 1px solid #dcdcdc; padding: 12px 20px; font-size: 16px;
    }}
    .stNumberInput > div > div > input {{
        border-radius: 12px; border: 1px solid #dcdcdc; padding: 12px 20px; font-size: 16px;
    }}
    .stButton > button {{
        background: {DARK} !important; color: {WHITE} !important; border-radius: 12px !important;
        padding: 14px 40px !important; font-weight: 500 !important; font-size: 16px !important;
        border: none !important; width: 100%; height: 52px;
    }}
    .stButton > button:hover {{ background: #333 !important; }}
    
    .results-card {{
        background: {WHITE}; border-radius: 24px; padding: 36px 40px;
        border: 1px solid {BORDER_COLOR}; box-shadow: 0 12px 40px rgba(0, 0, 0, 0.04);
        margin-bottom: 24px;
    }}
    .winner-card {{ border-left: 6px solid {GREEN}; }}
    .reserve-card {{ border-left: 6px solid {BLUE}; }}

    .company-name {{ font-size: 24px; font-weight: 600; letter-spacing: -0.2px; color: {DARK}; }}
    .company-inn {{ font-size: 16px; color: {GRAY}; margin-top: 2px; }}
    
    .result-grid {{
        display: grid; grid-template-columns: 1fr 1fr; gap: 16px 30px; margin-top: 20px;
    }}
    .result-item {{ border-bottom: 1px solid {LIGHT_GRAY}; padding-bottom: 10px; }}
    .result-item .label {{ font-size: 12px; color: {GRAY}; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
    .result-item .value {{ font-size: 18px; font-weight: 500; color: {DARK}; }}
    
    .score-badge {{
        display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600;
        background: #e6f0e6; color: {GREEN};
    }}
    .score-badge.reserve {{ background: #e0ecf5; color: {BLUE}; }}

    .footer {{
        margin-top: 40px; padding: 24px; border-top: 1px solid {BORDER_COLOR}; background: {WHITE};
        text-align: center; font-size: 14px; color: {GRAY};
    }}
    .footer a {{ color: {DARK}; text-decoration: none; margin: 0 12px; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 2. ШАПКА И ЗАГОЛОВОК
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
# 3. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЯ
# ----------------------------------------------------------------------------
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'form_data' not in st.session_state:
    st.session_state.form_data = None

# ----------------------------------------------------------------------------
# 4. ФОРМА ВВОДА ДАННЫХ
# ----------------------------------------------------------------------------
with st.form("tender_form"):
    st.markdown('<div class="search-card">', unsafe_allow_html=True)
    st.markdown("### Введите данные участников тендера")
    st.markdown("Заполните ИНН и ценовые предложения для двух компаний.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Участник 1**")
        inn1 = st.text_input("ИНН первой компании", max_chars=12, placeholder="10 или 12 цифр", key="inn1")
        price1 = st.number_input("Ценовое предложение (руб.)", min_value=0.0, step=1000.0, key="price1", format="%.2f")
    
    with col2:
        st.markdown("**Участник 2**")
        inn2 = st.text_input("ИНН второй компании", max_chars=12, placeholder="10 или 12 цифр", key="inn2")
        price2 = st.number_input("Ценовое предложение (руб.)", min_value=0.0, step=1000.0, key="price2", format="%.2f")
    
    submitted = st.form_submit_button("🚀 Отправить на проверку", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 5. ЛОГИКА ПРОВЕРКИ (основная функция)
# ----------------------------------------------------------------------------
api_key = st.secrets.get("FOCUS_API_KEY", "")

def fetch_kontur_data(inn, api_key):
    """Собирает данные из всех необходимых методов Контур.Фокуса."""
    result = {
        'inn': inn,
        'name': 'Неизвестно',
        'revenue': 0,
        'employees': 0,
        'yellow_statements': 0,
        'red_statements': 0,
        'risk_text': [],
        'scoring_score': 0,
        'max_debt': 0,
        'cred_day': 0,
        'equity': 0,
        'status': 'OK'
    }
    
    if not api_key:
        result['status'] = 'No API Key'
        return result
    
    try:
        # 1. /api3/req - Название компании
        req_resp = requests.get("https://focus-api.kontur.ru/api3/req", 
                                params={"key": api_key, "inn": inn}, timeout=15)
        if req_resp.status_code == 200 and req_resp.json():
            req_data = req_resp.json()[0]
            result['name'] = req_data.get('UL', {}).get('legalName', {}).get('short', 'Неизвестно')
        
        # 2. /api3/accountingReports - Выручка
        acc_resp = requests.get("https://focus-api.kontur.ru/api3/accountingReports",
                                params={"key": api_key, "inn": inn}, timeout=15)
        buh_forms = []
        if acc_resp.status_code == 200 and acc_resp.json():
            buh_data = acc_resp.json()
            if buh_data and len(buh_data) > 0:
                buh_forms = buh_data[0].get('buhForms', [])
                # Ищем последний год и выручку (код 2110)
                years = sorted([f.get('year') for f in buh_forms if f.get('year')], reverse=True)
                if years:
                    latest = next((f for f in buh_forms if f.get('year') == years[0]), None)
                    if latest:
                        for item in latest.get('form2', []):
                            if item.get('code') == 2110:
                                result['revenue'] = item.get('endValue', 0)
                                break
        
        # 3. /api3/legalAnalytics - Штат сотрудников
        legal_resp = requests.get("https://focus-api.kontur.ru/api3/legalAnalytics",
                                  params={"key": api_key, "inn": inn}, timeout=15)
        if legal_resp.status_code == 200 and legal_resp.json():
            legal_data = legal_resp.json()
            # Ищем среднесписочную численность
            if legal_data and len(legal_data) > 0:
                analytics = legal_data[0]
                # Пытаемся найти данные о численности
                emp_data = analytics.get('employees', [])
                if emp_data:
                    result['employees'] = emp_data[-1].get('count', 0) if isinstance(emp_data, list) else emp_data.get('count', 0)
        
        # 4. /api3/briefReport - Желтые и красные записи
        brief_resp = requests.get("https://focus-api.kontur.ru/api3/briefReport",
                                  params={"key": api_key, "inn": inn}, timeout=15)
        if brief_resp.status_code == 200 and brief_resp.json():
            brief_data = brief_resp.json()[0] if isinstance(brief_resp.json(), list) else brief_resp.json()
            yellow = brief_data.get('yellowStatements', [])
            red = brief_data.get('redStatements', [])
            result['yellow_statements'] = len(yellow)
            result['red_statements'] = len(red)
            # Собираем текст для отображения
            for y in yellow:
                result['risk_text'].append(f"⚠️ {y.get('text', '')}")
            for r in red:
                result['risk_text'].append(f"🔴 {r.get('text', '')}")
        
        # 5. /api3/scoring - Скоринговая оценка
        score_resp = requests.get("https://focus-api.kontur.ru/api3/scoring",
                                  params={"key": api_key, "inn": inn, "model": "FinState"}, timeout=15)
        if score_resp.status_code == 200 and score_resp.json():
            score_data = score_resp.json()
            if score_data and len(score_data) > 0:
                result['scoring_score'] = score_data[0].get('score', 0)
        
        # 6-8. Расчёт аванса, оборачиваемости, чистых активов (из вашего скрипта)
        if buh_forms:
            # Определяем последний год
            years = sorted([f.get('year') for f in buh_forms if f.get('year')], reverse=True)
            last_year = years[0] if years else None
            prev_year = years[1] if len(years) > 1 else None
            
            def get_val(form, code, vtype='endValue'):
                for item in form:
                    if item.get('code') == code:
                        return item.get(vtype, 0)
                return 0
            
            if last_year:
                latest = next((f for f in buh_forms if f.get('year') == last_year), None)
                if latest:
                    form1 = latest.get('form1', [])
                    form2 = latest.get('form2', [])
                    
                    eV_1230 = get_val(form1, 1230)
                    eV_2110 = get_val(form2, 2110)
                    eV_1520 = get_val(form1, 1520)
                    eV_1210 = get_val(form1, 1210)
                    eV_1220 = get_val(form1, 1220)
                    eV_1250 = get_val(form1, 1250)
                    eV_1510 = get_val(form1, 1510)
                    eV_1600 = get_val(form1, 1600)
                    eV_1400 = get_val(form1, 1400)
                    eV_1500 = get_val(form1, 1500)
                    eV_2400 = get_val(form2, 2400)
                    
                    NDS = 22
                    K1 = 1 + NDS/100
                    K2 = 0.8
                    
                    # Расчёт аванса
                    result['max_debt'] = max(0, int(((eV_1230 + eV_2110 * K1 * K2) - 0) / 12 * 0.6))
                    
                    # Расчёт оборачиваемости
                    if eV_2110 > 0:
                        result['cred_day'] = int(((eV_1520 + eV_1520) / 2) / eV_2110 * 365)
                    
                    # Чистые активы
                    result['equity'] = eV_1600 - (eV_1400 + eV_1500)
        
        return result
        
    except Exception as e:
        result['status'] = f'Error: {str(e)}'
        return result

def calculate_scores(df):
    """Рассчитывает баллы для каждой компании."""
    df['score'] = 0
    df['score_details'] = [[] for _ in range(len(df))]
    
    # 1. Наименьшая доля суммы тендера к выручке (цена / выручка * 100)
    df['revenue_ratio'] = df.apply(lambda r: (r['price'] / r['revenue'] * 100) if r['revenue'] > 0 else 999, axis=1)
    sorted_idx = df['revenue_ratio'].sort_values().index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 2
        df.loc[sorted_idx[0], 'score_details'].append("Доля тендера к выручке: +2")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 1
        df.loc[sorted_idx[1], 'score_details'].append("Доля тендера к выручке: +1")
    
    # 2. Наибольшая сумма допустимого аванса
    sorted_idx = df['max_debt'].sort_values(ascending=False).index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 2
        df.loc[sorted_idx[0], 'score_details'].append("Наибольший аванс: +2")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 1
        df.loc[sorted_idx[1], 'score_details'].append("Наибольший аванс: +1")
    
    # 3. Наибольшее превышение суммы аванса к 10% от суммы тендера
    df['advance_excess'] = df.apply(lambda r: (r['max_debt'] / (r['price'] * 0.1) * 100) if r['price'] > 0 else 0, axis=1)
    sorted_idx = df['advance_excess'].sort_values(ascending=False).index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 2
        df.loc[sorted_idx[0], 'score_details'].append("Превышение аванса к 10%: +2")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 1
        df.loc[sorted_idx[1], 'score_details'].append("Превышение аванса к 10%: +1")
    
    # 4. Отсутствие желтых и красных записей
    for idx, row in df.iterrows():
        if row['yellow_statements'] == 0 and row['red_statements'] == 0:
            df.loc[idx, 'score'] += 2
            df.loc[idx, 'score_details'].append("Нет рисковых записей: +2")
    
    # 5. Наибольший штат сотрудников
    sorted_idx = df['employees'].sort_values(ascending=False).index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 2
        df.loc[sorted_idx[0], 'score_details'].append("Наибольший штат: +2")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 1
        df.loc[sorted_idx[1], 'score_details'].append("Наибольший штат: +1")
    
    # 6. Наибольшая сумма скоринговых оценок
    sorted_idx = df['scoring_score'].sort_values(ascending=False).index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 2
        df.loc[sorted_idx[0], 'score_details'].append("Наилучший скоринг: +2")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 1
        df.loc[sorted_idx[1], 'score_details'].append("Наилучший скоринг: +1")
    
    # 7. Наименьшая оборачиваемость кредиторской задолженности (если > 0)
    df['cred_day_positive'] = df['cred_day'].apply(lambda x: x if x > 0 else 9999)
    sorted_idx = df['cred_day_positive'].sort_values().index.tolist()
    valid_idx = [i for i in sorted_idx if df.loc[i, 'cred_day_positive'] < 9999]
    if len(valid_idx) >= 1:
        df.loc[valid_idx[0], 'score'] += 2
        df.loc[valid_idx[0], 'score_details'].append("Наименьшая оборачиваемость: +2")
    if len(valid_idx) >= 2:
        df.loc[valid_idx[1], 'score'] += 1
        df.loc[valid_idx[1], 'score_details'].append("Наименьшая оборачиваемость: +1")
    
    # 8. Наибольший размер чистых активов
    sorted_idx = df['equity'].sort_values(ascending=False).index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 2
        df.loc[sorted_idx[0], 'score_details'].append("Наибольшие чистые активы: +2")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 1
        df.loc[sorted_idx[1], 'score_details'].append("Наибольшие чистые активы: +1")
    
    # 9. Наименьшая цена предложения по тендеру
    sorted_idx = df['price'].sort_values().index.tolist()
    if len(sorted_idx) >= 1:
        df.loc[sorted_idx[0], 'score'] += 6
        df.loc[sorted_idx[0], 'score_details'].append("Наименьшая цена: +6")
    if len(sorted_idx) >= 2:
        df.loc[sorted_idx[1], 'score'] += 3
        df.loc[sorted_idx[1], 'score_details'].append("Наименьшая цена: +3")
    
    return df

# Обработка отправки формы
if submitted:
    # Валидация
    errors = []
    if not inn1 or len(inn1) not in [10, 12]:
        errors.append("Введите корректный ИНН для первой компании")
    if not inn2 or len(inn2) not in [10, 12]:
        errors.append("Введите корректный ИНН для второй компании")
    if price1 <= 0:
        errors.append("Введите цену для первой компании")
    if price2 <= 0:
        errors.append("Введите цену для второй компании")
    if not api_key:
        errors.append("API ключ Контур.Фокуса не настроен")
    
    if errors:
        for e in errors:
            st.error(f"❌ {e}")
    else:
        with st.spinner("Запрос данных из Контур.Фокуса..."):
            # Собираем данные по обеим компаниям
            data1 = fetch_kontur_data(inn1, api_key)
            data1['price'] = price1
            
            data2 = fetch_kontur_data(inn2, api_key)
            data2['price'] = price2
            
            df = pd.DataFrame([data1, data2])
            
            # Рассчитываем баллы
            df = calculate_scores(df)
            
            # Сортируем по баллам
            df = df.sort_values('score', ascending=False).reset_index(drop=True)
            
            st.session_state.analysis_result = df
            st.session_state.form_data = {'inn1': inn1, 'price1': price1, 'inn2': inn2, 'price2': price2}

# ----------------------------------------------------------------------------
# 6. ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ
# ----------------------------------------------------------------------------
if st.session_state.analysis_result is not None:
    df = st.session_state.analysis_result
    
    st.markdown("---")
    st.markdown("## 📊 Результаты сравнения")
    
    # Таблица
    display_cols = ['name', 'inn', 'price', 'revenue', 'employees', 'scoring_score', 
                    'max_debt', 'cred_day', 'equity', 'yellow_statements', 'red_statements', 'score']
    display_df = df[display_cols].copy()
    display_df.columns = ['Компания', 'ИНН', 'Цена', 'Выручка', 'Штат', 
                          'Скоринг', 'Аванс', 'Оборач.', 'Чистые активы', 'Жёлтых', 'Красных', 'Баллы']
    
    st.dataframe(display_df.style.format({
        'Цена': '{:,.0f}',
        'Выручка': '{:,.0f}',
        'Аванс': '{:,.0f}',
        'Чистые активы': '{:,.0f}'
    }), use_container_width=True, hide_index=True)
    
    # Лучший кандидат
    winner = df.iloc[0]
    st.markdown(f"""
    <div class="results-card winner-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="company-name">🏆 {winner['name']}</div>
                <div class="company-inn">ИНН {winner['inn']}</div>
            </div>
            <div class="score-badge">Баллы: {winner['score']}</div>
        </div>
        <div class="result-grid">
            <div class="result-item">
                <div class="label">Ценовое предложение</div>
                <div class="value">{winner['price']:,.0f} ₽</div>
            </div>
            <div class="result-item">
                <div class="label">Выручка (посл. период)</div>
                <div class="value">{winner['revenue']:,.0f} ₽</div>
            </div>
            <div class="result-item">
                <div class="label">Сумма допустимого аванса</div>
                <div class="value">{winner['max_debt']:,.0f} ₽</div>
            </div>
            <div class="result-item">
                <div class="label">Оборачиваемость</div>
                <div class="value">{winner['cred_day']} дн.</div>
            </div>
            <div class="result-item">
                <div class="label">Чистые активы</div>
                <div class="value">{winner['equity']:,.0f} ₽</div>
            </div>
            <div class="result-item">
                <div class="label">Скоринг</div>
                <div class="value">{winner['scoring_score']}</div>
            </div>
        </div>
        <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid {LIGHT_GRAY};">
            <strong>Детализация баллов:</strong><br>
            {' | '.join(winner['score_details'])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Резервный кандидат (если есть)
    if len(df) > 1:
        reserve = df.iloc[1]
        st.markdown(f"""
        <div class="results-card reserve-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div class="company-name">🔄 {reserve['name']} (резерв)</div>
                    <div class="company-inn">ИНН {reserve['inn']}</div>
                </div>
                <div class="score-badge reserve">Баллы: {reserve['score']}</div>
            </div>
            <div class="result-grid">
                <div class="result-item">
                    <div class="label">Ценовое предложение</div>
                    <div class="value">{reserve['price']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Выручка (посл. период)</div>
                    <div class="value">{reserve['revenue']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Сумма допустимого аванса</div>
                    <div class="value">{reserve['max_debt']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Оборачиваемость</div>
                    <div class="value">{reserve['cred_day']} дн.</div>
                </div>
                <div class="result-item">
                    <div class="label">Чистые активы</div>
                    <div class="value">{reserve['equity']:,.0f} ₽</div>
                </div>
                <div class="result-item">
                    <div class="label">Скоринг</div>
                    <div class="value">{reserve['scoring_score']}</div>
                </div>
            </div>
            <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid {LIGHT_GRAY};">
                <strong>Детализация баллов:</strong><br>
                {' | '.join(reserve['score_details'])}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 7. ПОДВАЛ
# ----------------------------------------------------------------------------
st.markdown("""
<div class="footer">
    © 2026 Брусника · Проверка контрагентов
</div>
""", unsafe_allow_html=True)