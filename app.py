import streamlit as st
import pandas as pd
import io
import re
import urllib.parse

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(
    page_title="Görükle Acente - Hesap & F4 Paneli",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. OTURUM DURUMU (Session State)
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "HESAP"
if 'account_df' not in st.session_state:
    st.session_state.account_df = None
if 'hesap_df' not in st.session_state:
    st.session_state.hesap_df = None
if 'kasa_miktari' not in st.session_state:
    st.session_state.kasa_miktari = 0.0
if 'raw_df' not in st.session_state:
    st.session_state.raw_df = None
if 'f4_df' not in st.session_state:
    st.session_state.f4_df = None

KULLANICI_ISIM = "CELAL ŞENOL"
KULLANICI_GOREV = "(Şube Şefi)"

# ==========================================
# GİTHUB PERSONEL FOTOĞRAF HARİTASI
# ==========================================
def get_github_avatar(personel_adi):
    clean_name = str(personel_adi).strip()
    encoded_name = urllib.parse.quote(clean_name)
    return f"https://raw.githubusercontent.com/cllsenoll/F4-HESAP/main/{encoded_name}.png"

# ==========================================
# MÜŞTERİ - PERSONEL EŞLEŞTİRME SÖZLÜĞÜ (TAM LİSTE)
# ==========================================
MUSTERI_PERSONEL_MAP = {
    "KÜBRA AYDEMİR": "AHMET BERKAN ÖKSÜZ", "SERKAN KUYUMCU": "AHMET BERKAN ÖKSÜZ",
    "AKSUN AĞAÇ AMBALAJ": "ALATTİN CEBECİ", "ARTEA DIŞ TİCARET": "ALATTİN CEBECİ",
    "BURCU DÜREN": "BURCU DÜREN", "ALTINSOY MADENCİLİK": "CELAL ŞENOL",
    "HASAN SAĞLAM": "HASAN SAĞLAM", "SERGEN GÖRÜROĞLU": "SERGEN GÖRÜROĞLU", "SUAT ARI": "SUAT ARI"
    # Not: Sözlük tamlığı için önceki tam listeyi burada koruyunuz.
}

# ==========================================
# CSS VE TEMA
# ==========================================
custom_css = """
<style>
    .stApp { background-color: #0B192C !important; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #1E3E62 !important; }
    
    /* Geliştirici Kartı - Turuncu */
    .dev-card { 
        background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); 
        border-radius: 12px; padding: 12px; margin-bottom: 15px; 
        border: 1px solid #FFA200; box-shadow: 0 6px 0 #9E2A2B; color: #FFFFFF;
    }

    /* Sarı Upload Butonu */
    [data-testid="stFileUploader"] section { background: #FFB703 !important; border: 2px dashed #FB8500 !important; }
    [data-testid="stFileUploader"] button { background: #FB8500 !important; color: white !important; font-weight: bold !important; }

    .kasa-box { background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border-radius: 14px; padding: 20px; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# YARDIMCI FONKSİYONLAR
# ==========================================
def clean_string(text):
    text = str(text).upper().strip()
    return re.sub(r'[^A-Z0-9]', '', text.replace('İ','I').replace('Ş','S').replace('Ğ','G').replace('Ü','U').replace('Ö','O').replace('Ç','C'))

def parse_turkish_float(val):
    try:
        return float(str(val).replace(' ','').replace('₺','').replace('TL','').replace('.','').replace(',','.'))
    except: return 0.0

# ==========================================
# F4 İŞLEME MOTORU (GERİ YÜKLENDİ)
# ==========================================
def process_f4_payment_data(df):
    # Sütunları temizle
    df.columns = df.columns.astype(str).str.strip()
    processed_rows = []
    
    for _, row in df.iterrows():
        # Müşteri ve Tutar sütunlarını tahmin et
        m_adi = str(row[0]) 
        borc = parse_turkish_float(row[1] if len(row) > 1 else 0)
        
        if borc == 0: continue
        
        # Personel atama mantığı
        personel = "ATANMAMIŞ"
        for musteri, per in MUSTERI_PERSONEL_MAP.items():
            if clean_string(musteri) in clean_string(m_adi):
                personel = per
                break
        
        processed_rows.append({"Müşteri Adı": m_adi, "Fatura Borcu": borc, "Personel": personel})
    
    return pd.DataFrame(processed_rows)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown(f"""
    <div class="dev-card">
        <small style="color: #FFFFFF;">Geliştirici:</small><br>
        <strong style="color: #FFFFFF; font-size: 15px;">{KULLANICI_ISIM}</strong><br>
        <span style="color: #FFFFFF; font-weight: bold;">{KULLANICI_GOREV}</span>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Rapor Yükle", type=['csv', 'xlsx'])
    if st.button("💰 HESAP"): st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"): st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# ==========================================
# ANA İŞLEYİŞ
# ==========================================
if uploaded_file:
    df = pd.read_excel(uploaded_file) if 'xls' in uploaded_file.name else pd.read_csv(uploaded_file)
    if "F4" in uploaded_file.name.upper() or "BORÇ" in str(df.columns):
        st.session_state.f4_df = process_f4_payment_data(df)
    else:
        st.session_state.account_df = df # Hesap işlemleri...

if st.session_state.active_tab == "F4 ÖDEME LİSTESİ" and st.session_state.f4_df is not None:
    st.title("📋 F4 Ödeme Listesi")
    edited_df = st.data_editor(st.session_state.f4_df, use_container_width=True)
    st.session_state.f4_df = edited_df
