import streamlit as st
import ccxt
import pandas as pd
import time
import plotly.graph_objects as go
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Pro Pivot Terminali V12", layout="wide", page_icon="🦁")

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

pivot_secenekleri = {
    "Günlük (Standart)": "1d",
    "4 Saatlik (Day Trade)": "4h",
    "Haftalık (Swing)": "1w",
    "Aylık (Uzun Vade)": "1M"
}
secilen_pivot_isim = st.sidebar.selectbox("Pivot Zaman Dilimi", list(pivot_secenekleri.keys()), index=0)
pivot_tf = pivot_secenekleri[secilen_pivot_isim]

oto_yenile = st.sidebar.checkbox("Otomatik Yenileme (Döngü)", value=False)
yenileme_hizi = st.sidebar.slider("Döngü Hızı (Saniye)", 10, 300, 60)

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

if tara_buton:
    should_run_scan = True

# Otomatik yenileme kontrolü (Süreye göre)
if oto_yenile:
    gecen_sure = time.time() - st.session_state.last_fetch_time
    if gecen_sure > yenileme_hizi:
        should_run_scan = True

# TARAMA BAŞLAT
if should_run_scan:
    with st.spinner(f'{secilen_pivot_isim} verileri taranıyor...'):
        df_sonuc = tarama_yap(pivot_tf, secilen_pivot_isim)
        st.session_state.df = df_sonuc

# --- GÖSTERİM BÖLÜMÜ ---
if not st.session_state.df.empty:
    df = st.session_state.df
    st.info(f"Son Güncelleme: {st.session_state.son_guncelleme} | Referans: {secilen_pivot_isim} | EMA: {ema_periyot}")
    
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
                st.warning("Veri bulunamadı.")
else:
    st.warning("Henüz tarama yapılmadı. Sol menüden 'Taramayı Başlat' butonuna basın.")

# --- GERİ SAYIM SAYACI ---
if oto_yenile:
    # Kalan süreyi hesapla
    gecen_sure = time.time() - st.session_state.last_fetch_time
    kalan_sure = int(yenileme_hizi - gecen_sure)
    
    # Sayacı göster (Main alanın en altında)
    if kalan_sure > 0:
        # Sayacı güncellemek için anlık döngü
        # Not: Döngü yerine tek tek rerun yapmak tıklamayı zorlaştırıyordu.
        # Bu yüzden burada sadece bilgiyi gösterip 1 saniye uyuyoruz.
        # Streamlit tekrar başa dönüyor.
        
        st.divider()
        st.info(f"⏳ Otomatik yenilemeye yaklaşık **{kalan_sure}** saniye kaldı...")
        time.sleep(1)
        st.rerun()
    else:
        st.rerun()
