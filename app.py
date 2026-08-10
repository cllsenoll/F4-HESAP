import streamlit as st
import pandas as pd
import io
import re
import urllib.parse

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Görükle Acente - Hesap & F4 Paneli",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU
if 'active_tab' not in st.session_state: st.session_state.active_tab = "HESAP"
if 'account_df' not in st.session_state: st.session_state.account_df = None
if 'hesap_df' not in st.session_state: st.session_state.hesap_df = None
if 'kasa_miktari' not in st.session_state: st.session_state.kasa_miktari = 0.0
if 'raw_df' not in st.session_state: st.session_state.raw_df = None
if 'f4_df' not in st.session_state: st.session_state.f4_df = None

KULLANICI_ISIM = "CELAL ŞENOL"
KULLANICI_GOREV = "Şube Şefi"

# ==========================================
# KURUMSAL TEMA (Lacivert, Mavi, Turuncu, Beyaz)
# ==========================================
custom_css = """
<style>
    :root {
        --lacivert: #003366;
        --mavi: #0047AB;
        --turuncu: #FF6600;
        --beyaz: #FFFFFF;
    }

    .stApp {
        background-color: var(--lacivert);
        color: var(--beyaz);
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: var(--beyaz) !important;
        font-family: 'Segoe UI', Tahoma, sans-serif;
    }

    /* Sidebar - Mavi ve Lacivert Geçişi */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--mavi) 0%, var(--lacivert) 100%) !important;
    }

    /* Butonlar - Turuncu Vurgulu */
    div.stButton > button {
        background-color: var(--turuncu) !important;
        color: var(--beyaz) !important;
        border: 2px solid var(--beyaz) !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    div.stButton > button:hover {
        background-color: var(--beyaz) !important;
        color: var(--turuncu) !important;
        border: 2px solid var(--turuncu) !important;
    }

    /* Kasa Kutusu */
    .kasa-box {
        background-color: var(--mavi);
        border: 2px solid var(--turuncu);
        border-radius: 15px;
        padding: 20px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# [Geri kalan fonksiyonlar (clean_string, parse_turkish_float, process_... vb.) aynı şekilde kalıyor]
# (Kodun karmaşıklığını artırmamak adına fonksiyonları buraya tekrar yazmadım, 
# önceki kodunuzdaki fonksiyonları bu CSS bloğunun altına aynen ekleyin.)

# Önemli: Eğer kodun tamamını tek blokta istiyorsanız, 
# fonksiyonları dahil ederek aşağıda birleştirilmiş halini sunabilirim.
