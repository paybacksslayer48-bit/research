import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Настройка интерфейса под мобилки
st.set_page_config(page_title="Lead Hunter", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 50px; font-size: 18px; font-weight: bold; border-radius: 10px; }
    .lead-card { border: 2px solid #e0e0e0; padding: 20px; border-radius: 15px; margin-bottom: 15px; background: white; }
    .status-bad { color: #d9534f; font-weight: bold; }
    .status-ok { color: #5cb85c; font-weight: bold; }
    .phone-link { background: #28a745; color: white; padding: 12px; text-align: center; text-decoration: none; display: block; border-radius: 8px; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("📱 Lead Hunter: Поиск клиентов")

# Ввод данных
col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input("Что ищем?", placeholder="Напр: Стоматология Одесса", label_visibility="collapsed")
with col2:
    search_btn = st.button("Искать")

def analyze_site(url):
    if not url or url == "N/A":
        return "❌ САЙТА НЕТ", "status-bad"
    if "business.site" in url or "wix" in url or "tilda" in url:
        return "⚠️ КОНСТРУКТОР (ГОВНО)", "status-bad"
    return "✅ ЕСТЬ САЙТ", "status-ok"

def get_leads(q):
    # Используем альтернативный поиск (DuckDuckGo или подобные через парсинг)
    # Это работает быстрее и не требует API ключей
    headers = {'User-Agent': 'Mozilla/5.0'}
    search_url = f"https://www.google.com/search?q={q.replace(' ', '+')}+телефон+сайт"
    
    leads = []
    try:
        r = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Парсим результаты (упрощенная логика для стабильности)
        for g in soup.find_all('div', class_='tF2Cxc'):
            name = g.find('h3').text if g.find('h3') else "Бизнес"
            link = g.find('a')['href'] if g.find('a') else "N/A"
            
            # Пытаемся найти телефон в тексте описания
            snippet = g.find('div', class_='VwiC3b').text if g.find('div', class_='VwiC3b') else ""
            phone_match = re.search(r'\+?\d{10,12}', snippet)
            phone = phone_match.group(0) if phone_match else "Скрыт в картах"
            
            status, status_class = analyze_site(link)
            
            leads.append({
                "name": name,
                "link": link,
                "phone": phone,
                "status": status,
                "class": status_class
            })
    except:
        st.error("Ошибка парсинга. Попробуй еще раз.")
    return leads

if search_btn and query:
    with st.spinner('Ищу жирных лидов...'):
        results = get_leads(query)
        
        if not results:
            st.warning("Ничего не найдено. Попробуй изменить запрос (напр. добавить город).")
        
        for idx, lead in enumerate(results):
            with st.container():
                st.markdown(f"""
                <div class="lead-card">
                    <div style="font-size: 20px; font-weight: bold;">{lead['name']}</div>
                    <div class="{lead['class']}">{lead['status']}</div>
                    <div style="margin-top: 5px;">🌐 {lead['link']}</div>
                    <div style="font-size: 18px; margin-top: 5px;">📞 <b>{lead['phone']}</b></div>
                    <a href="tel:{lead['phone']}" class="phone-link">ПОЗВОНИТЬ КЛИЕНТУ</a>
                </div>
                """, unsafe_allow_html=True)
                
                # Кнопка копирования для каждого лида
                copy_text = f"Имя: {lead['name']}\nТел: {lead['phone']}\nСайт: {lead['link']}"
                st.code(copy_text, language="text")
