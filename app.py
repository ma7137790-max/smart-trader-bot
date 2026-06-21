import streamlit as st
import base64
import os
from datetime import datetime

# استيراد محرك التحليل المشترك (لا يعتمد على تيليجرام، أخف وأسرع للوحة التحكم)
from signal_engine import (
    analyze_smc_ict_real,
    load_stats,
    save_stats,
    LIVE_MARKET_ASSETS,
    OTC_MARKET_ASSETS,
    fetch_live_economic_calendar,
    log_signal,
    update_last_signal_result,
    get_signal_history,
)

# 1. إعدادات الصفحة وثيم التداول
st.set_page_config(page_title="👑 SMART.TRADER VIP - V5", layout="wide")


def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        style = f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/jpg;base64,{b64_encoded}");
            background-size: contain;
            background-repeat: no-repeat;
            background-position: top center;
            background-color: #060a17;
            background-attachment: fixed;
        }}
        [data-testid="stVerticalBlock"] {{
            background-color: rgba(6, 10, 23, 0.92);
            padding: 30px;
            border-radius: 16px;
            border: 1px solid rgba(212, 175, 55, 0.2);
            color: #ffffff;
            margin-top: 15px;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 12px;
            direction: rtl;
        }}
        .stTabs [data-baseweb="tab"] {{
            background-color: rgba(20, 30, 55, 0.85);
            border-radius: 8px 8px 0px 0px;
            padding: 12px 24px;
            color: #d4af37;
            font-weight: bold;
        }}
        h1, h2, h3, h4, p, span, label {{
            text-align: right;
            direction: rtl;
        }}
        </style>
        """
        st.markdown(style, unsafe_allow_html=True)


set_background("5773746578244964145_121.jpg")

st.markdown("<h1 style='text-align: center; color: #d4af37;'>👑 SMART.TRADER VIP 👑</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #ffffff;'>A KINGS' CHAMBER OF TRADING</h3>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #a0aec0; font-size: 14px;'>Dev. MOHAMAD ALREFAE</div>", unsafe_allow_html=True)
st.markdown("---")

# إدارة حالة الرادار والإشارات
if "scanning" not in st.session_state:
    st.session_state.scanning = False
if "last_signal" not in st.session_state:
    st.session_state.last_signal = None
if "scan_pool" not in st.session_state:
    st.session_state.scan_pool = []
if "scan_timeframe" not in st.session_state:
    st.session_state.scan_timeframe = "M1"
if "scan_index" not in st.session_state:
    st.session_state.scan_index = 0

TIMEFRAME_OPTIONS = ["M1", "M5", "M15", "H1"]

tab1, tab2, tab3 = st.tabs(["🔍 رادار الفحص البنيوي والقنص", "📰 رادار الأخبار الاقتصادي حياً", "📊 لوحة التحكم وإحصائياتك"])


def build_asset_pool(market_mode, manual_pair):
    if "1" in market_mode:
        return LIVE_MARKET_ASSETS
    elif "2" in market_mode:
        return OTC_MARKET_ASSETS
    elif "3" in market_mode:
        return LIVE_MARKET_ASSETS + OTC_MARKET_ASSETS
    elif "4" in market_mode:
        return [manual_pair.strip().upper()] if manual_pair.strip() else []
    return []


# --- التبويب الأول ---
with tab1:
    st.header("🎯 نظام مراقبة واقتناص أفضل الصفقات")

    col_mode, col_pair, col_tf = st.columns([2, 2, 1])
    with col_mode:
        market_mode = st.selectbox(
            "🎛️ اختر وضع فرز السوق المطلوبة:",
            [
                "1 - السوق الحقيقي فقط (Real Market Only)",
                "2 - سوق الـ OTC فقط (OTC Market Only)",
                "3 - كافة الأسواق المتاحة (All Assets Both)",
                "4 - كتابة اسم الزوج يدوياً (Search by Pair Name)"
            ]
        )

    with col_pair:
        manual_pair = st.text_input("✍️ [خيار 4] اكتب اسم الزوج هنا يدوياً:", placeholder="مثال: GOLD أو EURUSD")

    with col_tf:
        selected_timeframe = st.selectbox("⏱️ الفريم", TIMEFRAME_OPTIONS, index=0)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 إطلاق رادار المراقبة الحية وثقوب السيولة", use_container_width=True, type="primary"):
            pool = build_asset_pool(market_mode, manual_pair)
            if not pool:
                st.error("⚠️ الرجاء كتابة اسم الأصل بشكل صحيح لتفعيل الخيار 4.")
            else:
                st.session_state.scanning = True
                st.session_state.last_signal = None
                st.session_state.scan_pool = pool
                st.session_state.scan_timeframe = selected_timeframe
                st.session_state.scan_index = 0
    with col_btn2:
        if st.button("🛑 إيقاف الرادار مؤقتاً", use_container_width=True):
            st.session_state.scanning = False

    st.markdown("---")

    # عرض الإشارة وأزرار الربح/الخسارة إذا كانت موجودة في الذاكرة
    if st.session_state.last_signal:
        sig = st.session_state.last_signal
        is_call = "CALL" in sig['direction']
        color = "#00ff80" if is_call else "#ff3333"
        bg_box = "rgba(0, 255, 128, 0.04)" if is_call else "rgba(255, 51, 51, 0.04)"
        dir_text = f"{sig['direction']} ⬆️" if is_call else f"{sig['direction']} ⬇️"

        st.markdown(f"""
        <div style='background-color: {bg_box}; padding: 25px; border-radius: 12px; border: 2px solid {color}; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);'>
            <h2 style='color: {color}; margin-top: 0;'>🚨 تـم اقـتـنـاص إشـارة VIP مـؤكـدة الـجـودة 🚨</h2>
            <p style='font-size: 18px;'><b>الأصل المستهدف:</b> <span style='color: #00e1ff; font-weight: bold;'>{sig['asset']}</span></p>
            <p style='font-size: 16px;'><b>الفريم المعتمد:</b> {sig.get('timeframe', 'M1')}</p>
            <p style='font-size: 20px;'><b>التوصية الفنية المباشرة:</b> <span style='color: {color}; font-weight: bold; background: rgba(0,0,0,0.4); padding: 5px 15px; border-radius: 5px;'>{dir_text}</span></p>
            <p style='font-size: 16px;'><b>الاستراتيجية المطبقة:</b> {sig['strategy']} | <b>التوافق:</b> {sig['candle']}</p>
            <p style='font-size: 16px;'><b>قوة وموثوقية الصفقة:</b> <span style='color: #d4af37;'>{sig['score']}</span></p>
            <hr style='border-color: rgba(255,255,255,0.1);'>
            <p style='color: #a0aec0; font-size: 14px;'><b>تشخيص محرك الزخم:</b><br>{sig['momentum']}</p>
            <br>
            <p style='text-align: left; color: #a0aec0; font-style: italic;'>✍️ MOHAMAD ALREFAE | 📢 smar.trader</p>
        </div>
        """, unsafe_allow_html=True)

        if sig.get("is_otc"):
            st.warning("⚠️ هذا زوج OTC: الإشارة محسوبة من بيانات السوق الحقيقي كأقرب تقريب متاح، وقد تختلف عن تسعير الوسيط الفعلي داخل المنصة.")

        audio_html = """
        <audio autoplay>
            <source src="https://assets.mixkit.co/sfx/preview/mixkit-software-interface-start-2574.mp3" type="audio/mpeg">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)

        st.write("📝 **سجل نتيجة هذه الصفقة يدوياً:**")
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("✅ ربحت الصفقة (ITM)", use_container_width=True):
                stats = load_stats()
                stats["itm"] += 1
                save_stats(stats)
                update_last_signal_result(sig['asset'], "ITM")
                st.session_state.last_signal = None
                st.rerun()
        with btn_col2:
            if st.button("❌ خسرت الصفقة (OTM)", use_container_width=True):
                stats = load_stats()
                stats["otm"] += 1
                save_stats(stats)
                update_last_signal_result(sig['asset'], "OTM")
                st.session_state.last_signal = None
                st.rerun()

    elif st.session_state.scanning:
        @st.fragment(run_every="2.5s")
        def scanning_fragment():
            # الإيقاف الفوري: أول مرور للفراغمنت بعد ضغط زر الإيقاف يتوقف فعلياً
            # بدل انتظار اكتمال دورة الفحص الكاملة كما كان يحدث في النسخة القديمة
            if not st.session_state.scanning or st.session_state.last_signal:
                return

            pool = st.session_state.scan_pool
            timeframe = st.session_state.scan_timeframe

            if not pool:
                st.session_state.scanning = False
                return

            idx = st.session_state.scan_index % len(pool)
            asset = pool[idx]
            st.session_state.scan_index += 1

            st.success("📡 الرادار متصل ويقوم بالبحث عن أفضل صفقة...")
            st.info(f"⏳ جاري فحص بنية وهيكل السيولة لـ {asset} (فريم {timeframe}) ...")

            direction, explanation, score, votes_count, closes = analyze_smc_ict_real(asset, timeframe)

            if closes:
                st.line_chart(closes[-40:], height=120)

            if direction and direction != "FILTERED":
                is_otc = "OTC" in asset
                st.session_state.last_signal = {
                    "asset": asset,
                    "direction": direction,
                    "strategy": "نظام التصويت بـ10 فئات تحليلية مستقلة (SMC + ICT + اتجاه + زخم)",
                    "candle": f"توافق {votes_count} من 10 فئات مستقلة",
                    "score": score,
                    "momentum": explanation if explanation else f"تم تأكيد الإشارة بتوافق {votes_count} من أصل 10 فئات تحليلية مستقلة.",
                    "timeframe": timeframe,
                    "is_otc": is_otc,
                }
                log_signal(asset, direction, score, votes_count, timeframe, is_otc)
                st.session_state.scanning = False
                st.rerun()

        scanning_fragment()
    else:
        st.warning("💤 الرادار في وضع السكون. انقر على الزر بالأعلى للبحث.")

# --- التبويب الثاني ---
with tab2:
    st.header("📰 رادار دفق ومراقبة التأثيرات الإخبارية الحية")
    if st.button("🔄 تحديث ومزامنة جدول التقويم الاقتصادي الآن"):
        with st.spinner("جاري سحب المفكرة والتحليل الاقتصادي المباشر..."):
            news_data = fetch_live_economic_calendar()
            for idx, item in enumerate(news_data[:4], 1):
                impact_color = "#ff3333" if "HIGH" in item['impact'] else "#d4af37"
                st.markdown(f"""
                <div style='background-color: rgba(255,255,255,0.02); padding: 18px; border-radius: 10px; margin-bottom: 12px; border-right: 5px solid {impact_color};'>
                    <h4 style='margin: 0; color: #ffffff;'>📍 {idx}. {item['name']}</h4>
                    <p style='margin: 5px 0 0 0; font-size: 14px; color: #a0aec0;'>درجة تأثير الخبر: <span style='color: {impact_color}; font-weight: bold;'>{item['impact']}</span> | التوقيت: <span style='color: #00e1ff;'>{item['base_time']} (GMT+3)</span></p>
                </div>
                """, unsafe_allow_html=True)

# --- التبويب الثالث ---
with tab3:
    st.header("📊 مراقبة أداء وتوثيق معدلات نجاح النظام التاريخي")
    current_stats = load_stats()
    tot_trades = current_stats["itm"] + current_stats["otm"]
    win_rate = (current_stats["itm"] / tot_trades * 100) if tot_trades > 0 else 0

    st.subheader("🎯 صفقات الرادار التلقائي واليدوي الحية")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="إجمالي الصفقات الناجحة (ITM) ✅", value=current_stats["itm"])
    with c2:
        st.metric(label="إجمالي الصفقات الخاسرة (OTM) ❌", value=current_stats["otm"])
    with c3:
        st.metric(label="نسبة النجاح الإجمالية", value=f"{win_rate:.1f}%")

    st.markdown("---")
    st.subheader("📜 سجل الإشارات التاريخي (لمتابعة الدقة الحقيقية بمرور الوقت)")
    history = get_signal_history(limit=30)
    if history:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.caption("لا يوجد سجل إشارات محفوظ بعد. سيُسجَّل كل إشارة جديدة تلقائياً هنا فور صدورها.")

    st.markdown("---")
    if st.button("🗑️ تصفير وإعادة تعيين كافة العدادات والإحصائيات"):
        blank_stats = {"itm": 0, "otm": 0, "news_itm": 0, "news_otm": 0}
        save_stats(blank_stats)
        st.success("تم تصفير وإعادة تهيئة ملف الإحصائيات الحقيقي بنجاح! يرجى إعادة تحميل الصفحة.")
        st.rerun()
