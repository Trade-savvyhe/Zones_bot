import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import json
import os
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Configuration (Must be first Streamlit command)
st.set_page_config(
    page_title="SIGNAL AI | Sentinel Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Live Screen & Trigger Auto-Refresh (Every 5 seconds)
st_autorefresh(interval=5000, key="terminal_refresher")

# 2. Database Engine (JSON File Persistence)
DATA_FILE = "zones_database.json"

DEFAULT_DATA = {
    "channels": ["Gold Sniper VIP", "ICT Structure", "SMC Masters"],
    "zones": []
}

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(DEFAULT_DATA, f, indent=4)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DATA

def save_data():
    payload = {
        "channels": st.session_state.channels,
        "zones": st.session_state.zones
    }
    with open(DATA_FILE, "w") as f:
        json.dump(payload, f, indent=4)

# Initialize Session State
if "db_initialized" not in st.session_state:
    db = load_data()
    st.session_state.channels = db.get("channels", DEFAULT_DATA["channels"])
    st.session_state.zones = db.get("zones", DEFAULT_DATA["zones"])
    st.session_state.db_initialized = True

if "editing_zone_id" not in st.session_state:
    st.session_state.editing_zone_id = None

# 3. Responsive Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; box-sizing: border-box; }
    .stApp { background-color: #0c0d12 !important; color: #f1f5f9; }

    section[data-testid="stSidebar"] {
        background: #11131a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(18, 20, 29, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 10px 16px;
        margin-bottom: 14px;
        backdrop-filter: blur(12px);
    }
    .brand-title {
        font-size: 1.15rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .nav-pill {
        background: rgba(255, 75, 43, 0.12);
        border: 1px solid rgba(255, 75, 43, 0.35);
        color: #ff6b4a;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.72rem;
        font-weight: 700;
    }

    .stats-card {
        background: linear-gradient(180deg, #171923 0%, #12131b 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }

    .signal-card {
        background: linear-gradient(180deg, #171923 0%, #12131b 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
    }
    .signal-card.triggered {
        border: 1px solid #ff4b2b;
        box-shadow: 0 0 20px rgba(255, 75, 43, 0.25);
    }
    .signal-card.win-card {
        border: 1px solid #10b981;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.2);
    }
    .signal-card.loss-card {
        border: 1px solid #ef4444;
        box-shadow: 0 0 15px rgba(239, 68, 68, 0.2);
    }

    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    .asset-icon-box {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .coin-badge {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #f59e0b;
        color: #000;
        font-weight: 800;
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .coin-badge.xau { background: #38bdf8; color: #000; }
    .coin-badge.forex { background: #10b981; color: #000; }

    .asset-title { font-weight: 700; font-size: 0.95rem; color: #fff; margin: 0; }
    .channel-tag { font-size: 0.68rem; color: #64748b; font-weight: 600; text-transform: uppercase; }

    .badge-buy {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.65rem;
    }
    .badge-sell {
        background: rgba(244, 114, 182, 0.12);
        border: 1px solid rgba(244, 114, 182, 0.3);
        color: #f472b6;
        padding: 2px 7px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.65rem;
    }

    .data-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        margin: 10px 0;
        text-align: left;
    }
    .data-item-label { font-size: 0.62rem; color: #64748b; font-weight: 600; }
    .data-item-val { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 0.9rem; color: #f8fafc; }

    .bar-bg {
        background: rgba(255, 255, 255, 0.06);
        height: 8px;
        border-radius: 8px;
        overflow: hidden;
        margin: 10px 0;
    }
    .bar-fill {
        height: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
    }
    .bar-fill.safe {
        background: linear-gradient(90deg, #059669, #10b981);
    }

    .card-footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .proximity-percent {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 800;
        color: #fff;
    }
    .status-pill {
        font-size: 0.62rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 12px;
        text-transform: uppercase;
    }
    .status-pill.running { background: rgba(255, 75, 43, 0.15); color: #ff6b4a; border: 1px solid rgba(255, 75, 43, 0.3); }
    .status-pill.watching { background: rgba(255, 255, 255, 0.05); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.1); }
    .status-pill.win { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .status-pill.loss { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }

    .edit-box {
        background: #141721;
        border: 1px solid #3b82f6;
        border-radius: 10px;
        padding: 12px;
        margin-top: 8px;
        margin-bottom: 12px;
    }

    div.stButton > button {
        border-radius: 8px !important;
        font-size: 0.75rem !important;
        padding: 4px 6px !important;
        font-weight: 600 !important;
    }

    @media (max-width: 768px) {
        .brand-title { font-size: 1rem; }
        .data-item-val { font-size: 0.8rem; }
        .proximity-percent { font-size: 1rem; }
        .data-grid { gap: 4px; }
        .stats-card { padding: 12px; }
    }
</style>
""", unsafe_allow_html=True)

# 4. Webhook Dispatch Engine
DEFAULT_DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1543195984127856661/rgUCroi79KxyYjPfc00P7kEN_vK3pOYrxSWBRBN5ws22IeGtZ2eDGIWy22C5Lq4_HM5r"

def send_discord_rich_alert(webhook_url, channel_name, asset, zone_type, cur_price, low, high):
    if not webhook_url:
        return False
    color_code = 3447003 if "BUY" in zone_type else 15158332
    embed_data = {
        "username": "Apex Signal AI",
        "avatar_url": "https://cdn-icons-png.flaticon.com/512/2620/2620600.png",
        "embeds": [
            {
                "title": f"🚨 ZONE REACHED: {asset}",
                "description": f"**Channel:** `{channel_name}`\n**Bias:** `{zone_type}`\nPrice entered zone range.",
                "color": color_code,
                "fields": [
                    {"name": "Current Price", "value": f"`${cur_price:,.2f}`" if "Gold" in asset or "BTC" in asset else f"`{cur_price:.5f}`", "inline": True},
                    {"name": "Zone Bounds", "value": f"`{low} - {high}`", "inline": True},
                    {"name": "Channel", "value": f"`{channel_name}`", "inline": True}
                ],
                "footer": {"text": f"Signal AI • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
            }
        ]
    }
    try:
        res = requests.post(webhook_url, json=embed_data, timeout=5)
        return res.status_code in [200, 204]
    except Exception:
        return False

# 5. Asset Registry
ASSET_MAP = {
    "XAU/USD (Gold)": {"sym": "GC=F", "icon": "XAU", "class": "xau"},
    "BTC/USD (Bitcoin)": {"sym": "BTC-USD", "icon": "₿", "class": ""},
    "EUR/USD": {"sym": "EURUSD=X", "icon": "€", "class": "forex"},
    "GBP/USD": {"sym": "GBPUSD=X", "icon": "£", "class": "forex"},
    "USD/JPY": {"sym": "JPY=X", "icon": "¥", "class": "forex"}
}

# 6. Real-Time Multi-Feed Market Engine
@st.cache_data(ttl=3)
def fetch_live_data(tickers):
    prices = {}
    
    # Live Real-Time Binance Crypto Stream
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=3)
        if r.status_code == 200:
            b_data = r.json()
            prices["BTC/USD (Bitcoin)"] = {
                "price": float(b_data["lastPrice"]),
                "change": float(b_data["priceChangePercent"])
            }
    except Exception:
        prices["BTC/USD (Bitcoin)"] = {"price": 0.0, "change": 0.0}

    # Direct Forex Spot Rate Stream
    fx_rates = {}
    try:
        fx_res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=3)
        if fx_res.status_code == 200:
            fx_rates = fx_res.json().get("rates", {})
    except Exception:
        pass

    # Process Forex & Gold Pairs
    for label, item in tickers.items():
        if "Bitcoin" in label:
            continue
            
        cur = 0.0
        chg = 0.0
        
        # Calculate real-time spot forex
        if label == "EUR/USD" and "EUR" in fx_rates and fx_rates["EUR"] > 0:
            cur = round(1.0 / fx_rates["EUR"], 5)
        elif label == "GBP/USD" and "GBP" in fx_rates and fx_rates["GBP"] > 0:
            cur = round(1.0 / fx_rates["GBP"], 5)
        elif label == "USD/JPY" and "JPY" in fx_rates:
            cur = round(float(fx_rates["JPY"]), 3)
            
        # Spot Gold + Yahoo Tick / Weekend Settlement Fallback
        if cur == 0.0 or "Gold" in label:
            try:
                t_sym = "XAUUSD=X" if "Gold" in label else item["sym"]
                t = yf.Ticker(t_sym)
                df = t.history(period="1d", interval="1m")
                
                if not df.empty:
                    cur = float(df['Close'].iloc[-1])
                    op = float(df['Open'].iloc[0])
                    chg = ((cur - op) / op) * 100
                else:
                    df_daily = t.history(period="5d", interval="1d")
                    if not df_daily.empty:
                        cur = float(df_daily['Close'].iloc[-1])
                        prev = float(df_daily['Close'].iloc[-2]) if len(df_daily) > 1 else cur
                        chg = ((cur - prev) / prev) * 100
            except Exception:
                pass
                
        prices[label] = {"price": cur, "change": chg}
        
    return prices

live_data = fetch_live_data(ASSET_MAP)

# 7. Sidebar Controls
with st.sidebar:
    st.markdown("<h3 style='margin:0;'>⚡ Terminal Command</h3>", unsafe_allow_html=True)
    st.caption("Channel feeds & zone triggers")
    st.markdown("---")

    # Deploy Zone
    with st.expander("➕ Deploy New Zone Card", expanded=True):
        with st.form("new_zone_form", clear_on_submit=True):
            sel_ch = st.selectbox("Channel", st.session_state.channels) if st.session_state.channels else st.selectbox("Channel", ["General"])
            sel_asset = st.selectbox("Asset Pair", list(ASSET_MAP.keys()))
            sel_type = st.radio("Signal Bias", ["BUY ZONE", "SELL ZONE"], horizontal=True)
            in_low = st.number_input("Zone Low Floor", min_value=0.0001, format="%.4f")
            in_high = st.number_input("Zone High Ceiling", min_value=0.0001, format="%.4f")
            
            if st.form_submit_button("Deploy Signal Card", use_container_width=True):
                if in_high >= in_low > 0:
                    new_id = max([z["id"] for z in st.session_state.zones], default=0) + 1
                    st.session_state.zones.append({
                        "id": new_id,
                        "channel": sel_ch,
                        "asset": sel_asset,
                        "type": sel_type,
                        "low": in_low,
                        "high": in_high,
                        "alerted": False,
                        "status": "PENDING"
                    })
                    save_data()
                    st.success("Zone deployed and saved!")
                    st.rerun()
                else:
                    st.error("Ceiling must be >= Floor.")

    # Manage Channels
    with st.expander("📁 Manage Channels", expanded=False):
        with st.form("add_ch_form", clear_on_submit=True):
            new_channel_name = st.text_input("New Channel Name", placeholder="e.g., Tradovate Scalps")
            if st.form_submit_button("Add Channel", use_container_width=True):
                if new_channel_name and new_channel_name.strip() not in st.session_state.channels:
                    st.session_state.channels.append(new_channel_name.strip())
                    save_data()
                    st.rerun()

        if st.session_state.channels:
            st.markdown("---")
            with st.form("del_ch_form", clear_on_submit=True):
                ch_del = st.selectbox("Delete Channel", st.session_state.channels)
                if st.form_submit_button("🗑️ Delete Channel", use_container_width=True):
                    st.session_state.channels = [c for c in st.session_state.channels if c != ch_del]
                    st.session_state.zones = [z for z in st.session_state.zones if z.get("channel") != ch_del]
                    save_data()
                    st.rerun()

    # Discord Settings
    with st.expander("🔔 Discord Webhook", expanded=False):
        discord_webhook = st.text_input("Webhook URL", value=DEFAULT_DISCORD_WEBHOOK, type="password")
        if st.button("🚀 Test Discord Ping", use_container_width=True):
            send_discord_rich_alert(discord_webhook, "Test Node", "XAU/USD (Gold)", "BUY ZONE", 4529.0, 4520.0, 4535.0)
            st.success("Dispatched!")

# 8. Top Navigation Bar
st.markdown(f"""
<div class="top-nav">
    <div class="brand-title">
        <span style="background:#ff4b2b; color:#fff; padding:3px 6px; border-radius:6px; font-size:0.8rem;">⚡</span>
        SIGNAL AI <span style="color:#64748b; font-size:0.75rem; font-weight:500;">/ Sentinel Matrix</span>
    </div>
    <div style="display:flex; gap:8px; align-items:center;">
        <div class="nav-pill">LIVE FEED</div>
        <div style="color:#64748b; font-size:0.75rem; font-family:'JetBrains Mono';">{datetime.now().strftime('%H:%M:%S')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 9. Real-Time Price Strip
p_cols = st.columns(len(ASSET_MAP))
for idx, (asset_label, data) in enumerate(live_data.items()):
    with p_cols[idx]:
        st.metric(
            label=asset_label.split(" ")[0],
            value=f"${data['price']:,.2f}" if "BTC" in asset_label or "Gold" in asset_label else f"{data['price']:.5f}",
            delta=f"{data['change']:+.2f}%"
        )

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 10. Channel Filter
filter_opts = ["All Channels"] + st.session_state.channels
chosen_filter = st.selectbox("🎯 Channel Filter:", filter_opts)

filtered_zones = st.session_state.zones if chosen_filter == "All Channels" else [z for z in st.session_state.zones if z.get("channel") == chosen_filter]

# 11. Performance Win/Loss Donut & Summary
total_wins = sum(1 for z in filtered_zones if z.get("status") == "WIN")
total_losses = sum(1 for z in filtered_zones if z.get("status") == "LOSS")
total_completed = total_wins + total_losses
win_rate = int((total_wins / total_completed) * 100) if total_completed > 0 else 0

stat_c1, stat_c2 = st.columns([1.2, 2.8])

with stat_c1:
    fig = go.Figure(data=[go.Pie(
        labels=["Wins", "Losses", "Untracked"],
        values=[total_wins if total_completed > 0 else 0, total_losses if total_completed > 0 else 0, 1 if total_completed == 0 else 0],
        hole=0.74,
        marker=dict(colors=["#10b981", "#ef4444", "#1e293b"] if total_completed > 0 else ["#1e293b", "#1e293b", "#1e293b"]),
        textinfo="none",
        hoverinfo="label+value"
    )])
    fig.update_layout(
        showlegend=False,
        margin=dict(t=5, b=5, l=5, r=5),
        height=160,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{win_rate}%</b><br><span style='font-size:10px;color:#64748b;'>WIN RATE</span>",
            x=0.5, y=0.5, font_size=20, font_family="JetBrains Mono", font_color="#ffffff", showarrow=False
        )]
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with stat_c2:
    st.markdown(f"""
    <div class="stats-card">
        <div style="font-size: 0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:8px;">{chosen_filter} Performance</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px;">
            <div>
                <div style="font-size:0.68rem; color:#64748b; font-weight:600;">WINS</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.4rem; font-weight:800; color:#34d399;">{total_wins}</div>
            </div>
            <div>
                <div style="font-size:0.68rem; color:#64748b; font-weight:600;">LOSSES</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.4rem; font-weight:800; color:#f87171;">{total_losses}</div>
            </div>
            <div>
                <div style="font-size:0.68rem; color:#64748b; font-weight:600;">ACTIVE</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.4rem; font-weight:800; color:#38bdf8;">{len(filtered_zones) - total_completed}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 12. Signal Feed Grid
if filtered_zones:
    cols = st.columns(3)
    zone_triggered = False

    for idx, zone in enumerate(filtered_zones):
        cur_price = live_data.get(zone["asset"], {}).get("price", 0.0)
        in_zone = zone["low"] <= cur_price <= zone["high"]

        mid = (zone["low"] + zone["high"]) / 2
        spread = max(abs(zone["high"] - zone["low"]), 1.0)
        dist = abs(cur_price - mid)
        proximity = max(0, min(100, int((1 - (dist / (spread * 4))) * 100))) if not in_zone else 100

        is_completed = zone.get("status") in ["WIN", "LOSS"]

        if in_zone and not zone["alerted"] and not is_completed:
            zone_triggered = True
            send_discord_rich_alert(
                discord_webhook,
                zone.get("channel", "General"),
                zone["asset"],
                zone["type"],
                cur_price,
                zone["low"],
                zone["high"]
            )
            zone["alerted"] = True
            save_data()
            st.toast(f"⚡ [{zone.get('channel')}] {zone['asset']} In Zone!", icon="🔔")

        elif not in_zone and zone["alerted"]:
            zone["alerted"] = False
            save_data()

        if zone.get("status") == "WIN":
            card_class = "signal-card win-card"
            status_tag = '<span class="status-pill win">🏆 WIN TRADE</span>'
            bar_color_class = "safe"
        elif zone.get("status") == "LOSS":
            card_class = "signal-card loss-card"
            status_tag = '<span class="status-pill loss">❌ LOSS TRADE</span>'
            bar_color_class = ""
        elif in_zone:
            card_class = "signal-card triggered"
            status_tag = '<span class="status-pill running">🔥 IN ZONE</span>'
            bar_color_class = ""
        else:
            card_class = "signal-card"
            status_tag = '<span class="status-pill watching">◌ WATCHING</span>'
            bar_color_class = "safe" if proximity < 50 else ""

        bias_badge = '<span class="badge-buy">BUY</span>' if "BUY" in zone["type"] else '<span class="badge-sell">SELL</span>'
        asset_info = ASSET_MAP.get(zone["asset"], {"icon": "●", "class": ""})
        formatted_price = f"${cur_price:,.2f}" if "BTC" in zone["asset"] or "Gold" in zone["asset"] else f"{cur_price:.5f}"

        with cols[idx % 3]:
            card_html = (
                f'<div class="{card_class}">'
                f'<div class="card-header-row">'
                f'<div class="asset-icon-box">'
                f'<div class="coin-badge {asset_info["class"]}">{asset_info["icon"]}</div>'
                f'<div>'
                f'<div class="asset-title">{zone["asset"].split(" ")[0]}</div>'
                f'<div class="channel-tag">{zone.get("channel", "General")}</div>'
                f'</div>'
                f'</div>'
                f'<div>{bias_badge}</div>'
                f'</div>'
                f'<div class="data-grid">'
                f'<div><div class="data-item-label">ZONE LOW</div><div class="data-item-val">{zone["low"]}</div></div>'
                f'<div><div class="data-item-label">LIVE PRICE</div><div class="data-item-val" style="color:#ff6b4a;">{formatted_price}</div></div>'
                f'<div><div class="data-item-label">ZONE HIGH</div><div class="data-item-val">{zone["high"]}</div></div>'
                f'</div>'
                f'<div class="bar-bg"><div class="bar-fill {bar_color_class}" style="width: {proximity}%;"></div></div>'
                f'<div class="card-footer-row">'
                f'<div class="proximity-percent">{proximity}% <span style="font-size:0.65rem; color:#64748b;">PROXIMITY</span></div>'
                f'<div>{status_tag}</div>'
                f'</div>'
                f'</div>'
            )
            
            st.markdown(card_html, unsafe_allow_html=True)

            btn_c1, btn_c2, btn_c3, btn_c4, btn_c5 = st.columns([1, 1, 1, 1, 0.8])
            with btn_c1:
                if st.button("🏆 Win", key=f"win_{zone['id']}", use_container_width=True):
                    zone["status"] = "WIN"
                    save_data()
                    st.rerun()
            with btn_c2:
                if st.button("❌ Loss", key=f"loss_{zone['id']}", use_container_width=True):
                    zone["status"] = "LOSS"
                    save_data()
                    st.rerun()
            with btn_c3:
                if st.button("✏️ Edit", key=f"edit_{zone['id']}", use_container_width=True):
                    st.session_state.editing_zone_id = zone["id"] if st.session_state.editing_zone_id != zone["id"] else None
                    st.rerun()
            with btn_c4:
                if st.button("↺ Reset", key=f"rst_{zone['id']}", use_container_width=True):
                    zone["status"] = "PENDING"
                    save_data()
                    st.rerun()
            with btn_c5:
                if st.button("✕", key=f"del_{zone['id']}", use_container_width=True):
                    st.session_state.zones = [z for z in st.session_state.zones if z["id"] != zone["id"]]
                    if st.session_state.editing_zone_id == zone["id"]:
                        st.session_state.editing_zone_id = None
                    save_data()
                    st.rerun()

            if st.session_state.editing_zone_id == zone["id"]:
                with st.container():
                    st.markdown("<div class='edit-box'><b style='color:#38bdf8; font-size:0.85rem;'>✏️ Edit Zone Parameters</b>", unsafe_allow_html=True)
                    with st.form(key=f"edit_form_{zone['id']}"):
                        ch_idx = st.session_state.channels.index(zone["channel"]) if zone["channel"] in st.session_state.channels else 0
                        asset_list = list(ASSET_MAP.keys())
                        asset_idx = asset_list.index(zone["asset"]) if zone["asset"] in asset_list else 0
                        type_idx = 0 if "BUY" in zone["type"] else 1

                        e_ch = st.selectbox("Channel", st.session_state.channels, index=ch_idx)
                        e_asset = st.selectbox("Asset Pair", asset_list, index=asset_idx)
                        e_type = st.radio("Signal Bias", ["BUY ZONE", "SELL ZONE"], index=type_idx, horizontal=True)
                        e_low = st.number_input("Zone Low Floor", value=float(zone["low"]), format="%.4f")
                        e_high = st.number_input("Zone High Ceiling", value=float(zone["high"]), format="%.4f")
                        
                        save_c, cancel_c = st.columns(2)
                        with save_c:
                            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                if e_high >= e_low > 0:
                                    zone["channel"] = e_ch
                                    zone["asset"] = e_asset
                                    zone["type"] = e_type
                                    zone["low"] = e_low
                                    zone["high"] = e_high
                                    zone["alerted"] = False
                                    st.session_state.editing_zone_id = None
                                    save_data()
                                    st.success("Zone updated successfully!")
                                    st.rerun()
                                else:
                                    st.error("Ceiling must be >= Floor.")
                        with cancel_c:
                            if st.form_submit_button("Cancel", use_container_width=True):
                                st.session_state.editing_zone_id = None
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    if zone_triggered:
        st.markdown("""
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)

else:
    st.markdown(f"""
        <div style="text-align:center; padding: 40px; border: 1px dashed rgba(255,255,255,0.08); border-radius: 14px; color: #64748b;">
            No signal cards active under <b>{chosen_filter}</b>.<br>Deploy a new zone in the sidebar to populate this feed.
        </div>
    """, unsafe_allow_html=True)
