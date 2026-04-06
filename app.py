import os
import subprocess
import sys

# АВТО-УСТАНОВКА БИБЛИОТЕК (для тех, кто не хочет возиться с настройками)
def install_dependencies():
    required = {'beautifulsoup4', 'requests', 'pandas', 'lxml'}
    try:
        import bs4
        import requests
        import pandas
    except ImportError:
        st.info("Устанавливаю необходимые модули, подожди 10 секунд...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *required])
        st.success("Все готово! Сейчас страница перезагрузится.")
        st.rerun()

import streamlit as st

# Запускаем проверку при старте
if 'installed' not in st.session_state:
    install_dependencies()
    st.session_state['installed'] = True

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

# НАСТРОЙКА ИНТЕРФЕЙСА
st.set_page_config(page_title="Lead Finder 800$", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 60px; font-size: 20px; background-color: #007bff; color: white; border-radius: 15px; }
    .lead-card { border: 2px solid #f0f2f6; padding: 20px; border-radius: 15px; margin-bottom: 20px; background-color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .status-bad { background-color: #ffcccc; color: #cc0000; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    .status-ok { background-color: #ccffcc; color: #006600; padding: 5px 10px; border-radius: 5px; font-weight: bold; }
    .call-btn { background-color: #28a745; color: white; padding: 15px; text-align: center; text-decoration: none; display: block; border-radius: 10px; font-weight: bold; margin-top: 10px; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Поиск клиентов на разработку сайтов")

query = st.text_input("Введите услугу и город (например: СТО Одесса)", placeholder="Кого ищем?")

def check_site_quality(url):
    if not url or url == "N/A":
        return "❌ САЙТА НЕТ", "status-bad"
    bad_platforms = ['business.site', 'wix.com', 'tilda.ws', 'linktree']
    if any(plat in url for plat in bad_platforms):
        return "⚠️ ГОВНО-САЙТ (КОНСТРУКТОР)", "status-bad"
    return "✅ ЕСТЬ САЙТ", "status-ok"

def search_leads(q):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    # Поиск через Bing (он меньше банит, чем Google, при парсинге без ключей)
    url = f"https://www.bing.com/search?q={q.replace(' ', '+')}+телефон+сайт"
    
    leads = []
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for item in soup.find_all('li', class_='b_algo'):
            title = item.find('h2').text if item.find('h2') else "Бизнес"
            link = item.find('a')['href'] if item.find('a') else "N/A"
            snippet = item.text
            
            # Поиск телефона регуляркой
            phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}', snippet)
            phone = phone_match.group(0) if phone_match else "Нужно найти на странице"
            
            status_text, status_class = check_site_quality(link)
            
            leads.append({
                "name": title,
                "link": link,
                "phone": phone,
                "status": status_text,
                "class": status_class
            })
    except Exception as e:
        st.error(f"Ошибка поиска: {e}")
    return leads

if st.button("НАЙТИ ЛИДОВ"):
    if query:
        with st.spinner('Ищу тех, кто заплатит тебе $800...'):
            results = search_leads(query)
            if results:
                for lead in results:
                    st.markdown(f"""
                    <div class="lead-card">
                        <div style="font-size: 22px; font-weight: bold;">{lead['name']}</div>
                        <div style="margin: 10px 0;">
                            <span class="{lead['class']}">{lead['status']}</span>
                        </div>
                        <div style="color: #666;">🌐 {lead['link']}</div>
                        <div style="font-size: 20px; margin: 10px 0;">📞 <b>{lead['phone']}</b></div>
                        <a href="tel:{lead['phone']}" class="call-btn">📞 ПОЗВОНИТЬ</a>
                    </div>
                    """, unsafe_allow_html=True)
                    # Кнопка для быстрого копирования
                    st.code(f"{lead['name']} | {lead['phone']} | {lead['link']}")
            else:
                st.warning("Ничего не нашли. Попробуй запрос покороче, например 'Окна Киев'.")
