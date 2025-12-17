import streamlit as st
import ccxt
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime
import sys

# --- PLATFORM VE SES KONTROLÜ ---
if sys.platform.startswith('win'):
    try:
        import winsound
        windows_platform = True
    except ImportError:
        windows_platform = False
else:
    windows_platform = False

def ses_cal():
    """Sadece Windows'ta ses çıkarır."""
    if windows_platform:
        try: winsound.Beep(1000, 500)
        except: pass

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Pivot Terminali V8", layout="wide", page_icon="🦁")

# --- HAFIZA ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'son_guncelleme' not in st.session_state:
    st.session_state.son_guncelleme = "-"

# --- YAN MENÜ ---
st.sidebar.header("⚙️ Kontrol Paneli")
tara_buton = st.sidebar.button("🚀 Taramayı Başlat / Yenile", type="primary")
st.sidebar.markdown("---")

pivot_secenekleri = {
    "Günlük (Standart)": "1d",
    "4 Saatlik (Day Trade)": "4h",
    "Haftalık (Swing)": "1w",
    "Aylık (Uzun Vade)": "1M"
}
secilen_pivot_isim = st.sidebar.selectbox("Pivot Zaman Dilimi", list(pivot_secenekleri.keys()), index=0)
pivot_tf = pivot_secenekleri[secilen_pivot_isim]

oto_yenile = st.sidebar.checkbox("Otomatik Yenileme (Döngü)", value=False)
yenileme_hizi = st.sidebar.slider("Döngü Hızı (Saniye)", 10, 300, 60) # Alt limit 10 yapıldı
sesli_uyari = st.sidebar.checkbox("Sesli Alarm 🔊", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📊 İndikatör Ayarları")
rsi_periyot = st.sidebar.number_input("RSI Periyodu", value=14)
ema_periyot = st.sidebar.number_input("Trend EMA (Genelde 200)", value=200)

# Takip Listesi
DEFAULT_RAW_LIST = """
PYTH:GUSD,MEXC:GUSDT.P,CRYPTO:CHESSUSD,MEXC:CHESSUSDT.P,MEXC:BIOUSDT.P,CRYPTO:ORCAUSD,MEXC:ORCAUSDT.P,GATE:ORCAUSDT.P,MEXC:CVXUSDT.P,CRYPTO:CVXUSD,CRYPTO:LRCUSD,CRYPTO:KDAUSD,MEXC:YGGUSDT.P,GATE:DEXEUSDT.P,CRYPTO:YGGUSD,CRYPTO:CHRUSD,GATE:YGGUSDT.P,MEXC:CHRUSDT.P,CRYPTO:DEXEUSD,MEXC:C98USDT.P,CRYPTO:OGNUSD,GATE:IDUSDT.P,CRYPTO:GMTUSD,MEXC:GMTUSDT.P,CRYPTO:PERPUSD,GATE:NEARUSDT.P,CRYPTO:TNSRUSD,MEXC:TNSRUSDT.P,CRYPTO:NEARUSD,MEXC:ENJUSDT.P,MEXC:COSUSDT.P,MEXC:OGNUSDT.P,CRYPTO:GMXUSD,CRYPTO:COSUSD,MEXC:GMXUSDT.P,CRYPTO:IDUSD,MEXC:MASKUSDT.P,MEXC:LRCUSDT.P,MEXC:IDUSDT.P,CRYPTO:MASKUSD,GATE:MASKUSDT.P,MEXC:SYSUSDT.P,MEXC:LQTYUSDT.P,CRYPTO:ATOMUSD,CRYPTO:ENJUSD,MEXC:DUSDT.P,MEXC:ATOMUSDT.P,CRYPTO:GALAUSD,MEXC:COWUSDT.P,GATE:COSUSDT.P,GATE:ATOMUSDT.P,GATE:LQTYUSDT.P,CRYPTO:NKNUSD,MEXC:RPLUSDT.P,MEXC:NKNUSDT.P,CRYPTO:LQTYUSD,CRYPTO:RPLUSD,GATE:CETUSUSDT.P,CRYPTO:CETUSUSD,CRYPTO:LPTUSD,MEXC:CETUSUSDT.P,CRYPTO:IMXUSD,CRYPTO:JASMYUSD,CRYPTO:HOOKUSD,MEXC:SNXUSDT.P,CRYPTO:RSRUSD,MEXC:BLURUSDT.P,CRYPTO:COWUSD,CRYPTO:SYSUSD,MEXC:GALAUSDT.P,CRYPTO:SNXUSD,MEXC:LPTUSDT.P,CRYPTO:SSVUSD,MEXC:SSVUSDT.P,MEXC:HOOKUSDT.P,GATE:SNXUSDT.P,CRYPTO:CELOUSD,MEXC:APTUSDT.P,MEXC:SPXUSDT.P,MEXC:IMXUSDT.P,BITGET:LRCUSDT.P,MEXC:BANDUSDT.P,MEXC:SUPERUSDT.P,CRYPTO:BLURUSD,MEXC:CELOUSDT.P,MEXC:JASMYUSDT.P,MEXC:LUMIAUSDT.P,CRYPTO:MOVRUSD,MEXC:BICOUSDT.P,CRYPTO:LUMIAUSD,CRYPTO:BICOUSD,GATE:RPLUSDT.P,CRYPTO:ONEUSD,MEXC:XVSUSDT.P,CRYPTO:MINAUSD,MEXC:RAREUSDT.P,CRYPTO:XVSUSD,MEXC:HOTUSDT.P,CRYPTO:STGUSD,MEXC:MOVRUSDT.P,CRYPTO:RAREUSD,CRYPTO:CGPTUSD,MEXC:CGPTUSDT.P,CRYPTO:KASUSD,GATE:BANDUSDT.P,MEXC:DEGOUSDT.P,MEXC:ONTUSDT.P,CRYPTO:ONTUSD,CRYPTO:HOTUSD,MEXC:KASUSDT.P,BITGET:ARCUSDT.P,MEXC:TWTUSDT.P,CRYPTO:TWTUSD,CRYPTO:BANDUSD,MEXC:EGLDUSDT.P,CRYPTO:SUPERUSD,MEXC:ARCSOLUSDT.P,CRYPTO:DEGOUSD,MEXC:NOTUSDT.P,CRYPTO:CKBUSD,MEXC:ONEUSDT.P,CRYPTO:DYDXUSD,GATE:DYDXUSDT.P,CRYPTO:EGLDUSD,MEXC:CKBUSDT.P,CRYPTO:ALCHUSD,MEXC:RSRUSDT.P,CRYPTO:RVNUSD,MEXC:STGUSDT.P,CRYPTO:ILVUSD,MEXC:ALCHUSDT.P,CRYPTO:AUDIOUSD,CRYPTO:ICPUSD,GATE:ZRXUSDT.P,MEXC:RVNUSDT.P,BINANCE:ICPUSDT,MEXC:MINAUSDT.P,MEXC:ICPUSDT.P,CRYPTO:AEVOUSD,MEXC:ZRXUSDT.P,CRYPTO:ZRXUSD,CRYPTO:IOTXUSD,MEXC:IOTXUSDT.P,MEXC:ILVUSDT.P,MEXC:AEVOUSDT.P,MEXC:RDNTUSDT.P,CRYPTO:RDNTUSD,MEXC:FIDAUSDT.P,CRYPTO:FIDAUSD,CRYPTO:RLCUSD,MEXC:UMAUSDT.P,MEXC:RLCUSDT.P,CRYPTO:UMAUSD,MEXC:1INCHUSDT.P,CRYPTO:1INCHUSD,MEXC:SCRTUSDT.P,MEXC:AUDIOUSDT.P,MEXC:CYBERUSDT.P,BINANCE:STRKUSDT,MEXC:STRKUSDT.P,MEXC:TUSDT.P,CRYPTO:TUSD,MEXC:PHAUSDT.P,CRYPTO:PHAUSD,MEXC:HYPERUSDT.P,MEXC:GLMUSDT.P,MEXC:ZKUSDT.P,MEXC:EDUUSDT.P,CRYPTO:DASHUSD,MEXC:DASHUSDT.P,CRYPTO:MDTUSD,MEXC:BATUSDT.P,CRYPTO:BATUSD,MEXC:ZECUSDT.P,CRYPTO:ZECUSD,CRYPTO:GALUSD,CRYPTO:ORNUSD
"""
raw_input = st.sidebar.text_area("Takip Listesi", DEFAULT_RAW_LIST, height=150)

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

# --- GRAFİK FONKSİYONU ---
def grafik_ciz(baslik, pivot, current_price, ohlc_data, rsi_val, ema_val, pivot_label):
    df_chart = pd.DataFrame(ohlc_data, columns=['Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df_chart['Time'] = pd.to_datetime(df_chart['Time'], unit='ms')

    fig = go.Figure()

    # Mumlar
    fig.add_trace(go.Candlestick(x=df_chart['Time'], open=df_chart['Open'], high=df_chart['High'],
                low=df_chart['Low'], close=df_chart['Close'], name='Fiyat'))

    # Pivot (Dinamik Etiket)
    fig.add_hline(y=pivot, line_dash="dash", line_color="yellow", annotation_text=pivot_label)
    
    # EMA 200 Çizgisi (Mavi)
    fig.add_hline(y=ema_val, line_color="blue", annotation_text=f"EMA {ema_periyot} (Trend)", annotation_position="bottom right")

    trend_renk = "🟢" if current_price > ema_val else "🔴"
    
    fig.update_layout(
        title=f'{baslik} | RSI: {rsi_val} | Trend: {trend_renk}',
        yaxis_title='Fiyat', template='plotly_dark', height=450,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# --- TARAMA MOTORU ---
def tarama_yap(p_tf, p_label):
    items = [x.strip() for x in raw_input.split(',')]
    veriler = []
    yeni_sinyal = False
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, item in enumerate(items):
        if not item: continue
        parsed = parse_symbol(item)
        if not parsed: continue
        exc_id, symbol, is_futures, orig
