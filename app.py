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
# MÜŞTERİ - PERSONEL EŞLEŞTİRME SÖZLÜĞÜ
# ==========================================
MUSTERI_PERSONEL_MAP = {
    "KÜBRA AYDEMİR": "AHMET BERKAN ÖKSÜZ",
    "SERKAN KUYUMCU": "AHMET BERKAN ÖKSÜZ",
    "AKSUN AĞAÇ AMBALAJ KERESTE SAN. TİC.LTD.ŞTİ": "ALATTİN CEBECİ",
    "ARTEA DIŞ TİCARET MAKİNA SANAYİ LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "BAYAGRO TARIM İLAÇLARI SANAYİ VE TİCARETLTD. ŞTİ.": "ALATTİN CEBECİ",
    "BEREKET İLAÇ KOZMETİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "BURMOD TEKSTİL SAN.TİC.A.Ş.-BURSA ŞB.": "ALATTİN CEBECİ",
    "DEMİRCİOĞLU ŞASE ENDÜSTRİYEL YAĞ OTOMOTİV TEKSTİL GIDA İNŞAAT SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
    "EDDA MAKİNE AMBALAJ NAKLİYE İNŞAAT KİMYA SANAYİ TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "FLY MOBİLYA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "KOLİSAN AMBALAJ SANAYİ VE TİCARET A.Ş.": "ALATTİN CEBECİ",
    "M-BEND METAL ÇELİK MAKİNA İNŞAAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "ALATTİN CEBECİ",
    "MAVİFORM METAL KALIPFİKSTÜR VE APARAT SAN.VE TİC.LTD": "ALATTİN CEBECİ",
    "MERZE MOBİLYA TASARIM İNŞAAT SANAYİ TİCARET ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "MNC BİTKİSEL VE SAĞLIK ÜRÜNLERİ REKLAM VE ORGANİZASYON BİLİŞİM TEKNOLOJİLERİ İNŞAAT SAN.TİC.LTD.ŞTİ.": "ALATTİN CEBECİ",
    "SOMBURSA BAĞLANTI ELEMANLARI TİCARET VESAN.VE A.Ş.": "ALATTİN CEBECİ",
    "ÖZBEYAZ DIŞ TİCARET TAŞIMACILIK ANONİM ŞİRKETİ": "ALATTİN CEBECİ",
    "ALPER ŞEN": "BURCU DÜREN",
    "ALSTOM RAYLI SİSTEM SANAYİ ANONİM ŞİRKETİ": "BURCU DÜREN",
    "AMPHENOL TURKEY BAĞLANTI ÇÖZÜMLERİ LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "BAŞATLAR ORMAN ÜRÜNLERİ VE AMBALAJ SAN.TİC.LTD.ŞTİ.": "BURCU DÜREN",
    "D.K.C TEKNİK KAPLAMA APRE TEKSTİL KONFEKSİYON SERVİS TAŞIMACILIĞI SAN.VE TİC.LTD.ŞTİ.": "BURCU DÜREN",
    "DEBSA TASARIM KONFEKSİYON TEKSTİL SANAYİ TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "DEVSAN ENDÜSTRİYEL OTOMASYON MAKİNA SANAYİ VE TİCARET A.Ş.": "BURCU DÜREN",
    "DOĞANYİĞİTLER ORGANİK GIDA SANAYİ TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "DİLAN YILDIRIM - OLİNA BUTİK": "BURCU DÜREN",
    "ESAUTOMOTION MEKATRONİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "GENÇ GÖZDE TARIM MAKİNALARI SANAYİ VE TİC.LTD.ŞTİ.": "BURCU DÜREN",
    "GÜMÜŞ ARSLAN GENEL MAKİNE İMALATI ENERJİ VE ISI SİSTEMLERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "HMT MAKİNA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "JACQUARD FASHİON KONFEKSİYON TEKSTİL SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "KCL LOJİSTİK OTOMOTİV SANAYİ TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "MATAY OTOMOTİV YAN SANAYİ VE TİCARET A .Ş.": "BURCU DÜREN",
    "MİNTEKS TEKSTİL SAN VE TİC. LTD.ŞTİ. İŞLETME ADI:MİNTEKS": "BURCU DÜREN",
    "MS MOTION OTOMOTİV ANONİM ŞİRKETİ": "BURCU DÜREN",
    "NOBEL TEKNİK OTO YANSANAYİ VE TİCARET A.Ş.": "BURCU DÜREN",
    "ORCA HOME TEKSTİL İTHALAT İHRACATSANAYİ VE TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "OTEKSO MÜHENDİSLİK TASARIM MAKİNE SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "PROLİFT ASANSÖR SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "S.S.MARMARA ZEYTİN TARIM SAT.KOOP.BİR.MARMARABİRLİK": "BURCU DÜREN",
    "T-BİYOTEKNOLOJİ LABORATUVAR ESTETİK MEDİKAL KOZMETİK SANAYİVE TİCARET LTD.ŞTİ.": "BURCU DÜREN",
    "UĞURLU FİNİSAJ SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "BURCU DÜREN",
    "VARNA DERİ SANAYİ VE TİCARET A.Ş.": "BURCU DÜREN",
    "VETABİL GIDA TARIM HAYVANCILIK LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "ÖZGÜR ULUS - MARANGOZ": "BURCU DÜREN",
    "İLK-SEZ ENDÜSTRİYEL OTOMASYON SİSTEMLERİ ELEKTRİK ELEKTRONİK MAKİNA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "BURCU DÜREN",
    "ALTINSOY MADENCİLİKVE TİCARET A.Ş.": "CELAL ŞENOL",
    "ENDER DURSAK": "CELAL ŞENOL",
    "KAPLANLAR SOĞUTMA SAN.VE TİC.AŞ.": "CELAL ŞENOL",
    "NARVİN TEKSTİL EMLAK KOZMETİK SOSYAL MEDYA İHRACAT İTHALAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "SELFİE TARIMSAL TEDARİK SERACILIK DEPOCULUK DANIŞMANLIK SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "CELAL ŞENOL",
    "SERGEN GÖRÜROĞLU": "CELAL ŞENOL",
    "ARMENDUS OPERATÖR KOL VE PANO SİSTEMLERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "BAROMAK MAKİNE SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "BİLEKLER İNŞAAT MAKİNALARI SANAYİ VETİCARET LTD.ŞTİ.": "HASAN SAĞLAM",
    "BURKON MOBİLYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "DICHERSEAL ELASTOMER TEKNOLOJİLERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "DİGİTORİUM ELEKTRONİK TEKNOLOJİLERİ ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA KABLOSİSTEMLERİ SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA GRUP MÜHENDİSLİK ELEKTRİK TAAHHÜT MEKANİK PANO İMALAT İTHALAT İHRACAT SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ELECTRA PROJE ELEKTRİK MÜHENDİSLİK TAAHHÜT İNŞAAT ARAÇ KİRALAMA İTHALAT İHRACAT VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "F.S.K.MAKİNE İMALATTAAH.VE GIDA TEKN.SAN.T.LTD.ŞTİ.": "HASAN SAĞLAM",
    "IPM GALVANO YÜZEY KAPLAMA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "LİGNUM AĞAÇ MAKİNELERİ SANAYİ TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "TEMPOLİFT ASANSÖR ELEKTRİK ELEKTRONİK SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "HASAN SAĞLAM",
    "TURKAUTO MOTORLU ARAÇLAR SANAYİ VE TİCARET LİMİTED ŞİRKETİ.": "HASAN SAĞLAM",
    "VİYA OTOMOTİV CAM TURİZM DENİZCİLİK SANAYİ VE TİCARET LTD. ŞTİ.": "HASAN SAĞLAM",
    "YSL OTOMOTİV YAN SANAYİ VE TİCARET ANONİM ŞİRKETİ": "HASAN SAĞLAM",
    "ÖZGÖZDE OTOMOTİV İNŞAAT İŞ MAKİNALARI PETROL NAKLİYE VE TURİZM HİZMETLERİ SANAYİ TİCARET A.Ş.": "HASAN SAĞLAM",
    "ACH DIŞ TİCARET SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "AKEL DERİ TEKS.SAN.VE DIŞ TİC.LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "AYDEMİR DERİ SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "BURSA DERİ İHTİSAS VE KARMA ORGANİZE SANAYİ BÖLGESİ": "SERGEN GÖRÜROĞLU",
    "BURSA JELATİN GIDA SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "CİVAN GERİ DÖNÜŞÜM İZOLASYON PLASTİK METAL,İNŞAAT TAAH.SAN.VE TİC.LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "EMRE DERELİ - DERELİ MARİNE": "SERGEN GÖRÜROĞLU",
    "ERBA FİNİSAJ DERİ SANAYİ VE TİCARET LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "GESU ARITMA SİSTEMLERİ SANAYİ VE TİCARET LTD.ŞTİ.": "SERGEN GÖRÜROĞLU",
    "LAS-SAN LASTİK PLASTİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MECANICA CNC MAKİNE VE SERVİS LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MET-RİN DERİ MAKİNELERİ VE METAL SANAYİ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MORKİM KİMYA İNŞAAT İTHALAT İHRACAT SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "MURSAN FİBERGLASS VE DENİZ ARAÇLARI TURİZM SANAYİ TİCARET PAZARLAMA LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "NOVMA KİMYA SANAYİ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "VAKETA DERİCİLİK SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "YILDIZ GRUBU DERİ KİMYA İNŞAAT TARIM SANAYİ VE DIŞ TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "İDEA ENDÜSTRİYEL KİMYA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "İNVENTA GIDA SANAYİ VE TİCARET LİMİTED ŞİRKETİ": "SERGEN GÖRÜROĞLU",
    "ERKAN DEMİRCAN": "SUAT ARI",
    "NUR ALUÇLUOĞLU - NUR TERZİ": "SUAT ARI",
    "YERLİYURT MARİN DENİZ ARAÇ KAB.TUR.SVE P.LTD.ŞTİ.": "SUAT ARI",
    "ÖZBAYRAK KIZAK KORUMA SİSTEMLERİ ENDÜSTRİ MAKİNE SANAYİ VE TİCARET ANONİM ŞİRKETİ": "SUAT ARI"
}

# ==========================================
# CSS VE YENİ TEMA KODLARI
# ==========================================
custom_css = """
<style>
    .notranslate {
        translate: no !important;
    }
    .stApp {
        background-color: #0B192C !important;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #FFFFFF !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    [data-testid="stSidebar"] {
        background-color: #1E3E62 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    [data-testid="stSidebar"] div.stButton > button, div.stButton > button {
        width: 100% !important;
        height: 48px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #00B4D8 0%, #0077B6 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid #90E0EF !important;
        box-shadow: 0 6px 0 #03045E, 0 8px 10px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(0);
        transition: all 0.1s ease;
        margin-bottom: 10px !important;
        text-align: left !important;
        padding-left: 15px !important;
    }
    [data-testid="stSidebar"] div.stButton > button:hover, div.stButton > button:hover {
        background: linear-gradient(135deg, #48CAE4 0%, #00B4D8 100%) !important;
        box-shadow: 0 4px 0 #03045E, 0 6px 8px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(2px);
    }
    [data-testid="stSidebar"] div.stButton > button:active, div.stButton > button:active {
        box-shadow: 0 0 0 #03045E, 0 2px 4px rgba(0, 0, 0, 0.4) !important;
        transform: translateY(6px);
    }

    /* UPLOAD (Dosya Yükleme) Butonu Sarı Tasarımı */
    [data-testid="stFileUploader"] section {
        background: linear-gradient(135deg, #FFD166 0%, #FFB703) !important;
        border: 2px dashed #FB8500 !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] section * {
        color: #000000 !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #FFB703 0%, #FB8500) !important;
        color: #FFFFFF !important;
        border: 1px solid #FFFFFF !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 0 #9E2A2B, 0 6px 8px rgba(0,0,0,0.3) !important;
    }

    .kasa-box {
        background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%);
        border: 2px solid #FFA200;
        border-radius: 14px;
        padding: 20px;
        margin-top: 20px;
        box-shadow: 0 6px 12px rgba(255, 123, 0, 0.3);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

def clean_string(text):
    if pd.isna(text) or not text: return ""
    text = str(text).upper().strip()
    replacements = {'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for search, replace in replacements.items(): text = text.replace(search, replace)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def parse_turkish_float(val):
    if pd.isna(val) or val is None: return 0.0
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip()
    if not s or s.upper() in ['NAN', 'NONE', '-', '0', '0.0', '0,0']: return 0.0
    s = s.replace(' ', '').replace('₺', '').replace('TL', '')
    if ',' in s and '.' in s: s = s.replace('.', '').replace(',', '.')
    elif ',' in s: s = s.replace(',', '.')
    try: return float(s)
    except: return 0.0

def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    for enc in ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']:
        for sep in [';', ',', '\t', None]:
            try:
                engine = 'python' if sep is None else None
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, engine=engine, on_bad_lines='skip')
                if len(df.columns) > 1: return df
            except: continue
    try: return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except: pass
    raise Exception("Dosya yapısı çözümlenemedi.")

def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKİT" in row_str or "FT" in row_str or "ÖDEME" in row_str:
            header_idx = idx
            break
    df.columns = df.iloc[header_idx].astype(str).str.strip()
    df = df.iloc[header_idx + 1:].reset_index(drop=True)
    
    p_col, ft_col, odeme_col = None, None, None
    for col in df.columns:
        c = str(col).upper()
        if "PERSONEL" in c or "AD" in c or "KURYE" in c: p_col = col
        elif ("FT" in c or "FATURA" in c) and "AD" not in c: ft_col = col
        elif "ÖDEME" in c or "ODEME" in c: odeme_col = col

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p = str(row[p_col]).strip() if p_col else ""
        c_p = clean_string(raw_p)
        if not c_p or c_p in ["NAN", "NONE", "TOTAL", "TOPLAM"]: continue
        parsed_rows.append({
            "Raw_Name": raw_p,
            "Clean_Name": c_p,
            "Nakit Ft Tutarı Topl": parse_turkish_float(row[ft_col]) if ft_col else 0.0,
            "Nakit Ödeme Tutarı Topl": parse_turkish_float(row[odeme_col]) if odeme_col else 0.0
        })
    return pd.DataFrame(parsed_rows)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="notranslate" style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; color: #FFFFFF;">Yurtiçi Kargo</h2>
        <h4 style="margin: 0; color: #00B4D8;">Görükle Acente KOYS</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    # TURUNCU KART, BEYAZ YAZILAR
    st.markdown(f"""
    <div class="notranslate" style="background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #FFA200; box-shadow: 0 6px 0 #9E2A2B, 0 8px 12px rgba(0,0,0,0.3);">
        <small style="color: #FFFFFF; font-weight: 600;">Geliştirici:</small><br>
        <strong style="color: #FFFFFF; font-size: 15px;">{KULLANICI_ISIM}</strong><br>
        <span style="color: #FFFFFF; font-size: 13px; font-weight: bold;">{KULLANICI_GOREV}</span>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=['csv', 'xlsx', 'xls', 'html'])
    
    if st.button("💰 HESAP"): st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"): st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# (Geri kalan logic aynı şekilde devam ettirilir)
if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        st.session_state.raw_df = raw_df
    except Exception as e:
        st.error(f"❌ Dosya Hatası: {e}")

if st.session_state.active_tab == "HESAP":
    st.title("📋 Günlük Personel Hesap Takip Paneli")
    st.info("İşlem için dosya yükleyiniz.")
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme ve Personel Tahsilat Listesi")
