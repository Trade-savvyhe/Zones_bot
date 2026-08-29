import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# 1. Page Setup
st.set_page_config(
    page_title="SIGNAL AI | Sentinel Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh cycle (10 seconds)
st_autorefresh(interval=10000, key="terminal_refresher")

# 2. Ultra-Modern Dark Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; }
    .stApp { background-color: #0c0d12 !important; color: #f1f5f9; }

    /* Custom Glass Sidebar */
    section[data-testid="stSidebar"] {
        background: #11131a !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Top Brand Navigation Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(18, 20, 29, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 12px 24px;
        margin-bottom: 18px;
        backdrop-filter: blur(12px);
    }
    .brand-title {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: 0.05em;
        background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .nav-pill {
        background: rgba(255, 75, 43, 0.12);
        border: 1px solid rgba(255, 75, 43, 0.35);
        color: #ff6b4a;
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.78rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* Performance Analytics Banner */
    .stats-card {
        background: linear-gradient(180deg, #171923 0%, #12131b 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 18px 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }

    /* Signal Cards */
    .signal-card {
        background: linear-gradient(180deg, #171923 0%, #12131b 100%);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 18px;
        padding: 20px;
        position: relative;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.6);
        margin-bottom: 15px;
    }
    .signal-card.triggered {
        border: 1px solid #ff4b2b;
        box-shadow: 0 0 25px rgba(255, 75, 43, 0.25);
    }
    .signal-card.win-card {
        border: 1px solid #10b981;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
    }
    .signal-card.loss-card {
        border: 1px solid #ef4444;
        box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
    }

    /* Card Elements */
    .card-header-row {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 15px;
    }
    .asset-icon-box {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .coin-badge {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #f59e0b;
        color: #000;
        font-weight: 800;
        font-size: 0.85rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .coin-badge.xau { background: #38bdf8; color: #000; }
    .coin-badge.forex { background: #10b981; color: #000; }

    .asset-title { font-weight: 700; font-size: 1.05rem; color: #fff; margin: 0; line-height: 1.2; }
    .channel-tag { font-size: 0.72rem; color: #64748b; font-weight: 600; text-transform: uppercase; }

    .badge-buy {
        background: rgba(56, 189, 248, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.68rem;
    }
    .badge-sell {
        background: rgba(244, 114, 182, 0.12);
        border: 1px solid rgba(244, 114, 182, 0.3);
        color: #f472b6;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 0.68rem;
    }

    .data-grid {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        margin: 14px 0 10px 0;
    }
    .data-item-label { font-size: 0.68rem; color: #64748b; font-weight: 600; letter-spacing: 0.05em; }
    .data-item-val { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 1.05rem; color: #f8fafc; }

    /* Progress Glow Bar */
    .bar-bg {
        background: rgba(255, 255, 255, 0.06);
        height: 10px;
        border-radius: 10px;
        overflow: hidden;
        margin: 14px 0 12px 0;
        position: relative;
    }
    .bar-fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, #ff416c, #ff4b2b);
        box-shadow: 0 0 12px rgba(255, 75, 43, 0.6);
    }
    .bar-fill.safe {
        background: linear-gradient(90deg, #059669, #10b981);
        box-shadow: 0 0 12px rgba(16, 185, 129, 0.6);
    }

    .card-footer-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 4px;
    }
    .proximity-percent {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.35rem;
        font-weight: 800;
        color: #fff;
    }
    .status-pill {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        padding: 4px 10px;
        border-radius: 20px;
        text-transform: uppercase;
    }
    .status-pill.running { background: rgba(255, 75, 43, 0.15); color: #ff6b4a; border: 1px solid rgba(255, 75, 43, 0.3); }
    .status-pill.watching { background: rgba(255, 255, 255, 0.05); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.1); }
    .status-pill.win { background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }
    .status-pill.loss { background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
</style>
""", unsafe_allow_html=True)

# 3. Notification Dispatch Functions
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
                "description": f"**Channel Provider:** `{channel_name}`\n**Bias:** `{zone_type}`\nPrice has entered your designated execution zone.",
                "color": color_code,
                "fields": [
                    {"name": "Current Price", "value": f"`${cur_price:,.2f}`" if "Gold" in asset or "BTC" in asset else f"`{cur_price:.5f}`", "inline": True},
                    {"name": "Zone Bounds", "value": f"`{low} - {high}`", "inline": True},
                    {"name": "Provider", "value": f"`{channel_name}`", "inline": True}
                ],
                "footer": {"text": f"Signal AI Telemetry • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
            }
        ]
    }
    try:
        res = requests.post(webhook_url, json=embed_data, timeout=5)
        return res.status_code in [200, 204]
    except Exception:
        return False

# 4. State Management
ASSET_MAP = {
    "XAU/USD (Gold)": {"sym": "GC=F", "icon": "XAU", "class": "xau"},
    "BTC/USD (Bitcoin)": {"sym": "BTC-USD", "icon": "₿", "class": ""},
    "EUR/USD": {"sym": "EURUSD=X", "icon": "€", "class": "forex"},
    "GBP/USD": {"sym": "GBPUSD=X", "icon": "£", "class": "forex"},
    "USD/JPY": {"sym": "JPY=X", "icon": "¥", "class": "forex"}
}

if "channels" not in st.session_state:
    st.session_state.channels = ["Gold Sniper VIP", "ICT Structure", "SMC Masters"]

if "zones" not in st.session_state:
    st.session_state.zones = [
        {"id": 1, "channel": "Gold Sniper VIP", "asset": "XAU/USD (Gold)", "type": "BUY ZONE", "low": 4700.0, "high": 4705.0, "alerted": False, "status": "PENDING"},
        {"id": 2, "channel": "ICT Structure", "asset": "XAU/USD (Gold)", "type": "SELL ZONE", "low": 4650.0, "high": 4655.0, "alerted": False, "status": "WIN"},
        {"id": 3, "channel": "SMC Masters", "asset": "BTC/USD (Bitcoin)", "type": "BUY ZONE", "low": 76000.0, "high": 76500.0, "alerted": False, "status": "LOSS"},
    ]

# 5. Sidebar Controls
with st.sidebar:
    st.markdown("<h3 style='margin:0;'>⚡ Terminal Command</h3>", unsafe_allow_html=True)
    st.caption("Channel feeds & zone triggers")
    st.markdown("---")

    # Add Zone
    with st.expander("➕ Deploy New Zone Card", expanded=True):
        with st.form("new_zone_form", clear_on_submit=True):
            sel_ch = st.selectbox("Channel", st.session_state.channels)
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
                    st.success("Signal card generated!")
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
                    st.rerun()

        if st.session_state.channels:
            st.markdown("---")
            with st.form("del_ch_form", clear_on_submit=True):
                ch_del = st.selectbox("Delete Channel", st.session_state.channels)
                if st.form_submit_button("🗑️ Delete Channel", use_container_width=True):
                    st.session_state.channels = [c for c in st.session_state.channels if c != ch_del]
                    st.session_state.zones = [z for z in st.session_state.zones if z.get("channel") != ch_del]
                    st.rerun()

    # Webhook
    with st.expander("🔔 Discord Webhook", expanded=False):
        discord_webhook = st.text_input("Webhook URL", value=DEFAULT_DISCORD_WEBHOOK, type="password")
        if st.button("🚀 Test Discord Ping", use_container_width=True):
            send_discord_rich_alert(discord_webhook, "Test Node", "XAU/USD (Gold)", "BUY ZONE", 4529.0, 4520.0, 4535.0)
            st.success("Dispatched!")

# 6. Live Feed
@st.cache_data(ttl=8)
def fetch_live_data(tickers):
    prices = {}
    for label, item in tickers.items():
        try:
            t = yf.Ticker(item["sym"])
            df = t.history(period="1d", interval="1m")
            if not df.empty:
                cur = float(df['Close'].iloc[-1])
                op = float(df['Open'].iloc[0])
                chg = ((cur - op) / op) * 100
                prices[label] = {"price": cur, "change": chg}
            else:
                prices[label] = {"price": 0.0, "change": 0.0}
        except Exception:
            prices[label] = {"price": 0.0, "change": 0.0}
    return prices

live_data = fetch_live_data(ASSET_MAP)

# 7. Navigation Bar UI
st.markdown(f"""
<div class="top-nav">
    <div class="brand-title">
        <span style="background:#ff4b2b; color:#fff; padding:4px 8px; border-radius:8px; font-size:0.9rem;">⚡</span>
        SIGNAL AI <span style="color:#64748b; font-size:0.85rem; font-weight:500;">/ Sentinel Matrix</span>
    </div>
    <div style="display:flex; gap:12px; align-items:center;">
        <div class="nav-pill">⚡ SIGNAL FEED</div>
        <div style="color:#64748b; font-size:0.8rem; font-family:'JetBrains Mono';">{datetime.now().strftime('%H:%M:%S')}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 8. Top Live Price Matrix
p_cols = st.columns(len(ASSET_MAP))
for idx, (asset_label, data) in enumerate(live_data.items()):
    with p_cols[idx]:
        st.metric(
            label=asset_label.split(" ")[0],
            value=f"${data['price']:,.2f}" if "BTC" in asset_label or "Gold" in asset_label else f"{data['price']:.5f}",
            delta=f"{data['change']:+.2f}%"
        )

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# 9. Main Filter Bar (Channel Selector)
filter_col1, filter_col2 = st.columns([2.5, 7.5])
with filter_col1:
    filter_opts = ["All Channels"] + st.session_state.channels
    chosen_filter = st.selectbox("🎯 Active Channel Filter:", filter_opts)

# Filter the list of zones based on user selection
filtered_zones = st.session_state.zones if chosen_filter == "All Channels" else [z for z in st.session_state.zones if z.get("channel") == chosen_filter]

# 10. Channel-Specific Win/Loss Performance Analytics Ring Chart
total_wins = sum(1 for z in filtered_zones if z.get("status") == "WIN")
total_losses = sum(1 for z in filtered_zones if z.get("status") == "LOSS")
total_completed = total_wins + total_losses
win_rate = int((total_wins / total_completed) * 100) if total_completed > 0 else 0

st.markdown(f"### 📊 Performance Analytics: <span style='color:#38bdf8;'>{chosen_filter}</span>", unsafe_allow_html=True)
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
        margin=dict(t=10, b=10, l=10, r=10),
        height=190,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(
            text=f"<b>{win_rate}%</b><br><span style='font-size:11px;color:#64748b;'>WIN RATE</span>",
            x=0.5, y=0.5, font_size=24, font_family="JetBrains Mono", font_color="#ffffff", showarrow=False
        )]
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with stat_c2:
    st.markdown(f"""
    <div class="stats-card">
        <div style="font-size: 0.85rem; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px;">Overview for {chosen_filter}</div>
        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:16px;">
            <div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:600;">CHANNEL WINS</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.6rem; font-weight:800; color:#34d399;">{total_wins}</div>
            </div>
            <div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:600;">CHANNEL LOSSES</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.6rem; font-weight:800; color:#f87171;">{total_losses}</div>
            </div>
            <div>
                <div style="font-size:0.75rem; color:#64748b; font-weight:600;">ACTIVE CARDS</div>
                <div style="font-family:'JetBrains Mono'; font-size:1.6rem; font-weight:800; color:#38bdf8;">{len(filtered_zones) - total_completed}</div>
            </div>
        </div>
        <div style="margin-top:14px; font-size:0.75rem; color:#64748b;">
            💡 Showing cards & stats solely under <b>{chosen_filter}</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

# 11. Signal Feed Grid
if filtered_zones:
    cols = st.columns(3)
    zone_triggered = False

    for idx, zone in enumerate(filtered_zones):
        cur_price = live_data.get(zone["asset"], {}).get("price", 0.0)
        in_zone = zone["low"] <= cur_price <= zone["high"]

        # Proximity percentage calculation
        mid = (zone["low"] + zone["high"]) / 2
        spread = max(abs(zone["high"] - zone["low"]), 1.0)
        dist = abs(cur_price - mid)
        proximity = max(0, min(100, int((1 - (dist / (spread * 4))) * 100))) if not in_zone else 100

        # Disarm alerts once marked WIN or LOSS
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
            st.toast(f"⚡ [{zone.get('channel')}] {zone['asset']} In Zone!", icon="🔔")

        elif not in_zone and zone["alerted"]:
            zone["alerted"] = False

        # Card Status UI States
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
                f'<div class="proximity-percent">{proximity}% <span style="font-size:0.7rem; color:#64748b; font-weight:600;">PROXIMITY</span></div>'
                f'<div>{status_tag}</div>'
                f'</div>'
                f'</div>'
            )
            
            st.markdown(card_html, unsafe_allow_html=True)

            # Action Controls (Win, Loss, Reset, Delete)
            btn_c1, btn_c2, btn_c3, btn_c4 = st.columns([1, 1, 1, 0.8])
            with btn_c1:
                if st.button("🏆 Win", key=f"win_{zone['id']}", use_container_width=True):
                    zone["status"] = "WIN"
                    st.rerun()
            with btn_c2:
                if st.button("❌ Loss", key=f"loss_{zone['id']}", use_container_width=True):
                    zone["status"] = "LOSS"
                    st.rerun()
            with btn_c3:
                if st.button("↺ Reset", key=f"rst_{zone['id']}", use_container_width=True):
                    zone["status"] = "PENDING"
                    st.rerun()
            with btn_c4:
                if st.button("✕ Del", key=f"del_{zone['id']}", use_container_width=True):
                    st.session_state.zones = [z for z in st.session_state.zones if z["id"] != zone["id"]]
                    st.rerun()

    # Browser Sound Alarm
    if zone_triggered:
        st.markdown("""
        <audio autoplay>
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """, unsafe_allow_html=True)

else:
    st.markdown(f"""
        <div style="text-align:center; padding: 60px; border: 1px dashed rgba(255,255,255,0.08); border-radius: 20px; color: #64748b;">
            No signal cards active under <b>{chosen_filter}</b>.<br>Deploy a new zone in the sidebar to populate this channel.
        </div>
    """, unsafe_allow_html=True)