import streamlit as st
import pandas as pd
import io
import re
import urllib.parse
import streamlit.components.v1 as components
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'DejaVuSans-Bold.ttf'))
    FONT_NAME = 'DejaVuSans'
    FONT_NAME_BOLD = 'DejaVuSans-Bold'
except:
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'

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

PERSONEL_LISTESI = [
    "HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN",
    "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ",
    "SUAT ARI", "SERGEN GÖRÜROĞLU", "CELAL ŞENOL", "ATANMAMIŞ"
]

# ==========================================
# CSS VE TEMA KODLARI
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

# ==========================================
# TÜRKÇE TEMİZLEME VE PARS FONKSİYONLARI
# ==========================================
def clean_string(text):
    if pd.isna(text) or not text:
        return ""
    text = str(text).upper().strip()
    replacements = {'İ': 'I', 'I': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C'}
    for search, replace in replacements.items():
        text = text.replace(search, replace)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

def parse_turkish_float(val):
    if pd.isna(val) or val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s or s.upper() in ['NAN', 'NONE', '-', '0', '0.0', '0,0']:
        return 0.0
    s = s.replace(' ', '').replace('₺', '').replace('TL', '')
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except:
        return 0.0

# ==========================================
# GÜÇLÜ DOSYA OKUMA MOTORU
# ==========================================
def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    encodings = ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']
    separators = [';', ',', '\t', None]

    for enc in encodings:
        for sep in separators:
            try:
                engine_type = 'python' if sep is None else None
                df = pd.read_csv(io.BytesIO(file_bytes), sep=sep, encoding=enc, engine=engine_type, on_bad_lines='skip')
                if df is not None and len(df.columns) > 1 and len(df) > 0:
                    return df
            except Exception:
                continue

    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl')
    except Exception:
        pass

    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine='xlrd')
    except Exception:
        pass

    for enc in ['utf-8', 'cp1254', 'latin1']:
        try:
            dfs = pd.read_html(io.BytesIO(file_bytes), encoding=enc)
            if dfs and len(dfs) > 0:
                return dfs[0]
        except Exception:
            continue

    raise Exception("Dosya yapısı çözümlenemedi. Lütfen dosyanın bozuk olmadığını kontrol edin.")

# ==========================================
# PERSONEL HESAP ALIMI EKRANI PARSER
# ==========================================
def process_personnel_account_data(df):
    header_idx = 0
    for idx, row in df.iterrows():
        row_str = " ".join([str(val).upper() for val in row.values])
        if "PERSONEL" in row_str or "NAKİT" in row_str or "FT" in row_str or "ÖDEME" in row_str:
            header_idx = idx
            break
            
    if header_idx > 0:
        df.columns = df.iloc[header_idx].astype(str).str.strip()
        df = df.iloc[header_idx + 1:].reset_index(drop=True)
    else:
        df.columns = df.columns.astype(str).str.strip()

    cols_to_drop = [c for c in df.columns if "AÇIKLAMA" in str(c).upper() or "ACIKLAMA" in str(c).upper()]
    df = df.drop(columns=cols_to_drop, errors='ignore')

    p_col, ft_col, odeme_col = None, None, None

    for col in df.columns:
        c_upper = str(col).upper()
        if ("PERSONEL" in c_upper or "AD" in c_upper or "KURYE" in c_upper) and not p_col:
            p_col = col
        elif (("FT" in c_upper or "FATURA" in c_upper) and not ("AD" in c_upper or "ADET" in c_upper)) and not ft_col:
            ft_col = col
        elif ("ÖDEME" in c_upper or "ODEME" in c_upper) and not odeme_col:
            odeme_col = col

    cols_list = list(df.columns)
    if not p_col and len(cols_list) > 0: p_col = cols_list[0]
    if not ft_col and len(cols_list) > 1: ft_col = cols_list[1]
    if not odeme_col and len(cols_list) > 2: odeme_col = cols_list[2]

    parsed_rows = []
    for _, row in df.iterrows():
        raw_p_name = str(row[p_col]).strip() if p_col else ""
        c_p_name = clean_string(raw_p_name)
        
        if not c_p_name or c_p_name in ["NAN", "NONE", "TOTAL", "TOPLAM", "GENELTOPLAM"]:
            continue
            
        ft_val = parse_turkish_float(row[ft_col]) if ft_col else 0.0
        odeme_val = parse_turkish_float(row[odeme_col]) if odeme_col else 0.0

        parsed_rows.append({
            "Raw_Name": raw_p_name,
            "Clean_Name": c_p_name,
            "Nakit Ft Tutarı Topl": ft_val,
            "Nakit Ödeme Tutarı Topl": odeme_val,
            "Banka/ATM": 0.0
        })

    temp_df = pd.DataFrame(parsed_rows)

    priority_list = [
        "HATİCE KÜBRA IŞIK", "ALATTİN CEBECİ", "BURCU DÜREN",
        "AHMET BERKAN ÖKSÜZ", "HASAN SAĞLAM", "MEHMET KAYMAZ",
        "SUAT ARI", "SERGEN GÖRÜROĞLU", "CELAL ŞENOL"
    ]

    final_rows = []
    processed_clean_names = set()

    for fixed_name in priority_list:
        clean_fixed = clean_string(fixed_name)
        matched_row = None
        
        if not temp_df.empty:
            exact_match = temp_df[temp_df["Clean_Name"] == clean_fixed]
            if not exact_match.empty:
                matched_row = exact_match.iloc[0]
            else:
                contains_match = temp_df[temp_df["Clean_Name"].apply(lambda x: clean_fixed in x or x in clean_fixed)]
                if not contains_match.empty:
                    matched_row = contains_match.iloc[0]

        if matched_row is not None:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": float(matched_row["Nakit Ft Tutarı Topl"]),
                "Nakit Ödeme Tutarı Topl": float(matched_row["Nakit Ödeme Tutarı Topl"]),
                "Banka/ATM": 0.0,
            })
            processed_clean_names.add(matched_row["Clean_Name"])
        else:
            final_rows.append({
                "Personel Adı": fixed_name,
                "Nakit Ft Tutarı Topl": 0.0,
                "Nakit Ödeme Tutarı Topl": 0.0,
                "Banka/ATM": 0.0,
            })

    if not temp_df.empty:
        for _, row in temp_df.iterrows():
            c_name = row["Clean_Name"]
            if c_name not in processed_clean_names:
                final_rows.append({
                    "Personel Adı": row["Raw_Name"],
                    "Nakit Ft Tutarı Topl": float(row["Nakit Ft Tutarı Topl"]),
                    "Nakit Ödeme Tutarı Topl": float(row["Nakit Ödeme Tutarı Topl"]),
                    "Banka/ATM": 0.0,
                })
                processed_clean_names.add(c_name)

    result_df = pd.DataFrame(final_rows)
    result_df["Hesap"] = result_df["Nakit Ft Tutarı Topl"] + result_df["Nakit Ödeme Tutarı Topl"] - result_df["Banka/ATM"]
    result_df["İşlem"] = False

    result_df.reset_index(drop=True, inplace=True)
    result_df.index = range(1, len(result_df) + 1)

    return result_df[["Personel Adı", "Nakit Ft Tutarı Topl", "Nakit Ödeme Tutarı Topl", "Banka/ATM", "Hesap", "İşlem"]]

# ==========================================
# F4 ÖDEME LİSTESİ İŞLEME MOTORU
# ==========================================
def process_f4_payment_data(df):
    df.columns = df.columns.astype(str).str.strip()
    
    musteri_col, borc_col, aciklama_col = None, None, None
    for col in df.columns:
        c_upper = str(col).upper()
        if ("MÜŞTERİ" in c_upper or "MUSTERI" in c_upper or "FIRMA" in c_upper or "UNVAN" in c_upper) and not musteri_col:
            musteri_col = col
        elif ("BORÇ" in c_upper or "BORC" in c_upper or "BAKİYE" in c_upper or "BAKIYE" in c_upper or "TUTAR" in c_upper) and not borc_col:
            borc_col = col
        elif "AÇIKLAMA" in c_upper or "ACIKLAMA" in c_upper:
            aciklama_col = col

    cols_list = list(df.columns)
    if not musteri_col and len(cols_list) > 0: musteri_col = cols_list[0]
    if not borc_col and len(cols_list) > 1: borc_col = cols_list[1]
    if not aciklama_col and len(cols_list) > 2: aciklama_col = cols_list[2]

    processed_rows = []
    for _, row in df.iterrows():
        m_adi = str(row[aciklama_col]).strip() if aciklama_col and not pd.isna(row[aciklama_col]) else ""
        if not m_adi or m_adi.upper() in ["NAN", "NONE", "TOPLAM", "TOTAL"]:
            m_adi = str(row[musteri_col]).strip() if musteri_col else ""
            
        if not m_adi or m_adi.upper() in ["NAN", "NONE", "TOPLAM", "TOTAL"]:
            continue
            
        borc_val = parse_turkish_float(row[borc_col]) if borc_col else 0.0
        
        if borc_val == 0.0:
            continue

        assigned_personel = "ATANMAMIŞ"
        m_upper = m_adi.upper()
        m_clean = clean_string(m_adi)

        if m_upper in MUSTERI_PERSONEL_MAP:
            assigned_personel = MUSTERI_PERSONEL_MAP[m_upper]
        else:
            found = False
            for k, v in MUSTERI_PERSONEL_MAP.items():
                if clean_string(k) == m_clean:
                    assigned_personel = v
                    found = True
                    break
            
            if not found:
                for k, v in MUSTERI_PERSONEL_MAP.items():
                    k_clean = clean_string(k)
                    if k_clean and (k_clean in m_clean or m_clean in k_clean):
                        assigned_personel = v
                        break

        processed_rows.append({
            "Müşteri Adı": m_adi,
            "Fatura Borcu": borc_val,
            "Açıklama": "",
            "Personel": assigned_personel
        })

    res_df = pd.DataFrame(processed_rows)
    if not res_df.empty:
        res_df.reset_index(drop=True, inplace=True)
        res_df.index = range(1, len(res_df) + 1)
    return res_df

# ==========================================
# PDF OLUŞTURMA MOTORU (REPORTLAB)
# ==========================================
def generate_personnel_pdf(personel_adi, sub_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=FONT_NAME_BOLD,
        fontSize=16,
        textColor=colors.HexColor('#0B192C'),
        alignment=1,
        spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=20
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        textColor=colors.HexColor('#000000')
    )
    cell_bold_style = ParagraphStyle(
        'CellBoldStyle',
        parent=styles['Normal'],
        fontName=FONT_NAME_BOLD,
        fontSize=9,
        textColor=colors.HexColor('#000000')
    )

    elements.append(Paragraph(f"YURTİÇİ KARGO GÖRÜKLE ACENTE", title_style))
    elements.append(Paragraph(f"Sorumlu Personel Tahsilat Listesi: <b>{personel_adi}</b>", subtitle_style))

    toplam_tutar = sub_df["Fatura Borcu"].sum() if not sub_df.empty else 0.0

    table_data = [[Paragraph("<b>Müşteri / Firma Adı</b>", cell_bold_style), Paragraph("<b>Fatura Borcu (₺)</b>", cell_bold_style)]]

    for _, row in sub_df.iterrows():
        table_data.append([
            Paragraph(str(row["Müşteri Adı"]), cell_style),
            Paragraph(f"{row['Fatura Borcu']:,.2f} ₺", cell_style)
        ])

    table_data.append([
        Paragraph("<b>TOPLAM TUTAR</b>", cell_bold_style),
        Paragraph(f"<b>{toplam_tutar:,.2f} ₺</b>", cell_bold_style)
    ])

    col_widths = [400, 135]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00B4D8')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#CCCCCC')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E2E8F0')),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#0B192C')),
    ]))

    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# ==========================================
# SIDEBAR VE GEZİNTİ MENÜSÜ
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="notranslate" style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; color: #FFFFFF;">Yurtiçi Kargo</h2>
        <h4 style="margin: 0; color: #00B4D8;">Görükle Acente KOYS</h4>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="notranslate" style="background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border-radius: 12px; padding: 12px; margin-bottom: 15px; border: 1px solid #FFA200; box-shadow: 0 6px 0 #9E2A2B, 0 8px 12px rgba(0,0,0,0.3);">
        <small style="color: #FFFFFF; font-weight: 600;">Geliştirici:</small><br>
        <strong style="color: #FFFFFF; font-size: 15px;">{KULLANICI_ISIM}</strong><br>
        <span style="color: #FFFFFF; font-size: 13px; font-weight: bold;">{KULLANICI_GOREV}</span>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=['csv', 'xlsx', 'xls', 'html'])
    
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("💰 HESAP"):
        st.session_state.active_tab = "HESAP"
    if st.button("📋 F4 ÖDEME LİSTESİ"):
        st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

# ==========================================
# AKILLI VERİ DAĞITIM VE İŞLEME MİMARİSİ
# ==========================================
if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        st.session_state.raw_df = raw_df
        
        cols_str = " ".join([str(c).upper() for c in raw_df.columns])
        if "NAKIT" in cols_str or "FT" in cols_str or "ODEME" in cols_str or "BANKA" in cols_str or "PERSONEL" in cols_str:
            processed_acc = process_personnel_account_data(raw_df)
            st.session_state.account_df = processed_acc
            st.session_state.hesap_df = processed_acc.copy()
            
        if "MÜŞTERİ" in cols_str or "MUSTERI" in cols_str or "BORÇ" in cols_str or "BORC" in cols_str or "FATURA BORCU" in cols_str or "F4" in uploaded_file.name.upper():
            f4_res = process_f4_payment_data(raw_df)
            st.session_state.f4_df = f4_res
            
    except Exception as e:
        st.error(f"❌ Dosya Okuma/İşleme Hatası: {e}")

# ==========================================
# TAB 1: HESAP
# ==========================================
if st.session_state.active_tab == "HESAP":
    account_df = st.session_state.account_df

    if account_df is not None:
        current_df = st.session_state.hesap_df.copy()
        
        temp_hesap_toplam = 0.0
        for idx, row in current_df.iterrows():
            ft_val = float(row["Nakit Ft Tutarı Topl"])
            odeme_val = float(row["Nakit Ödeme Tutarı Topl"])
            curr_b = st.session_state.get(f"banka_{idx}", float(row["Banka/ATM"]))
            temp_hesap_toplam += (ft_val + odeme_val - curr_b)

        def update_kasa():
            st.session_state.kasa_miktari = st.session_state.ust_kasa_input

        top_col1, top_col2 = st.columns([2.5, 2.5])
        with top_col1:
            st.title("📋 Günlük Personel Hesap Takip Paneli")
        with top_col2:
            st.markdown("<div style='background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border: 2px solid #FFA200; border-radius: 12px; padding: 12px; margin-top: 5px; box-shadow: 0 4px 8px rgba(255, 123, 0, 0.3);'>", unsafe_allow_html=True)
            
            kasa_input_col1, kasa_input_col2 = st.columns(2)
            with kasa_input_col1:
                st.number_input(
                    "🏦 MANÜEL KASA GİR", 
                    value=float(st.session_state.kasa_miktari), 
                    step=100.0, 
                    format="%.2f", 
                    key="ust_kasa_input",
                    on_change=update_kasa
                )
            with kasa_input_col2:
                st.markdown(f"<div style='padding-top: 28px;'><span style='font-size: 13px; color: #FFFFFF;'>📊 Toplam: <strong>{temp_hesap_toplam:,.2f} ₺</strong></span></div>", unsafe_allow_html=True)
            
            GuncelKasa = float(st.session_state.ust_kasa_input if "ust_kasa_input" in st.session_state else st.session_state.kasa_miktari)
            
            if GuncelKasa > temp_hesap_toplam:
                durum_metni = f"🔴 AÇIK {abs(GuncelKasa - temp_hesap_toplam):,.2f} ₺"
                renk_kodu = "#FFE5D9"
            elif GuncelKasa < temp_hesap_toplam:
                durum_metni = f"🟢 FAZLA {abs(temp_hesap_toplam - GuncelKasa):,.2f} ₺"
                renk_kodu = "#D8F3DC"
            else:
                durum_metni = "✅ KASA TAM (0.00 ₺)"
                renk_kodu = "#FFFFFF"
            
            st.markdown(f"<div style='text-align: center; padding-top: 8px; font-weight: bold; font-size: 15px; color: {renk_kodu};'>{durum_metni}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("💵 Hesap Toplama Ekranı (Para Sayma Modülü)", expanded=False):
            st.markdown("<p style='font-size:14px; color:#A0E7E5;'>Banknot adetlerini girerek toplam kasa tutarını hesaplayabilirsiniz.</p>", unsafe_allow_html=True)
            
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                 adet_200 = st.number_input("💵 200 TL Adet", min_value=0, value=0, step=1, key="adet_200")
                 adet_20 = st.number_input("💵 20 TL Adet", min_value=0, value=0, step=1, key="adet_20")
            with p_col2:
                 adet_100 = st.number_input("💵 100 TL Adet", min_value=0, value=0, step=1, key="adet_100")
                 adet_10 = st.number_input("💵 10 TL Adet", min_value=0, value=0, step=1, key="adet_10")
            with p_col3:
                 adet_50 = st.number_input("💵 50 TL Adet", min_value=0, value=0, step=1, key="adet_50")
                 adet_5 = st.number_input("💵 5 TL Adet", min_value=0, value=0, step=1, key="adet_5")

            toplam_para = (adet_200 * 200) + (adet_100 * 100) + (adet_50 * 50) + (adet_20 * 20) + (adet_10 * 10) + (adet_5 * 5)
            
            fark_hesaplama = toplam_para - GuncelKasa
            if fark_hesaplama > 0:
                fark_durum_metni = f"🟢 FAZLA: {fark_hesaplama:,.2f} ₺"
                fark_renk = "#D8F3DC"
            elif fark_hesaplama < 0:
                fark_durum_metni = f"🔴 AÇIK: {abs(fark_hesaplama):,.2f} ₺"
                fark_renk = "#FFE5D9"
            else:
                fark_durum_metni = "✅ KASA TAM (0.00 ₺)"
                fark_renk = "#FFFFFF"

            st.markdown(f"<div style='background: rgba(0,180,216,0.2); padding: 10px; border-radius: 8px; text-align: center; margin-top: 10px;'><span style='font-size: 16px; font-weight: bold; color: #90E0EF;'>Para Sayma Toplamı: {toplam_para:,.2f} ₺</span></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; text-align: center; margin-top: 8px;'><span style='font-size: 15px; font-weight: bold; color: {fark_renk};'>Fazla/Açık Durumu (Para Sayma Toplamı - Manüel Kasa): {fark_durum_metni}</span></div>", unsafe_allow_html=True)
            
            if st.button("📥 Bu Tutarı Manüel Kasaya Aktar"):
                st.session_state.kasa_miktari = float(toplam_para)
                st.rerun()

        st.caption("✍️ Personel fotoğrafları doğrudan GitHub deponuzdan URL kodlanmış şekilde çekilir.")

        if st.sidebar.button("🔄 Verileri Sıfırla"):
            st.session_state.hesap_df = account_df.copy()
            st.session_state.kasa_miktari = 0.0
            st.rerun()

        updated_rows = []
        
        for idx, row in current_df.iterrows():
            p_name = row["Personel Adı"]
            ft_val = float(row["Nakit Ft Tutarı Topl"])
            odeme_val = float(row["Nakit Ödeme Tutarı Topl"])
            current_banka = float(row["Banka/ATM"])
            current_islem = bool(row["İşlem"])

            foto_url = get_github_avatar(p_name)
            fallback_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={p_name.replace(' ', '')}"

            bg_style = "background: rgba(46, 125, 50, 0.35); border: 1px solid #2E7D32;" if current_islem else "background: linear-gradient(135deg, #FF7B00 0%, #FF5400 100%); border: 1px solid #FFA200; box-shadow: 0 4px 8px rgba(255, 123, 0, 0.2);"
            
            st.markdown(f"""
            <div style="{bg_style} border-radius: 12px; padding: 12px 15px; margin-bottom: 10px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                    <img src="{foto_url}" width="40" height="40" style="border-radius: 50%; object-fit: cover; border: 2px solid #00B4D8; background: #fff;" onerror="this.onerror=null; this.src='{fallback_url}';" />
                    <span style="font-weight: bold; font-size: 16px; color: #FFFFFF;">{p_name}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1.5])
            
            with c1:
                st.metric("Nakit Ft Topl", f"{ft_val:,.2f} ₺")
            with c2:
                st.metric("Nakit Ödeme Topl", f"{odeme_val:,.2f} ₺")
            with c3:
                new_banka = st.number_input(
                    "Banka/ATM (Manuel)", 
                    value=current_banka, 
                    step=10.0, 
                    format="%.2f", 
                    key=f"banka_{idx}",
                    label_visibility="collapsed"
                )
            with c4:
                hesap_sonuc = ft_val + odeme_val - new_banka
                st.metric("Hesap", f"{hesap_sonuc:,.2f} ₺")
            with c5:
                new_islem = st.checkbox("Tamam", value=current_islem, key=f"islem_{idx}")

            st.markdown("<hr style='margin: 5px 0 15px 0; border: none; border-top: 1px solid rgba(255,255,255,0.2);'>", unsafe_allow_html=True)

            updated_rows.append({
                "Personel Adı": p_name,
                "Nakit Ft Tutarı Topl": ft_val,
                "Nakit Ödeme Tutarı Topl": odeme_val,
                "Banka/ATM": new_banka,
                "Hesap": hesap_sonuc,
                "İşlem": new_islem
            })

        new_df = pd.DataFrame(updated_rows)
        
        if not new_df.equals(st.session_state.hesap_df):
            st.session_state.hesap_df = new_df
            st.rerun()

        st.markdown("<div class='kasa-box'>", unsafe_allow_html=True)
        st.subheader("💵 Genel Kasa ve Hesap Dengesi Özeti")
        toplam_hesap_alt = float(new_df["Hesap"].sum())

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Toplam Hesap", f"{toplam_hesap_alt:,.2f} ₺")
        col2.metric("🏦 Girilen Kasa", f"{GuncelKasa:,.2f} ₺")

        fark_alt = GuncelKasa - toplam_hesap_alt
        if fark_alt > 0:
            col3.metric("⚖️ Kasa Durumu", f"{fark_alt:,.2f} ₺", delta="FAZLA", delta_color="normal")
        elif fark_alt < 0:
            col3.metric("⚖️ Kasa Durumu", f"{abs(fark_alt):,.2f} ₺", delta="AÇIK", delta_color="inverse")
        else:
            col3.metric("⚖️ Kasa Durumu", f"0.00 ₺", delta="TAM", delta_color="off")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.title("📋 Günlük Personel Hesap Takip Paneli")
        st.info("💡 Lütfen sol taraftan **Personel Hesap Alımı Ekranı** dosyanızı yükleyin.")

# ==========================================
# TAB 2: F4 ÖDEME LİSTESİ (TAM FONKSİYONEL + PDF + ATANMAMIŞLAR)
# ==========================================
elif st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.title("📋 F4 Ödeme ve Personel Tahsilat Listesi")
    st.caption("✍️ Tablo üzerinden 'Sorumlu Personel' sütunundan açılır menüyü kullanarak veya manuel olarak personel seçebilir, değiştirebilirsiniz.")

    f4_df = st.session_state.f4_df
    if f4_df is not None and not f4_df.empty:
        
        edited_f4_df = st.data_editor(
            f4_df,
            column_config={
                "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺", disabled=True),
                "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                "Personel": st.column_config.SelectboxColumn(
                    "Sorumlu Personel",
                    help="Müşteriden sorumlu personeli seçin",
                    options=PERSONEL_LISTESI,
                    required=True
                )
            },
            hide_index=False,
            use_container_width=True,
            num_rows="fixed",
            key="f4_editable_table"
        )
        
        st.session_state.f4_df = pd.DataFrame(edited_f4_df)
        
        st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
        
        # ATANMAMIŞLAR BÖLÜMÜ
        atanmamis_df = st.session_state.f4_df[st.session_state.f4_df["Personel"] == "ATANMAMIŞ"]
        if not atanmamis_df.empty:
            st.markdown("### ⚠️ Personel Atanmamış Firmalar Listesi")
            st.info(f"Toplam {len(atanmamis_df)} adet firmaya henüz personel atanmamıştır. Yukarıdaki tablodan personel ataması yapabilirsiniz.")
            st.dataframe(
                atanmamis_df[["Müşteri Adı", "Fatura Borcu", "Personel"]],
                column_config={
                    "Müşteri Adı": st.column_config.TextColumn("Müşteri / Firma Adı"),
                    "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺"),
                    "Personel": st.column_config.TextColumn("Atanan Personel")
                },
                hide_index=True,
                use_container_width=True
            )
            st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)

        st.subheader("👥 Personele Göre F4 Tahsilat Dağılımı, Detayları ve PDF Çıktıları")

        current_f4 = st.session_state.f4_df
        personel_ozet = current_f4.groupby("Personel")["Fatura Borcu"].sum().reset_index()
        personel_ozet.columns = ["Personel Adı", "Toplam Tahsilat / Borç"]

        for _, row in personel_ozet.iterrows():
            p_ad = row["Personel Adı"]
            p_tutar = row["Toplam Tahsilat / Borç"]

            foto_url = get_github_avatar(p_ad)
            fallback_url = f"https://api.dicebear.com/7.x/avataaars/svg?seed={p_ad.replace(' ', '')}"

            with st.expander(f"👤 {p_ad} — Toplam: {p_tutar:,.2f} ₺", expanded=False):
                st.markdown(f"""
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <img src="{foto_url}" width="40" height="40" style="border-radius: 50%; object-fit: cover; border: 2px solid #FFA200; background: #fff;" onerror="this.onerror=null; this.src='{fallback_url}';" />
                        <div>
                            <strong style="color: #FFFFFF; font-size: 16px;">{p_ad}</strong><br>
                            <span style="color: #00B4D8; font-size: 14px;">Toplam Sorumluluk Tutarı: <strong>{p_tutar:,.2f} ₺</strong></span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                sub_df = current_f4[current_f4["Personel"] == p_ad]
                if not sub_df.empty:
                    st.dataframe(
                        sub_df[["Müşteri Adı", "Fatura Borcu"]],
                        column_config={
                            "Müşteri Adı": st.column_config.TextColumn("Müşteri / Firma Adı"),
                            "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    pdf_bytes = generate_personnel_pdf(p_ad, sub_df)
                    safe_filename = p_ad.replace(" ", "_").replace("İ", "I").replace("Ş", "S").replace("Ğ", "G").replace("Ü", "U").replace("Ö", "O").replace("Ç", "C")
                    st.download_button(
                        label=f"📄 {p_ad} - PDF Listesini İndir",
                        data=pdf_bytes,
                        file_name=f"F4_Tahsilat_Listesi_{safe_filename}.pdf",
                        mime="application/pdf",
                        key=f"pdf_btn_{p_ad}"
                    )
                else:
                    st.info("Bu personele atanmış müşteri bulunmuyor.")
    else:
        st.info("💡 Lütfen sol taraftan **F4 / Müşteri Borç Listesi** dosyanızı yükleyin.")
