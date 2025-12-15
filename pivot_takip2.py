import streamlit as st
import ccxt
import pandas as pd
import time
from datetime import datetime
import winsound

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Pivot Terminali (Tablo Modu)", layout="wide", page_icon="🦁")

# --- HAFIZA AYARLARI ---
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()
if 'son_guncelleme' not in st.session_state:
    st.session_state.son_guncelleme = "-"

# --- YAN MENÜ ---
st.sidebar.header("⚙️ Kontrol Paneli")

# Taramayı Başlat Butonu
tara_buton = st.sidebar.button("🚀 Taramayı Başlat / Yenile", type="primary")

st.sidebar.markdown("---")

# Pivot Zaman Dilimi Seçimi
pivot_secenekleri = {
    "Günlük (Standart)": "1d",
    "4 Saatlik (Day Trade)": "4h",
    "Haftalık (Swing)": "1w",
    "Aylık (Uzun Vade)": "1M"
}
secilen_pivot_isim = st.sidebar.selectbox("Pivot Zaman Dilimi", list(pivot_secenekleri.keys()), index=0)
pivot_tf = pivot_secenekleri[secilen_pivot_isim]

oto_yenile = st.sidebar.checkbox("Otomatik Yenileme (Döngü)", value=False)
yenileme_hizi = st.sidebar.slider("Döngü Hızı (Saniye)", 30, 600, 60)
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

def ses_cal():
    try: winsound.Beep(1000, 500)
    except: pass

def tarama_yap(p_tf):
    items = [x.strip() for x in raw_input.split(',')]
    veriler = []
    yeni_sinyal = False
    
    # İlerleme Çubuğu
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

            # 1. PIVOT HESAPLAMA
            htf_candles = exchange.fetch_ohlcv(symbol, timeframe=p_tf, limit=2, params=params)
            if len(htf_candles) < 2: continue
            prev = htf_candles[0] 
            pivot = (prev[2] + prev[3] + prev[4]) / 3
            
            # 2. ANLIK VERİ
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
            uyari_var = False
            
            if abs(fark) < 0.6:
                sinyal_txt = "⚠️ KIRILIM YAKIN"
                uyari_var = True
                if (current_price > pivot and current_price < ema_val) or \
                   (current_price < pivot and current_price > ema_val):
                    sinyal_txt += " (Trend Tersi!)"
            
            if uyari_var: yeni_sinyal = True
                
            veriler.append({
                "Borsa": exc_id.upper(),
                "Coin": orig_name,
                "Fiyat": current_price,
                "Pivot": round(pivot, 4),
                "Fark (%)": round(fark, 2),
                "RSI": rsi_val,
                "Trend": trend,
                "Durum": durum,  # <-- Geri Geldi
                "Sinyal": sinyal_txt,
            })
            
        except Exception as e: pass
        
        status_text.text(f"Taranıyor: {orig_name}...")
        progress_bar.progress((i + 1) / len(items))
        
    progress_bar.empty()
    status_text.empty()
    
    if yeni_sinyal and sesli_uyari: ses_cal()
    
    st.session_state.son_guncelleme = datetime.now().strftime('%H:%M:%S')
    return pd.DataFrame(veriler)

# --- ARAYÜZ AKIŞI ---
st.title(f"🦁 Pro Pivot Terminali: {secilen_pivot_isim}")

# 1. Tarama Tetikleyicisi
run_scan = False
if tara_buton:
    run_scan = True
elif oto_yenile:
    run_scan = True

# 2. Tarama İşlemi
if run_scan:
    with st.spinner(f'{secilen_pivot_isim} verileri taranıyor...'):
        df_sonuc = tarama_yap(pivot_tf)
        st.session_state.df = df_sonuc

# 3. Sonuç Gösterimi
if not st.session_state.df.empty:
    df = st.session_state.df
    st.info(f"Son Güncelleme: {st.session_state.son_guncelleme} | Referans: {secilen_pivot_isim} | EMA: {ema_periyot}")
    
    # Tam ekran tablo (use_container_width=True)
    st.dataframe(
        df[['Borsa', 'Coin', 'Fiyat', 'Pivot', 'Fark (%)', 'RSI', 'Trend', 'Durum', 'Sinyal']].style.applymap(
            lambda x: 'color: green' if 'YÜKSELİŞ' in str(x) else 'color: red' if 'DÜŞÜŞ' in str(x) else '', subset=['Trend']
        ).format({"Fiyat": "{:.4f}", "RSI": "{:.2f}", "Pivot": "{:.4f}"}),
        height=700, 
        use_container_width=True
    )

else:
    st.warning("Henüz tarama yapılmadı. Sol menüden 'Taramayı Başlat' butonuna basın.")

if oto_yenile:
    time.sleep(yenileme_hizi)
    st.rerun()