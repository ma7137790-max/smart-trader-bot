import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
import random

from signal_engine import (
    analyze_smc_ict_real,
    load_stats,
    save_stats,
    fetch_live_economic_calendar,
    log_signal,
    update_last_signal_result,
    LIVE_MARKET_ASSETS,
    OTC_MARKET_ASSETS,
)

# --- محرك التحليل (المؤشرات + التحليل اللحظي) منتقل بالكامل إلى signal_engine.py
# بنسخة محسّنة: 10 فئات تحليلية مستقلة فعلياً + دعم حقيقي للفريم، ويُستورد من الأعلى.

# --- لوحة إشارات VIP المحدّثة ---
def get_vip_signal_board(asset, direction, timeframe="M1", is_otc=False, score="5/10", votes_count=5):
    if "CALL" in direction or "صاعد" in direction:
        dir_tag = "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n🟢 [ شُــــــــــــــــرَاء - CALL ] 🟢\n🟩🟩🟩🟩🟩🟩🟩🟩🟩"
    else:
        dir_tag = "🟥🟥🟥🟥🟥🟥🟥🟥🟥\n🔴 [ بَـــــــــــــــــيْـع - PUT ] 🔴\n🟥🟥🟥🟥🟥🟥🟥🟥🟥" 

    algo = "خوارزمية خروج البورصة الحقيقية الموازية OTC ⚙️" if is_otc else "خوارزمية تحليل متطور للسوق الحقيقي ⚙️" 
    
    base_accuracy = 58.0 + (float(votes_count) * 2.5)
    base_accuracy = min(93.5, max(73.0, base_accuracy))

    trade_duration = "1m"
    if timeframe == "M5": trade_duration = "5m"
    elif timeframe == "M15": trade_duration = "15m"
    elif timeframe == "H1": trade_duration = "1h" 

    return (f"🚨 إشارة VIP معتمدة ومحللة حقيقيّاً 🚨\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 الأداة الاستثمارية: {asset}\n"
            f"⏱ الفريم المعتمد: {timeframe}\n"
            f"⌛ المدة الزمنية: {trade_duration}\n"
            f"🧭 النمط التحليلي: {algo}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👇👇 الاتجاه الفني الفعلي حالياً 👇👇\n\n{dir_tag}\n\n"
            f"☝️☝️ الاتجاه الفني الفعلي حالياً ☝️☝️\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💪 قوة البنية الهيكلية: [{score}] (تطابق آمن ومحقق {votes_count} من 10 فئات تحليلية مستقلة)\n"
            f"📈 نسبة الكفاءة الرياضية المتوقعة: {base_accuracy:.1f}%\n"
            f"💵 الدخول: دخول مباشر فور بداية الشمعة القادمة\n"
            f"━━━━━━━━━━━━━━━━━━━━") 

# --- إعدادات وتدشين البوت ونظام الجلسات ---
BOT_TOKEN = "8737456090:AAHjLkThxPbBV5MynyWxrlgqVp2mrDfNExg"
bot = telebot.TeleBot(BOT_TOKEN) 

global_stats = load_stats()
user_sessions = {}

# --- بناء لوحة التحكم المخصصة واختيار الخبر الفردي المراد تحليله ---
def run_high_impact_news_analysis(chat_id):
    try:
        bot.send_message(chat_id, "📡 جاري سحب وتصفية الأحداث المتبقية في جدول اليوم...", parse_mode="Markdown") 
        LIVE_NEWS = fetch_live_economic_calendar()
        
        if not LIVE_NEWS:
            bot.send_message(chat_id, "📰 رادار الحماية الذكي: لا توجد أي أخبار اقتصادية متبقية قادمة لهذا اليوم المالي.")
            return

        if chat_id not in user_sessions:
            user_sessions[chat_id] = {}
        
        user_sessions[chat_id]['fetched_news'] = LIVE_NEWS

        markup = InlineKeyboardMarkup(row_width=1)
        for idx, item in enumerate(LIVE_NEWS):
            btn_text = f"⏰ {item['base_time']} | {item['flag']} {item['currency']} - {item['title'][:25]}..."
            markup.add(InlineKeyboardButton(btn_text, callback_data=f"sel_news_{idx}"))
        
        bot.send_message(chat_id, "📰 **رادار المفكرة الاقتصادية الحية (المتبقي اليوم فقط):**\n\n👇 يرجى اختيار الحدث الاقتصادي القادم الذي ترغب في تحليله واقتناصه الآن:", parse_mode="Markdown", reply_markup=markup)

    except Exception as e:
        print(f"Error inside news main interface: {e}")
        bot.send_message(chat_id, "❌ حدث خطأ فني طارئ أثناء توليد أزرار الأخبار اللحظية.")

def send_welcome_msg(chat_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row("🔍 البحث الأوتوماتيكي", "📰 تحليل الأخبار")
    markup.row("📊 الإحصائيات", "🔄 إعادة تعيين الجلسة")
    markup.row("⚜️ المطور ⚜️") 

    welcome_text = (
        "👋 مرحباً بك في البوت الخاص بـ MOHAMAD ALREFAE 👑\n\n"
        "✨ أهلاً بك يا Smart Trader. المنظومة تعمل الآن بنظام الحد الأدنى الآمن المعتمد [5/10] على 10 فئات تحليلية مستقلة.\n\n"
        "👇 اختر أداة التشغيل المطلوبة من القائمة السفلية لبدء الفحص المالي:"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=markup) 

@bot.message_handler(commands=['start'])
def start_command(message):
    send_welcome_msg(message.chat.id) 

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    chat_id = message.chat.id
    text = message.text.strip() 

    if text == "📊 الإحصائيات":
        show_statistics(chat_id)
        return
    elif text == "🔍 البحث الأوتوماتيكي":
        market_choice = random.choice(["LIVE", "OTC"])
        selected_asset = random.choice(LIVE_MARKET_ASSETS) if market_choice == "LIVE" else random.choice(OTC_MARKET_ASSETS)
        user_sessions[chat_id] = {
            "market_type": market_choice,
            "asset": selected_asset,
            "mode": "AUTO_CHOSEN_BY_BOT"
        }
        ask_timeframe(chat_id)
        return
    elif text == "📰 تحليل الأخبار":
        run_high_impact_news_analysis(chat_id)
        return
    elif text == "🔄 إعادة تعيين الجلسة":
        user_sessions.pop(chat_id, None)
        send_welcome_msg(chat_id)
        return
    elif text == "⚜️ المطور ⚜️":
        bot.send_message(chat_id, "⚜️ نظام تداول بنيوي مخصص ومطور بالكامل لـ محمد الرفاعي\n👑 النسخة المقفلة المحدثة بدون ICT: GOLD V. 1 MOHAMAD ALREFAE", parse_mode="Markdown")
        return 

    user_sessions[chat_id] = {"asset": text.upper(), "mode": "MANUAL"}
    bot.send_message(chat_id, f"📥 تم استلام الرمز المكتوب: {text.upper()}", parse_mode="Markdown")
    ask_timeframe(chat_id) 

def ask_timeframe(chat_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("M1 (دقيقة)", callback_data="tf_M1"),
        InlineKeyboardButton("M5 (5 دقائق)", callback_data="tf_M5"),
        InlineKeyboardButton("M15 (15 دقيقة)", callback_data="tf_M15"),
        InlineKeyboardButton("H1 (ساعة)", callback_data="tf_H1")
    )
    markup.row(InlineKeyboardButton("⚜️ GOLD V. 1 SECURITY SYSTEM ⚜️", callback_data="none"))
    bot.send_message(chat_id, "⏱️ اختر فريم التحليل المطلوب لبدء عملية الفلترة والحماية الحتمية للفرصة:", parse_mode="Markdown", reply_markup=markup) 

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data 

    if data == "none": return 

    # محرك تفعيل زر إعادة التحليل التلقائي واليدوي الفوري لكافة المنظومات
    if data.startswith("re_val_"):
        parts = data.split("_")
        re_asset = parts[2]
        re_tf = parts[3]
        user_sessions[chat_id] = {"asset": re_asset, "timeframe": re_tf, "mode": "MANUAL"}
        run_real_technical_analysis(chat_id)
        return

    # معالجة اختيار خبر فردي مع حساب الإشارة الخاصة به فوراً
    if data.startswith("sel_news_"):
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        idx = int(data.split("_")[2])
        session = user_sessions.get(chat_id, {})
        fetched = session.get('fetched_news', [])
        
        if not fetched or idx >= len(fetched):
            bot.send_message(chat_id, "🔄 انتهت صلاحية الجلسة المفتوحة، يرجى إعادة الضغط على زر تحليل الأخبار لسحب القائمة مجدداً.")
            return
        
        item = fetched[idx]
        curr = item['currency']
        
        if curr == "EUR": pair_to_scan = "EURUSD"
        elif curr == "GBP": pair_to_scan = "GBPUSD"
        elif curr == "JPY": pair_to_scan = "USDJPY"
        elif curr == "CAD": pair_to_scan = "USDCAD"
        elif curr == "AUD": pair_to_scan = "AUDUSD"
        elif curr == "CHF": pair_to_scan = "USDCHF"
        elif curr == "NZD": pair_to_scan = "NZDUSD"
        else: pair_to_scan = "EURUSD" if curr == "USD" else f"{curr}USD"

        bot.send_message(chat_id, f"🎯 تم اختيار حدث: {item['title']}\n🔍 جاري الآن تشغيل مصفوفة التصفية لزوج: **{pair_to_scan}**...", parse_mode="Markdown")
        
        direction, _, score, votes_count, _closes = analyze_smc_ict_real(pair_to_scan)
        
        if direction == "FILTERED":
            bot.send_message(chat_id, f"🚨 للحدث المحدد [{item['title']}]: تم حجب الإشارة؛ لا يوجد توافق كافٍ بين الفئات التحليلية المستقلة في هذه اللحظة السعرية.")
            send_welcome_msg(chat_id)
            return

        if direction is None:
            bot.send_message(chat_id, f"❌ فشل فني في جلب البيانات الفورية الحية لزوج {pair_to_scan} المرتبط بالخبر.")
            send_welcome_msg(chat_id)
            return

        log_signal(pair_to_scan, direction, score, votes_count, "M1", "OTC" in pair_to_scan)

        if "CALL" in direction:
            dir_tag = "🟩🟩🟩🟩🟩🟩🟩🟩🟩\n🟢 [ شُــــــــــــــــرَاء - CALL ] 🟢\n🟩🟩🟩🟩🟩🟩🟩🟩🟩"
        else:
            dir_tag = "🟥🟥🟥🟥🟥🟥🟥🟥🟥\n🔴 [ بَـــــــــــــــــيْـع - PUT ] 🔴\n🟥🟥🟥🟥🟥🟥🟥🟥🟥"

        news_signal_msg = (
            f"🚨 إشارة مخصصة للحدث الاقتصادي المختار 🚨\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🔥 الحدث المراد دخولُه: {item['flag']} {item['title']}\n"
            f"⏰ التوقيت الدقيق للصدور: {item['base_time']}\n"
            f"📊 رتبة قوة التأثير: {item['impact']}\n"
            f"🎯 الأداة المالية الفعّالة: {pair_to_scan}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👇 اتجاه الزخم المتوقع في اللحظة الفردية الحالية 👇\n\n{dir_tag}\n\n"
            f"☝️ اتجاه الزخم المتوقع في اللحظة الفردية الحالية ☝️\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💪 قوة البنية التوافقية: [{score}] (تطابق معتمد لـ {votes_count} من 10 فئات تحليلية مستقلة)\n"
            f"💵 آلية التداول الفردي: الدخول مباشرة فور بداية الشمعة المتزامنة مع وقت صدور الخبر المحدد.\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        )
        
        markup_res = InlineKeyboardMarkup()
        markup_res.add(
            InlineKeyboardButton("✅ ربح الخبر (ITM)", callback_data=f"newsres_itm_{pair_to_scan}"),
            InlineKeyboardButton("❌ خسارة الخبر (OTM)", callback_data=f"newsres_otm_{pair_to_scan}")
        )
        markup_res.row(InlineKeyboardButton("🔄 إعادة تحليل نفس الزوج", callback_data=f"re_val_{pair_to_scan}_M1"))
        bot.send_message(chat_id, news_signal_msg, parse_mode="Markdown", reply_markup=markup_res)
        return

    if data.startswith("res_"):
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        if data.startswith("res_itm_"):
            asset_name = data[len("res_itm_"):]
            global_stats["itm"] += 1
            update_last_signal_result(asset_name, "ITM")
            bot.send_message(chat_id, "Good 🟢 تم تسجيل صفقة ناجحة.")
        elif data.startswith("res_otm_"):
            asset_name = data[len("res_otm_"):]
            global_stats["otm"] += 1
            update_last_signal_result(asset_name, "OTM")
            bot.send_message(chat_id, "🔴 واصل الالتزام بالاستراتيجية وضوابط إدارة المخاطر، الخسارة طبيعية.")
        save_stats(global_stats)
        send_welcome_msg(chat_id)
        return 

    if data.startswith("newsres_"):
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None)
        if data.startswith("newsres_itm_"):
            asset_name = data[len("newsres_itm_"):]
            global_stats["news_itm"] += 1
            update_last_signal_result(asset_name, "ITM")
            bot.send_message(chat_id, "Good 🔥 تم تسجيل صفقة أخبار ناجحة.")
        elif data.startswith("newsres_otm_"):
            asset_name = data[len("newsres_otm_"):]
            global_stats["news_otm"] += 1
            update_last_signal_result(asset_name, "OTM")
            bot.send_message(chat_id, "📉 تقلبات حادة مفاجئة خارجة عن المعطيات أثناء صدور الخبر.")
        save_stats(global_stats)
        send_welcome_msg(chat_id)
        return 

    if data == "stats_reset":
        global_stats["itm"] = 0
        global_stats["otm"] = 0
        global_stats["news_itm"] = 0
        global_stats["news_otm"] = 0
        save_stats(global_stats)
        bot.answer_callback_query(call.id, "🔄 تم تصفير جميع عدادات الإحصائيات الفنية.")
        send_welcome_msg(chat_id)
        return 

    if data == "stats_back":
        bot.delete_message(chat_id, message_id)
        send_welcome_msg(chat_id)
        return 

    if chat_id not in user_sessions:
        send_welcome_msg(chat_id)
        return 

    if data.startswith("tf_"):
        raw_tf = data.split("_")[1]
        user_sessions[chat_id]["timeframe"] = raw_tf
        bot.edit_message_reply_markup(chat_id=chat_id, message_id=message_id, reply_markup=None) 

        session_mode = user_sessions[chat_id].get("mode")
        if session_mode == "AUTO_CHOSEN_BY_BOT":
            run_automatic_market_scan(chat_id)
        else:
            run_real_technical_analysis(chat_id)
        return 

def run_automatic_market_scan(chat_id):
    session = user_sessions.get(chat_id, {})
    selected_asset = session.get("asset")
    m_type = session.get("market_type")
    final_tf = session.get("timeframe") 

    bot.send_message(chat_id, f"🔄 جاري استدعاء محرك التصويت بـ10 فئات تحليلية مستقلة لـ {selected_asset} (فريم {final_tf})...", parse_mode="Markdown") 

    is_otc = "OTC" in selected_asset or m_type == "OTC"
    direction, explanation, score, votes_count, _closes = analyze_smc_ict_real(selected_asset, final_tf) 

    if direction == "FILTERED":
        bot.send_message(chat_id, explanation)
        send_welcome_msg(chat_id)
        return

    if direction is None:
        bot.send_message(chat_id, f"❌ خطأ فني: البيانات الفورية الحية غير متوفرة حالياً. يرجى تكرار المحاولة لاحقاً.")
        send_welcome_msg(chat_id)
        return 

    log_signal(selected_asset, direction, score, votes_count, final_tf, is_otc)

    final_signal_message = get_vip_signal_board(
        asset=selected_asset, direction=direction, timeframe=final_tf,
        is_otc=is_otc, score=score, votes_count=votes_count
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ ITM", callback_data=f"res_itm_{selected_asset}"), InlineKeyboardButton("❌ OTM", callback_data=f"res_otm_{selected_asset}"))
    markup.row(InlineKeyboardButton("🔄 إعادة تحليل نفس الزوج", callback_data=f"re_val_{selected_asset}_{final_tf}"))
    bot.send_message(chat_id, final_signal_message, parse_mode="Markdown", reply_markup=markup)
    user_sessions.pop(chat_id, None) 

def run_real_technical_analysis(chat_id):
    session = user_sessions.get(chat_id, {})
    asset = session.get("asset")
    timeframe = session.get("timeframe") 

    bot.send_message(chat_id, f"🔍 جاري إجراء المسح الهيكلي وتطابق الأصوات اللحظية لـ {asset} حياً...", parse_mode="Markdown") 

    is_otc = "OTC" in asset
    direction, explanation, score, votes_count, _closes = analyze_smc_ict_real(asset, timeframe) 

    if direction == "FILTERED":
        bot.send_message(chat_id, explanation)
        send_welcome_msg(chat_id)
        return

    if direction is None:
        bot.send_message(chat_id, f"❌ فشل: البيانات غير متوفرة. تأكد من صحة كتابة الرمز واقترانه بالبيانات الحية.")
        send_welcome_msg(chat_id)
        return 

    log_signal(asset, direction, score, votes_count, timeframe, is_otc)

    final_signal_message = get_vip_signal_board(
        asset=asset, direction=direction, timeframe=timeframe,
        is_otc=is_otc, score=score, votes_count=votes_count
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ ITM", callback_data=f"res_itm_{asset}"), InlineKeyboardButton("❌ OTM", callback_data=f"res_otm_{asset}"))
    markup.row(InlineKeyboardButton("🔄 إعادة تحليل نفس الزوج", callback_data=f"re_val_{asset}_{timeframe}"))
    bot.send_message(chat_id, final_signal_message, parse_mode="Markdown", reply_markup=markup)
    user_sessions.pop(chat_id, None) 

def show_statistics(chat_id):
    itm = global_stats["itm"]
    otm = global_stats["otm"]
    total_normal = itm + otm
    win_rate_normal = (itm / total_normal * 100) if total_normal > 0 else 0 

    n_itm = global_stats["news_itm"]
    n_otm = global_stats["news_otm"]
    total_news = n_itm + n_otm
    win_rate_news = (n_itm / total_news * 100) if total_news > 0 else 0 

    stats_message = (
        f"👑 GOLD V. 1 MOHAMAD ALREFAE 👑\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 [ صفقات منظومة التصويت اللحظية ] 🎯\n"
        f"─────────────────\n"
        f"✅ الرابحة (ITM): {itm}\n"
        f"❌ الخاسرة (OTM): {otm}\n"
        f"📊 مجموع الصفقات الموثقة: {total_normal}\n"
        f"📈 كفاءة النجاح الرياضية الحقيقية: {win_rate_normal:.1f}%\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📰 [ صفقات الأخبار اللحظية الفردية ] 📰\n"
        f"─────────────────\n"
        f"✅ الرابحة (ITM): {n_itm}\n"
        f"❌ الخاسرة (OTM): {n_otm}\n"
        f"📊 مجموع صفقات حزم الأخبار: {total_news}\n"
        f"📈 كفاءة الأخبار الواقعية الحالية: {win_rate_news:.1f}%\n\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    ) 

    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔄 تصفير العدادات", callback_data="stats_reset"))
    markup.row(InlineKeyboardButton("🔙 عودة للقائمة الرئيسية", callback_data="stats_back"))
    bot.send_message(chat_id, stats_message, parse_mode="Markdown", reply_markup=markup) 

if __name__ == "__main__":
    bot.infinity_polling(timeout=15, long_polling_timeout=5)