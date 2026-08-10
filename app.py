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
KULLANICI_GOREV = "Şube Şefi"

# GİTHUB PERSONEL FOTOĞRAF HARİTASI
def get_github_avatar(personel_adi):
    clean_name = str(personel_adi).strip()
    encoded_name = urllib.parse.quote(clean_name)
    return f"https://raw.githubusercontent.com/cllsenoll/F4-HESAP/main/{encoded_name}.png"

# MÜŞTERİ - PERSONEL EŞLEŞTİRME SÖZLÜĞÜ (Kısaltıldı, kendi listenizi korur)
MUSTERI_PERSONEL_MAP = {
    "KÜBRA AYDEMİR": "AHMET BERKAN ÖKSÜZ",
    "SERKAN KUYUMCU": "AHMET BERKAN ÖKSÜZ",
    "ALTINSOY MADENCİLİKVE TİCARET A.Ş.": "CELAL ŞENOL",
    "ENDER DURSAK": "CELAL ŞENOL",
    "KAPLANLAR SOĞUTMA SAN.VE TİC.AŞ.": "CELAL ŞENOL",
    "SERGEN GÖRÜROĞLU": "CELAL ŞENOL"
    # ... diğer eşleşmeleriniz burada kalmaya devam eder
}

# CSS
st.markdown("""
<style>
    .notranslate { translate: no !important; }
    .stApp { background-color: #070E1E; color: #FFFFFF; }
    h1, h2, h3, h4, h5, h6, p, span, label { color: #FFFFFF !important; font-family: sans-serif; }
    [data-testid="stSidebar"] { background-color: #0B172E !important; }
    .kasa-box { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; padding: 20px; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# YARDIMCI FONKSİYONLAR
def clean_string(text):
    text = str(text).upper().strip()
    replacements = {'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for s, r in replacements.items(): text = text.replace(s, r)
    return re.sub(r'[^A-Z0-9]', '', text)

def parse_turkish_float(val):
    try:
        s = str(val).replace(' ', '').replace('₺', '').replace('TL', '').replace(',', '.')
        return float(s)
    except: return 0.0

def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    encodings = ['cp1254', 'iso-8859-9', 'utf-8']
    for enc in encodings:
        try: return pd.read_csv(io.BytesIO(file_bytes), sep=None, encoding=enc, engine='python')
        except: continue
    return pd.read_excel(io.BytesIO(file_bytes))

# --- ANA MANTIKSAL DÖNGÜ ---
# (process_personnel_account_data ve process_f4_payment_data fonksiyonlarınız buraya gelecek)

# TAB 1: HESAP
if st.session_state.active_tab == "HESAP":
    if st.session_state.account_df is not None:
        current_df = st.session_state.hesap_df.copy()
        
        temp_hesap_toplam = sum(float(row["Nakit Ft Tutarı Topl"]) + float(row["Nakit Ödeme Tutarı Topl"]) - st.session_state.get(f"banka_{idx+1}", float(row["Banka/ATM"])) for idx, row in current_df.iterrows())

        def update_kasa(): st.session_state.kasa_miktari = st.session_state.ust_kasa_input

        top_col1, top_col2 = st.columns([2.5, 2.5])
        with top_col1: st.title("📋 Günlük Personel Hesap Takip")
        with top_col2:
            st.number_input("🏦 MANÜEL KASA GİR", value=float(st.session_state.kasa_miktari), key="ust_kasa_input", on_change=update_kasa)
            
            GuncelKasa = float(st.session_state.ust_kasa_input if "ust_kasa_input" in st.session_state else st.session_state.kasa_miktari)
            fark = GuncelKasa - temp_hesap_toplam
            
            # --- REVİZE EDİLMİŞ MANTIK ---
            if GuncelKasa > temp_hesap_toplam:
                durum_metni = f"🔴 KASA AÇIK: {abs(fark):,.2f} ₺"
                renk_kodu = "#FF5252"
            elif GuncelKasa < temp_hesap_toplam:
                durum_metni = f"🟢 KASA FAZLA: {abs(fark):,.2f} ₺"
                renk_kodu = "#4CAF50"
            else:
                durum_metni = "✅ KASA TAM (0.00 ₺)"
                renk_kodu = "#FFFFFF"
            
            st.markdown(f"<div style='text-align: center; font-weight: bold; font-size: 18px; color: {renk_kodu};'>{durum_metni}</div>", unsafe_allow_html=True)
            
        # ... (Geri kalan hesap döngüsü ve tablo arayüzü aynı şekilde devam eder)
