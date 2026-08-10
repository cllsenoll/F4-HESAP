import streamlit as st
import pandas as pd
import io
import re
import urllib.parse

# 1. SAYFA YAPILANDIRMASI
st.set_page_config(page_title="Görükle Acente - Hesap & F4 Paneli", page_icon="💰", layout="wide")

# 2. OTURUM DURUMU
if 'active_tab' not in st.session_state: st.session_state.active_tab = "HESAP"
if 'account_df' not in st.session_state: st.session_state.account_df = None
if 'hesap_df' not in st.session_state: st.session_state.hesap_df = None
if 'kasa_miktari' not in st.session_state: st.session_state.kasa_miktari = 0.0
if 'f4_df' not in st.session_state: st.session_state.f4_df = None

# ... [BURAYA ÖNCEKİ KODDAKİ MUSTERI_PERSONEL_MAP VE YARDIMCI FONKSİYONLARINI (clean_string, smart_read_file vb.) EKLİYORUZ] ...
# (Not: Kodunuzun en başındaki o fonksiyonları koruduğunuzdan emin olun)

# --- TAB 1: HESAP PANELİ (REVİZE EDİLMİŞ KISIM) ---
if st.session_state.active_tab == "HESAP":
    if st.session_state.account_df is not None:
        current_df = st.session_state.hesap_df.copy()
        
        # Toplam hesaplama
        temp_hesap_toplam = 0.0
        for idx, row in current_df.iterrows():
            ft = float(row["Nakit Ft Tutarı Topl"])
            odeme = float(row["Nakit Ödeme Tutarı Topl"])
            banka = st.session_state.get(f"banka_{idx+1}", float(row["Banka/ATM"]))
            temp_hesap_toplam += (ft + odeme - banka)

        # Başlık ve Kasa Girişi
        top_col1, top_col2 = st.columns([2, 1])
        with top_col1: st.title("📋 Günlük Personel Hesap Takip")
        with top_col2:
            st.number_input("🏦 MANÜEL KASA GİR", value=float(st.session_state.kasa_miktari), key="ust_kasa_input")
            GuncelKasa = float(st.session_state.ust_kasa_input)
            
            # REVİZE EDİLMİŞ MANTIK
            fark = GuncelKasa - temp_hesap_toplam
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

        # ... (Geri kalan satır döngüleri ve tablo oluşturma kısmı olduğu gibi kalacak)
