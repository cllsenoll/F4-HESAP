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
if 'editable_f4_df' not in st.session_state:
    st.session_state.editable_f4_df = None

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
        margin-bottom: 10px !important;
        text-align: left !important;
        padding-left: 15px !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# YARDIMCI PARSE FONKSİYONLARI
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

def smart_read_file(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    for enc in ['cp1254', 'iso-8859-9', 'utf-8-sig', 'utf-8', 'latin1']:
        for sep in [';', ',', '\t', None]:
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
    raise Exception("Dosya yapısı çözümlenemedi.")

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
# SIDEBAR MENÜ
# ==========================================
with st.sidebar:
    st.markdown("""
    <div class="notranslate" style="text-align: center; padding-bottom: 10px;">
        <h2 style="margin: 0; color: #FFFFFF;">Yurtiçi Kargo</h2>
        <h4 style="margin: 0; color: #F57C00;">Görükle Acente KOYS</h4>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("📂 Rapor / Liste Yükle", type=['csv', 'xlsx', 'xls', 'html'])
    st.markdown("<hr style='border: 1px solid rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    
    if st.button("📋 F4 ÖDEME LİSTESİ"):
        st.session_state.active_tab = "F4 ÖDEME LİSTESİ"

if uploaded_file is not None:
    try:
        raw_df = smart_read_file(uploaded_file)
        st.session_state.raw_df = raw_df
        cols_str = " ".join([str(c).upper() for c in raw_df.columns])
        if "MÜŞTERİ" in cols_str or "MUSTERI" in cols_str or "BORÇ" in cols_str or "BORC" in cols_str or "FATURA BORCU" in cols_str or "F4" in uploaded_file.name.upper():
            f4_res = process_f4_payment_data(raw_df)
            st.session_state.f4_df = f4_res
            st.session_state.editable_f4_df = f4_res.copy()
    except Exception as e:
        st.error(f"❌ Dosya Okuma/İşleme Hatası: {e}")

# ==========================================
# ANA EKRAN: F4 ÖDEME LİSTESİ
# ==========================================
if st.session_state.active_tab == "F4 ÖDEME LİSTESİ":
    st.markdown("### 📋 F4 Ödeme ve Personel Tahsilat Listesi")
    st.caption("Tablo üzerinden 'Sorumlu Personel' sütununa tıklayarak eksik veya atanmamış firmaların personel isimlerini **manuel olarak** yazabilir veya değiştirebilirsiniz.")
    
    f4_df = st.session_state.get('f4_df', None)
    
    if f4_df is not None and not f4_df.empty:
        if st.session_state.editable_f4_df is None:
            st.session_state.editable_f4_df = f4_df.copy()

        tum_personel_secenekleri = sorted(list(set(PERSONEL_LISTESI + list(st.session_state.editable_f4_df["Personel"].unique()))))
        
        # 1. BÖLÜM: TÜM LİSTE (Düzenlenebilir Ana Tablo)
        edited_df = st.data_editor(
            st.session_state.editable_f4_df,
            column_config={
                "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺", disabled=True),
                "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                "Personel": st.column_config.SelectboxColumn(
                    "Sorumlu Personel (Düzenlenebilir)",
                    options=tum_personel_secenekleri,
                    required=True
                )
            },
            use_container_width=True,
            hide_index=True,
            key="f4_main_data_editor"
        )
        st.session_state.editable_f4_df = edited_df

        st.markdown("<hr style='border: 2px solid #F57C00; margin: 40px 0;'>", unsafe_allow_html=True)

        # 2. BÖLÜM: PERSONELE GÖRE SÜZGEÇ VE ALT GÖRÜNÜM
        st.markdown("🔍 **Sorumlu Personele Göre Süzgeçle:**")
        secilen_personel_filtre = st.selectbox(
            "Personel Seçin",
            options=tum_personel_secenekleri,
            label_visibility="collapsed"
        )

        filtered_display_df = st.session_state.editable_f4_df[st.session_state.editable_f4_df["Personel"] == secilen_personel_filtre]
        toplam_kayit = len(filtered_display_df)

        st.markdown(f"### 📌 Seçilen Görünüm: {secilen_personel_filtre} (Toplam {toplam_kayit} Kayıt)")

        st.dataframe(
            filtered_display_df,
            column_config={
                "Müşteri Adı": st.column_config.TextColumn("Müşteri Adı", disabled=True),
                "Fatura Borcu": st.column_config.NumberColumn("Fatura Borcu", format="%.2f ₺", disabled=True),
                "Açıklama": st.column_config.TextColumn("Açıklama", disabled=True),
                "Personel": st.column_config.TextColumn("Personel", disabled=True)
            },
            use_container_width=True,
            hide_index=True
        )
        
    else:
        st.info("ℹ️ Lütfen sol panelden F4 ödeme / müşteri borç listesini yükleyin.")
