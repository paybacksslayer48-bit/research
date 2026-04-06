import streamlit as st
import pandas as pd
from duckduckgo_search import DDGS
import re

# Настройка страницы под мобилки
st.set_page_config(page_title="LEAD HUNTER 800$", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; height: 60px; font-size: 20px; background-color: #2e7d32; color: white; border-radius: 12px; border: none; font-weight: bold; }
    .lead-card { border: 2px solid #e0e0e0; padding: 15px; border-radius: 15px; margin-bottom: 15px; background-color: #ffffff; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .status-bad { color: #d32f2f; background: #ffebee; padding: 4px 8px; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 5px; }
    .status-ok { color: #388e3c; background: #e8f5e9; padding: 4px 8px; border-radius: 5px; font-weight: bold; display: inline-block; margin-bottom: 5px; }
    .call-link { background: #1976d2; color: white !important; text-align: center; padding: 12px; display: block; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Поиск клиентов на сайты")
st.write("Введи услугу и город. Я найду бизнесы и проверю их сайты.")

query = st.text_input("", placeholder="Напр: Стоматолог Одесса или СТО Киев")

def check_site(url):
    if not url or url == "N/A": return "🔴 НЕТ САЙТА", "status-bad"
    bad_list = ['wix', 'tilda', 'business.site', 'facebook.com', 'instagram.com', 'linktr.ee']
    if any(x in url.lower() for x in bad_list):
        return "🟠 САЙТ-МУСОР (КОНСТРУКТОР)", "status-bad"
    return "🟢 ЕСТЬ САЙТ", "status-ok"

def find_leads(q):
    leads = []
    try:
        with DDGS() as ddgs:
            # Ищем 20 результатов
            results = ddgs.text(f"{q} телефон сайт", max_results=20)
            
            for r in results:
                title = r.get('title', 'Бизнес')
                link = r.get('href', 'N/A')
                body = r.get('body', '')
                
                # Ищем номер телефона в тексте
                phone_match = re.search(r'(\+38|0)\d{9,10}', body.replace(" ", "").replace("-", "").replace("(", "").replace(")", ""))
                phone = phone_match.group(0) if phone_match else "Найди на сайте"
                
                status_text, status_class = check_site(link)
                
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

if st.button("🔍 НАЙТИ КЛИЕНТОВ"):
    if query:
        with st.spinner('Копаюсь в базе данных...'):
            results = find_leads(query)
            if results:
                st.success(f"Найдено {len(results)} заведений")
                for lead in results:
                    with st.container():
                        st.markdown(f"""
                        <div class="lead-card">
                            <div style="font-size: 18px; font-weight: bold;">{lead['name']}</div>
                            <div class="{lead['class']}">{lead['status']}</div>
                            <div style="color: #555; font-size: 14px; overflow: hidden; text-overflow: ellipsis;">🌐 {lead['link']}</div>
                            <div style="font-size: 20px; margin-top: 10px;">📞 <b>{lead['phone']}</b></div>
                            <a href="tel:{lead['phone']}" class="call-link">ПОЗВОНИТЬ</a>
                        </div>
                        """, unsafe_allow_html=True)
                        # Кнопка Копировать (встроенная в Streamlit)
                        st.code(f"{lead['name']}\nТел: {lead['phone']}\nСайт: {lead['link']}")
            else:
                st.info("Ничего не нашли. Попробуй сменить город.")
    else:
        st.warning("Впиши что-то в поиск!")
