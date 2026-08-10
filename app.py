# Anlık Kasa Durumu Hesaplama
        GuncelKasa = float(st.session_state.ust_kasa_input if "ust_kasa_input" in st.session_state else st.session_state.kasa_miktari)
        fark = GuncelKasa - temp_hesap_toplam
        
        # MANTIK REVİZYONU: 
        # Kasa > Toplam ise -> AÇIK (Kırmızı)
        # Kasa < Toplam ise -> FAZLA (Gerektiği gibi)
        if GuncelKasa > temp_hesap_toplam:
            durum_metni = f"🔴 KASA AÇIK: {abs(fark):,.2f} ₺"
            renk_kodu = "#FF5252" # Kırmızı
        elif GuncelKasa < temp_hesap_toplam:
            durum_metni = f"🟢 KASA FAZLA: {abs(fark):,.2f} ₺"
            renk_kodu = "#4CAF50" # Yeşil
        else:
            durum_metni = "✅ KASA TAM (0.00 ₺)"
            renk_kodu = "#FFFFFF"
        
        st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: bold; font-size: 15px; color: {renk_kodu};'>{durum_metni}</div>", unsafe_allow_html=True)
