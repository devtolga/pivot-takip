import streamlit as st
import ccxt
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime
import sys

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Pivot Terminali V15.1", layout="wide", page_icon="🦁")

# --- PLATFORM KONTROLÜ (SESSİZ MOD) ---
windows_platform = False 

# --- HAFIZA (SESSION STATE) ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'son_guncelleme' not in st.session_state:
    st.session_state.son_guncelleme = "-"
if 'secilen_coin_kodu' not in st.session_state:
    st.session_state.secilen_coin_kodu = None
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = 0

# --- YAN MENÜ ---
st.sidebar.header("⚙️ Kontrol Paneli")
tara_buton = st.sidebar.button("🚀 Taramayı Başlat / Yenile", type="primary")
st.sidebar.markdown("---")

# --- ÇOKLU İZLEME LİSTESİ SİSTEMİ ---
IZLEME_LISTELERI = {
    "Liste 1 (Genel Karışık)": """
EWTUSDT.P,GATE:BANKUSDT.P,MEXC:BANKUSDT.P,KCEX:BASUSDT.P,MEXC:BASUSDT.P,GATE:BASUSDT.P,MEXC:SPKUSDT.P,KCEX:LUNAUSDT.P,MEXC:ADAUSDT.P,GATE:SPKUSDT.P,MEXC:MITOUSDT.P,KCEX:HEMIUSDT.P,MEXC:SAPIENUSDT.P,MEXC:HYPEUSDT.P,MEXC:HEMIUSDT.P,MEXC:XDCUSDT.P,MEXC:FILUSDT.P,MEXC:CAMPUSDT.P,MEXC:PLUMEUSDT.P,MEXC:REZUSDT.P,MEXC:PENGUUSDT.P,GATE:GUNUSDT.P,MEXC:GUNUSDT.P,MEXC:SOMIUSDT.P,MEXC:HOMEUSDT.P,KCEX:LUNCUSDT.P,KCEX:USTCUSDT.P,MEXC:MOODENGUSDT.P,MEXC:SKATEUSDT.P,MEXC:CATIUSDT.P,BITGET:BGBUSDT.P,MEXC:QUSDT.P,MEXC:TURBOUSDT.P,MEXC:TLMUSDT.P,GATE:QUSDT.P,MEXC:TAUSDT.P,MEXC:HMSTRUSDT.P,MEXC:BLASTUSDT.P,MEXC:VELOUSDT.P,BINANCE:BNBUSDT.P,GATE:TLMUSDT.P,MEXC:RESOLVUSDT.P,MEXC:XPINUSDT.P,GATE:STXUSDT.P,MEXC:STXUSDT.P,MEXC:OLUSDT.P,MEXC:BRETTUSDT.P,MEXC:WLDUSDT.P,MEXC:DOGSUSDT.P,MEXC:HBARUSDT.P,MEXC:CAKEUSDT.P,GATE:CAKEUSDT.P,MEXC:HEIUSDT.P,GATE:C98USDT.P,MEXC:SAHARAUSDT.P,GATE:VETUSDT.P,MEXC:AIOZUSDT.P,MEXC:NEIROCTOUSDT.P,MEXC:FUNUSDT.P,MEXC:POPCATUSDT.P,MEXC:BERAUSDT.P,MEXC:VETUSDT.P,MEXC:IPUSDT.P,MEXC:AKEUSDT.P,MEXC:STBLUSDT.P,MEXC:ENSOUSDT.P,MEXC:HANAUSDT.P,MEXC:EPTUSDT.P,MEXC:FLOCKUSDT.P,MEXC:XPLUSDT.P,MEXC:VFYUSDT.P,MEXC:ARIAUSDT.P,MEXC:YBUSDT.P,MEXC:NILUSDT.P,MEXC:TSTUSDT.P,MEXC:HAEDALUSDT.P,MEXC:LIGHTUSDT.P,MEXC:EVAAUSDT.P,MEXC:TAKEUSDT.P,MEXC:OBOLUSDT.P,MEXC:TOSHIUSDT.P,MEXC:XANUSDT.P,MEXC:BUSDT.P,MEXC:FFUSDT.P,MEXC:DOODUSDT.P,MEXC:HOLOUSDT.P,MEXC:FORMUSDT.P,MEXC:MONUSDT.P,MEXC:SYRUPUSDT.P,MEXC:BANANAS31USDT.P,MEXC:LINEAUSDT.P,MEXC:ONDOUSDT.P,MEXC:B3USDT.P,MEXC:SOONUSDT.P,MEXC:CUDISUSDT.P,MEXC:LAUSDT.P,MEXC:BDXNUSDT.P,MEXC:AVAAIUSDT.P,MEXC:BABYUSDT.P,MEXC:YZYUSDT.P,MEXC:FUSDT.P,MEXC:WLFIUSDT.P,MEXC:KOMAUSDT.P,MEXC:METUSDT.P,MEXC:DEEPUSDT.P,MEXC:STOUSDT.P,MEXC:TRADOORUSDT.P,MEXC:UBUSDT.P,MEXC:AIOTUSDT.P,MEXC:OPENUSDT.P,MEXC:BLESSUSDT.P,MEXC:XIONUSDT.P,MEXC:RAYUSDT.P,MEXC:TFUELUSDT.P,MEXC:PENDLEUSDT.P,MEXC:ENAUSDT.P,MEXC:RECALLUSDT.P,BITGET:TRUSTUSDT.P,MEXC:4USDT.P,MEXC:0GUSDT.P,MEXC:KMNOUSDT.P,MEXC:TOWNSUSDT.P,MEXC:KITEUSDT.P,BITGET:KMNOUSDT.P,MEXC:ONUSDT.P,MEXC:MIRAUSDT.P,MEXC:GIGGLEUSDT.P,MEXC:BANUSDT.P,MEXC:TREEUSDT.P,MEXC:TURTLEUSDT.P,MEXC:ORDIUSDT.P,MEXC:DRIFTUSDT.P,MEXC:PUFFERUSDT.P,MEXC:AKTUSDT.P,BITGET:TRUMPUSDT.P,MEXC:LTCUSDT.P,MEXC:NXPCUSDT.P,GATE:MAVUSDT.P,MEXC:AIUSDT.P,MEXC:MAVUSDT.P,MEXC:ARKMUSDT.P,MEXC:TUTUSDT.P,MEXC:WALUSDT.P,MEXC:NOBODYUSDT.P,GATE:SKATEUSDT.P,MEXC:L3USDT.P,MEXC:PLAYUSDT.P,MEXC:CLANKERUSDT.P,MEXC:ONGUSDT.P,MEXC:AIOUSDT.P,MEXC:PROMPTUSDT.P,MEXC:PARTIUSDT.P,MEXC:FHEUSDT.P,GATE:NEWTUSDT.P,MEXC:NUSDT.P
    """,
    
    "Liste 2 (Altcoin Sepeti)": """
MEXC:SQDUSDT.P,MEXC:BULLAUSDT.P,MEXC:XVGUSDT.P,GATE:WOOUSDT.P,MEXC:WOOUSDT.P,MEXC:DMCUSDT.P,MEXC:GRIFFAINUSDT.P,MEXC:AGIUSDT.P,MEXC:DUSKUSDT.P,GATE:HUSDT.P,MEXC:HUSDT.P,MEXC:KAITOUSDT.P,MEXC:STORJUSDT.P,MEXC:QTUMUSDT.P,MEXC:TAGUSDT.P,MEXC:OXTUSDT.P,MEXC:VOXELUSDT.P,MEXC:CROSSUSDT.P,GATE:TANSSIUSDT.P,MEXC:NEOUSDT.P,MEXC:PUMPBTCUSDT.P,MEXC:BELUSDT.P,MEXC:IOSTUSDT.P,MEXC:PTBUSDT.P,MEXC:NTRNUSDT.P,MEXC:YALAUSDT.P,MEXC:TANSSIUSDT.P,MEXC:FLMUSDT.P,MEXC:CVCUSDT.P,MEXC:SLPUSDT.P,MEXC:ALICEUSDT.P,MEXC:TACUSDT.P,MEXC:DFUSDT.P,MEXC:ESPORTSUSDT.P,MEXC:SHELLUSDT.P,MEXC:DOGUSDT.P,MEXC:PONKEUSDT.P,MEXC:A2ZUSDT.P,MEXC:CHILLGUYUSDT.P,MEXC:PEAQUSDT.P,MEXC:SCRUSDT.P,MEXC:NFPUSDT.P,MEXC:ROAMUSDT.P,GATE:DENTUSDT.P,MEXC:USUALUSDT.P,MEXC:WCTUSDT.P,MEXC:EPICUSDT.P,MEXC:DENTUSDT.P,MEXC:GHSTUSDT.P,KCEX:KSMUSDT.P,MEXC:PYRUSDT.P,MEXC:SEIUSDT.P,MEXC:KSMUSDT.P,MEXC:SANTOSUSDT.P,MEXC:TRBUSDT.P,MEXC:AVAUSDT.P,GATE:DOTUSDT.P,MEXC:MLNUSDT.P,GATE:CELRUSDT.P,MEXC:AICUSDT.P,GATE:CRVUSDT.P,MEXC:CELRUSDT.P,MEXC:DOTUSDT.P,MEXC:CROUSDT.P,MEXC:CRVUSDT.P,MEXC:HIGHUSDT.P,MEXC:POWRUSDT.P,MEXC:GPSUSDT.P,MEXC:OPUSDT.P,GATE:PHBUSDT.P,MEXC:AWEUSDT.P,MEXC:PUNDIXUSDT.P,MEXC:ASTRUSDT.P,GATE:FORTHUSDT.P,MEXC:FORTHUSDT.P,MEXC:ENSUSDT.P,MEXC:SUSHIUSDT.P,MEXC:INUSDT.P,MEXC:AUCTIONUSDT.P,MEXC:SUNUSDT.P,MEXC:ANKRUSDT.P,MEXC:PHBUSDT.P,MEXC:KNCUSDT.P,MEXC:MOCAUSDT.P,MEXC:WUSDT.P,GATE:INUSDT.P,MEXC:ACEUSDT.P,GATE:KNCUSDT.P,GATE:MOCAUSDT.P,MEXC:MAGICUSDT.P,MEXC:MEUSDT.P,MEXC:ICXUSDT.P,MEXC:ZETAUSDT.P,GATE:TAIKOUSDT.P,GATE:AIXBTUSDT.P,MEXC:TAIKOUSDT.P,MEXC:VTHOUSDT.P,MEXC:ARPAUSDT.P,MEXC:AIXBTUSDT.P,MEXC:FIOUSDT.P,MEXC:DIAUSDT.P,MEXC:BEAMXUSDT.P,MEXC:VELODROMEUSDT.P,MEXC:AAVEUSDT.P,MEXC:ETHFIUSDT.P,MEXC:FLUXUSDT.P,MEXC:MEMEUSDT.P,MEXC:GIGAUSDT.P,MEXC:ACHUSDT.P,MEXC:SXPUSDT.P,MEXC:PYTHUSDT.P,MEXC:PNUTUSDT.P,GATE:PYTHUSDT.P,MEXC:SONICUSDT.P,MEXC:ETHWUSDT.P,MEXC:DODOUSDT.P,MEXC:ACXUSDT.P,MEXC:ZEUSUSDT.P,MEXC:GASUSDT.P,MEXC:AERGOUSDT.P,MEXC:VELVETUSDT.P,MEXC:BCHUSDT.P,MEXC:MEWUSDT.P,MEXC:ELXUSDT.P,MEXC:COOKIEUSDT.P,GATE:GASUSDT.P,MEXC:FLOWUSDT.P,GATE:FLOWUSDT.P,MEXC:FARTCOINUSDT.P,BINANCE:FARTCOINUSDT.P,MEXC:THEUSDT.P,MEXC:TOKENUSDT.P,GATE:ALICEUSDT.P,GATE:VANAUSDT.P,MEXC:AGTUSDT.P,MEXC:ICNTUSDT.P,MEXC:BTRUSDT.P,MEXC:KERNELUSDT.P,GATE:ICNTUSDT.P,MEXC:LAYERUSDT.P,MEXC:NAORISUSDT.P,MEXC:PROVEUSDT.P,MEXC:FWOGUSDT.P,MEXC:HIPPOUSDT.P,MEXC:SOPHUSDT.P,MEXC:MORPHOUSDT.P,MEXC:MERLUSDT.P,MEXC:SKYAIUSDT.P,MEXC:AINUSDT.P,GATE:ZORAUSDT.P,MEXC:SWARMSUSDT.P,MEXC:PUMPUSDT.P,GATE:AI16ZUSDT.P,GATE:SKLUSDT.P,MEXC:TIAUSDT.P,MEXC:MUSDT.P,MEXC:SKLUSDT.P,MEXC:BMTUSDT.P,MEXC:GRASSUSDT.P,GATE:ROSEUSDT.P,GATE:ZBCNUSDT.P,MEXC:ZBCNUSDT.P,MEXC:ROSEUSDT.P,GATE:VIRTUALUSDT.P,MEXC:CFXUSDT.P,MEXC:ORDERUSDT.P,MEXC:VIRTUALUSDT.P,MEXC:ERAUSDT.P,MEXC:PIPPINUSDT.P,MEXC:SYNUSDT.P,MEXC:CARVUSDT.P,MEXC:XNYUSDT.P,GATE:CARVUSDT.P,GATE:XNYUSDT.P,MEXC:XAIUSDT.P,MEXC:HUMAUSDT.P,MEXC:ZORAUSDT.P,GATE:BMTUSDT.P,MEXC:ASPUSDT.P,MEXC:AVLUSDT.P,MEXC:ALGOUSDT.P,MEXC:SIRENUSDT.P,MEXC:RUNEUSDT.P,MEXC:DOLOUSDT.P,GATE:RUNEUSDT.P,MEXC:IDOLUSDT.P,MEXC:CUSDT.P,GATE:SYNUSDT.P,MEXC:POLYXUSDT.P,MEXC:RBNTUSDT.P,MEXC:VINEUSDT.P
    """,

    "Liste 3 (Majör & Trend)": """
MEXC:ONTUSDT.P,MEXC:LUMIAUSDT.P,MEXC:MAVIAUSDT.P,MEXC:ZRXUSDT.P,GATE:ZRXUSDT.P,MEXC:ACTUSDT.P,MEXC:EDUUSDT.P,MEXC:OGNUSDT.P,MEXC:HIVEUSDT.P,KCEX:ACTUSDT.P,MEXC:TNSRUSDT.P,MEXC:SAFEUSDT.P,MEXC:MYXUSDT.P,BITGET:ZENUSDT.P,MEXC:ZECUSDT.P,MEXC:MELANIAUSDT.P,MEXC:IOUSDT.P,MEXC:CHZUSDT.P,MEXC:OGUSDT.P,MEXC:ARKUSDT.P,GATE:OGUSDT.P,MEXC:IDUSDT.P,MEXC:SSVUSDT.P,GATE:IDUSDT.P,MEXC:CTSIUSDT.P,MEXC:GOATUSDT.P,MEXC:BIOUSDT.P,MEXC:RDNTUSDT.P,GATE:DEXEUSDT.P,GATE:ASRUSDT.P,MEXC:PROMUSDT.P,MEXC:HFTUSDT.P,MEXC:ASRUSDT.P,MEXC:ONEUSDT.P,MEXC:FIDAUSDT.P,MEXC:CHESSUSDT.P,MEXC:XVSUSDT.P,MEXC:BANDUSDT.P,MEXC:CKBUSDT.P,MEXC:YGGUSDT.P,MEXC:ZILUSDT.P,MEXC:ATAUSDT.P,GATE:BANDUSDT.P,MEXC:GLMUSDT.P,MEXC:STGUSDT.P,MEXC:ZROUSDT.P,GATE:YGGUSDT.P,MEXC:XTZUSDT.P,MEXC:ALCHUSDT.P,MEXC:AEROUSDT.P,MEXC:HYPERUSDT.P,GATE:RPLUSDT.P,MEXC:XRPUSDT.P,MEXC:MANAUSDT.P,MEXC:DOGEUSDT.P,MEXC:ENJUSDT.P,MEXC:BICOUSDT.P,MEXC:ALPINEUSDT.P,MEXC:LDOUSDT.P,GATE:COMPUSDT.P,MEXC:DUSDT.P,MEXC:COMPUSDT.P,MEXC:SYSUSDT.P,MEXC:GUSDT.P,MEXC:COSUSDT.P,MEXC:ZKUSDT.P,MEXC:VICUSDT.P,MEXC:RAREUSDT.P,MEXC:HOOKUSDT.P,MEXC:LPTUSDT.P,MEXC:LINKUSDT.P,GATE:IDEXUSDT.P,MEXC:SANDUSDT.P,MEXC:RPLUSDT.P,MEXC:SPELLUSDT.P,MEXC:AUSDT.P,MEXC:COWUSDT.P,MEXC:HOTUSDT.P,MEXC:CYBERUSDT.P,MEXC:MINAUSDT.P,MEXC:CGPTUSDT.P,MEXC:TRUUSDT.P,MEXC:AVAXUSDT.P,MEXC:API3USDT.P,MEXC:AEVOUSDT.P,MEXC:SCRTUSDT.P,MEXC:RENDERUSDT.P,GATE:COSUSDT.P,MEXC:IDEXUSDT.P,MEXC:DEGOUSDT.P,MEXC:PHAUSDT.P,MEXC:C98USDT.P,MEXC:FTTUSDT.P,MEXC:ZEREBROUSDT.P,MEXC:VANRYUSDT.P,MEXC:RLCUSDT.P,MEXC:MBOXUSDT.P,MEXC:STRKUSDT.P,MEXC:BLURUSDT.P,GATE:OMUSDT.P,MEXC:LISTAUSDT.P,MEXC:LRCUSDT.P,MEXC:XLMUSDT.P,MEXC:NOTUSDT.P,GATE:ORCAUSDT.P,MEXC:MOVRUSDT.P,MEXC:OMUSDT.P,MEXC:ETCUSDT.P,MEXC:ORCAUSDT.P,GATE:DYDXUSDT.P,BITGET:LRCUSDT.P,MEXC:JASMYUSDT.P,MEXC:DYMUSDT.P,MEXC:COTIUSDT.P,MEXC:APTUSDT.P,MEXC:CHRUSDT.P,MEXC:PEOPLEUSDT.P,MEXC:IOTXUSDT.P,MEXC:THETAUSDT.P,MEXC:CVXUSDT.P,GATE:FETUSDT.P,MEXC:KASUSDT.P,MEXC:SUPERUSDT.P,MEXC:FETUSDT.P,GATE:SNXUSDT.P,MEXC:1INCHUSDT.P,GATE:CETUSUSDT.P,MEXC:CETUSUSDT.P,MEXC:CELOUSDT.P,MEXC:IOTAUSDT.P,MEXC:ILVUSDT.P,MEXC:UMAUSDT.P,GATE:IOTAUSDT.P,MEXC:NKNUSDT.P,MEXC:GALAUSDT.P,MEXC:RSRUSDT.P,MEXC:SNXUSDT.P,GATE:MASKUSDT.P,MEXC:POLUSDT.P,MEXC:AXSUSDT.P,MEXC:RVNUSDT.P,MEXC:SUSDT.P,MEXC:MASKUSDT.P,MEXC:DASHUSDT.P,MEXC:IMXUSDT.P,GATE:NEARUSDT.P,MEXC:ICPUSDT.P,GATE:KAVAUSDT.P,MEXC:APEUSDT.P,MEXC:KAVAUSDT.P,MEXC:PORTALUSDT.P,MEXC:UNIUSDT.P,GATE:INJUSDT.P,MEXC:INJUSDT.P,GATE:LQTYUSDT.P,MEXC:BATUSDT.P,MEXC:SPXUSDT.P,MEXC:TUSDT.P,MEXC:LQTYUSDT.P,GATE:ATOMUSDT.P,MEXC:ATOMUSDT.P,MEXC:GMTUSDT.P,MEXC:WAVESUSDT.P,MEXC:EGLDUSDT.P,MEXC:ARUSDT.P,KCEX:FXSUSDT.P,GATE:GRTUSDT.P,MEXC:GRTUSDT.P,BITGET:ARCUSDT.P,MEXC:ARCSOLUSDT.P,MEXC:ZKPUSDT.P
    """,
    
    "Liste 4 (Gem & Yeni)": """
MEXC:PIEVERSEUSDT.P,BINANCE:RAVEUSDT.P,MEXC:RIVERUSDT.P,KCEX:L3USDT.P,MEXC:DAMUSDT.P,BINANCE:CYSUSDT.P,MEXC:TRUTHUSDT.P,MEXC:VVVUSDT.P,MEXC:CLOUSDT.P,BINANCE:NIGHTUSDT.P,MEXC:AVNTUSDT.P,MEXC:MMTUSDT.P,MEXC:SENTUSDT.P,MEXC:SIGNUSDT.P,MEXC:BLUAIUSDT.P,MEXC:1000RATSUSDT.P,MEXC:LABUSDT.P,MEXC:APRUSDT.P,MEXC:LYNUSDT.P,KCEX:PROVEUSDT.P,KCEX:GIGGLEUSDT.P,MEXC:BARDUSDT.P,MEXC:42USDT.P,MEXC:BROCCOLIUSDT.P,MEXC:MANTAUSDT.P,MEXC:COMMONUSDT.P,KCEX:DGRAMUSDT.P,MEXC:DGRAMUSDT.P,MEXC:JCTUSDT.P,MEXC:ASTERUSDT.P,MEXC:SKYUSDT.P,MEXC:METISUSDT.P,MEXC:KGENUSDT.P,MEXC:SAGAUSDT.P,MEXC:BANANAUSDT.P,MEXC:ZRCUSDT.P,MEXC:GUAUSDT.P,MEXC:CCUSDT.P,BINANCE:WETUSDT.P,MEXC:JELLYJELLYUSDT.P,MEXC:UAIUSDT.P,MEXC:GAIXUSDT.P,MEXC:ATUSDT.P,KCEX:PINGUSDT.P,MEXC:RVVUSDT.P,KCEX:BEATUSDT.P,MEXC:FOLKSUSDT.P,KCEX:FOLKSUSDT.P,MEXC:ARTXUSDT.P,KCEX:TRUTHUSDT.P,MEXC:NOMUSDT.P,KCEX:NOBODYUSDT.P,MEXC:ZBTUSDT.P,MEXC:ZKCUSDT.P
    """
}

# Listeyi Seçme Kutusu
secilen_liste_adi = st.sidebar.selectbox("📋 İzleme Listesi Seç", list(IZLEME_LISTELERI.keys()))

# Seçilen listenin içeriğini al
liste_icerigi = IZLEME_LISTELERI[secilen_liste_adi]

# Kullanıcının düzenleyebilmesi için Text Area'ya koy (Varsayılan değer seçilen liste)
raw_input = st.sidebar.text_area("Liste İçeriği (Düzenlenebilir)", liste_icerigi, height=150)
# ----------------------------------------

pivot_secenekleri = {
    "Günlük (Standart)": "1d",
    "4 Saatlik (Day Trade)": "4h",
    "Haftalık (Swing)": "1w",
    "Aylık (Uzun Vade)": "1M"
}
secilen_pivot_isim = st.sidebar.selectbox("Pivot Zaman Dilimi", list(pivot_secenekleri.keys()), index=0)
pivot_tf = pivot_secenekleri[secilen_pivot_isim]

oto_yenile = st.sidebar.checkbox("Otomatik Yenileme (Döngü)", value=False)
yenileme_hizi = st.sidebar.slider("Döngü Hızı (Saniye)", min_value=10, max_value=900, value=60)
st.sidebar.caption(f"Seçilen Süre: {yenileme_hizi // 60} dakika {yenileme_hizi % 60} saniye")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 İndikatör Ayarları")
rsi_periyot = st.sidebar.number_input("RSI Periyodu", value=14)
ema_periyot = st.sidebar.number_input("Trend EMA (Genelde 200)", value=200)

# --- BAĞLANTILAR ---
@st.cache_resource
def init_exchanges():
    return {
        'binance': ccxt.binance(),
        'mexc': ccxt.mexc(),
        'gate': ccxt.gate(),
        'htx': ccxt.htx(),
        'bitget': ccxt.bitget(),
        'coinex': ccxt.coinex()
    }
exchanges = init_exchanges()

# --- ANALİZ FONKSİYONLARI ---
def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_ema(prices, period=200):
    return prices.ewm(span=period, adjust=False).mean()

def parse_symbol(tv_string):
    try:
        parts = tv_string.split(':')
        if len(parts) != 2: return None
        exchange_tag, symbol_raw = parts[0].upper(), parts[1]
        exchange_id = 'binance' 
        if 'MEXC' in exchange_tag: exchange_id = 'mexc'
        elif 'GATE' in exchange_tag: exchange_id = 'gate'
        elif 'BITGET' in exchange_tag: exchange_id = 'bitget'
        elif 'HTX' in exchange_tag: exchange_id = 'htx'
        elif 'COINEX' in exchange_tag: exchange_id = 'coinex'
        is_futures = symbol_raw.endswith('.P')
        clean_symbol = symbol_raw.replace('.P', '') if is_futures else symbol_raw
        if clean_symbol.endswith('USDT'): base, quote = clean_symbol[:-4], 'USDT'
        elif clean_symbol.endswith('USD'): base, quote = clean_symbol[:-3], 'USDT'
        else: return None
        final_symbol = f"{base}/{quote}"
        return (exchange_id, final_symbol, is_futures, tv_string)
    except: return None

def grafik_ciz(baslik, pivot, current_price, ohlc_data, rsi_val, ema_val, pivot_label):
    df_chart = pd.DataFrame(ohlc_data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df_chart['Time'] = pd.to_datetime(df_chart['Time'], unit='ms')

    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_chart['Time'], open=df_chart['Open'], high=df_chart['High'],
                low=df_chart['Low'], close=df_chart['Close'], name='Fiyat'))
    fig.add_hline(y=pivot, line_dash="dash", line_color="yellow", annotation_text=pivot_label)
    fig.add_hline(y=ema_val, line_color="blue", annotation_text=f"EMA {ema_periyot} (Trend)", annotation_position="bottom right")
    trend_renk = "🟢" if current_price > ema_val else "🔴"
    fig.update_layout(title=f'{baslik} | RSI: {rsi_val} | Trend: {trend_renk}',
        yaxis_title='Fiyat', template='plotly_dark', height=450, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def tarama_yap(p_tf, p_label):
    items = [x.strip() for x in raw_input.split(',')]
    veriler = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, item in enumerate(items):
        if not item: continue
        parsed = parse_symbol(item)
        if not parsed: continue
        exc_id, symbol, is_futures, orig_name = parsed
        
        try:
            exchange = exchanges[exc_id]
            params = {'type': 'swap'} if is_futures else {}
            if is_futures and exc_id == 'mexc' and ':' not in symbol: symbol += ":USDT"

            htf_candles = exchange.fetch_ohlcv(symbol, timeframe=p_tf, limit=2, params=params)
            if len(htf_candles) < 2: continue
            prev = htf_candles[0] 
            pivot = (prev[2] + prev[3] + prev[4]) / 3
            
            klines = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=400, params=params)
            if len(klines) < ema_periyot: continue
            
            df_close = pd.Series([x[4] for x in klines])
            current_price = klines[-1][4]
            rsi_val = round(calculate_rsi(df_close, rsi_periyot).iloc[-1], 2)
            ema_val = calculate_ema(df_close, ema_periyot).iloc[-1]
            
            trend = "YÜKSELİŞ 🐂" if current_price > ema_val else "DÜŞÜŞ 🐻"
            fark = ((current_price - pivot) / pivot) * 100
            durum = "🟢 ÜSTÜNDE" if current_price > pivot else "🔴 ALTINDA"
            
            sinyal_txt = "Sakin"
            if abs(fark) < 0.6:
                sinyal_txt = "⚠️ KIRILIM YAKIN"
                if (current_price > pivot and current_price < ema_val) or \
                   (current_price < pivot and current_price > ema_val):
                    sinyal_txt += " (Trend Tersi!)"
                
            veriler.append({
                "Borsa": exc_id.upper(), "Coin": orig_name, "Fiyat": current_price,
                "Pivot": round(pivot, 4), "Fark (%)": round(fark, 2), "RSI": rsi_val,
                "Trend": trend, "Durum": durum, "Sinyal": sinyal_txt,
                "Veri": klines[-50:], "EMA_Val": ema_val, "Pivot_Label": p_label
            })
        except Exception as e: pass
        
        status_text.text(f"Taranıyor ({p_label}): {orig_name}...")
        progress_bar.progress((i + 1) / len(items))
        
    progress_bar.empty()
    status_text.empty()
    
    st.session_state.son_guncelleme = datetime.now().strftime('%H:%M:%S')
    st.session_state.last_fetch_time = time.time()
    return pd.DataFrame(veriler)

# --- TARAMA TETİKLEME MANTIĞI ---
st.title(f"🦁 Pro Pivot Terminali: {secilen_pivot_isim}")

should_run_scan = False

# Manuel Buton
if tara_buton:
    should_run_scan = True

# Otomatik Yenileme (Zaman Kontrolü)
if oto_yenile:
    gecen_sure = time.time() - st.session_state.last_fetch_time
    if gecen_sure > yenileme_hizi:
        should_run_scan = True

# TARAMA İŞLEMİ
if should_run_scan:
    with st.spinner(f'{secilen_liste_adi} - {secilen_pivot_isim} verileri taranıyor...'):
        df_sonuc = tarama_yap(pivot_tf, secilen_pivot_isim)
        st.session_state.df = df_sonuc
        st.rerun()

# --- GÖSTERİM BÖLÜMÜ ---
if not st.session_state.df.empty:
    df = st.session_state.df
    st.info(f"Son Güncelleme: {st.session_state.son_guncelleme} | Liste: {secilen_liste_adi} | Referans: {secilen_pivot_isim} | EMA: {ema_periyot}")
    
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("📊 Piyasa Tablosu (Seçim Yapın)")
        event = st.dataframe(
            df[['Borsa', 'Coin', 'Fiyat', 'Pivot', 'Fark (%)', 'RSI', 'Trend', 'Durum', 'Sinyal']].style.applymap(
                lambda x: 'color: green' if 'YÜKSELİŞ' in str(x) else 'color: red' if 'DÜŞÜŞ' in str(x) else '', subset=['Trend']
            ).format({"Fiyat": "{:.4f}", "RSI": "{:.2f}", "Pivot": "{:.4f}"}),
            height=600, use_container_width=True,
            on_select="rerun", selection_mode="single-row"
        )
        
        if len(event.selection.rows) > 0:
            secilen_index = event.selection.rows[0]
            st.session_state.secilen_coin_kodu = df.iloc[secilen_index]['Coin']

    with col2:
        st.subheader("🔍 Grafik Analizi")
        gosterilecek_coin = st.session_state.secilen_coin_kodu
        
        # Seçim yoksa ilkini göster
        if gosterilecek_coin is None and not df.empty:
            gosterilecek_coin = df.iloc[0]['Coin']
            
        if gosterilecek_coin:
            try:
                row = df[df['Coin'] == gosterilecek_coin].iloc[0]
                fig = grafik_ciz(f"{row['Borsa']} - {row['Coin']}", row['Pivot'], row['Fiyat'], row['Veri'], row['RSI'], row['EMA_Val'], row['Pivot_Label'])
                st.plotly_chart(fig, use_container_width=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Pivot Farkı", f"% {row['Fark (%)']}")
                c2.metric("RSI", f"{row['RSI']}")
                c3.metric("Trend", "BULLISH" if "YÜKSELİŞ" in row['Trend'] else "BEARISH", delta_color="normal")
            except IndexError:
                st.warning("Veri bulunamadı veya liste değişti.")
else:
    st.warning("Henüz tarama yapılmadı. Sol menüden 'Taramayı Başlat' butonuna basın.")

# --- GERİ SAYIM SAYACI ve DÖNGÜ ---
if oto_yenile:
    gecen_sure = time.time() - st.session_state.last_fetch_time
    kalan_sure = int(yenileme_hizi - gecen_sure)
    
    if kalan_sure > 0:
        st.divider()
        st.caption(f"⏳ Otomatik yenilemeye kalan süre: **{kalan_sure}** saniye.")
        time.sleep(1)
        st.rerun()
    else:
        st.rerun()
