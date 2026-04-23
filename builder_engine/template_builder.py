# Template APK Builder - Phase 2
"""
Template-based APK builder that modifies pre-compiled Android client
Instead of building from scratch, injects server config into template
"""

import os
import json
import shutil
import uuid
from datetime import datetime
import zipfile
import tempfile

class TemplateAPKBuilder:
    def __init__(self):
        self.templates_dir = "builder_engine/templates"
        self.output_dir = "payloads"
        self.template_apk = os.path.join(self.templates_dir, "client_template.apk")

    def create_template_apk(self, server_url, admin_id, app_name="UAMS_Client"):
        """
        Create APK by modifying template with server config
        """
        try:
            # Generate unique payload ID
            payload_id = str(uuid.uuid4())[:8]

            # Create output filename
            output_filename = f"{app_name}_{payload_id}.apk"
            output_path = os.path.join(self.output_dir, output_filename)

            # Ensure output directory exists
            os.makedirs(self.output_dir, exist_ok=True)

            # For now, create a placeholder APK (we'll add real template later)
            # In production, this would extract template.apk, modify assets/config.json, re-sign

            # Create a simple config that would be injected
            config = {
                "server_url": server_url,
                "admin_id": admin_id,
                "payload_id": payload_id,
                "created_at": datetime.now().isoformat(),
                "app_name": app_name
            }

            # Save config for reference
            config_path = os.path.join(self.output_dir, f"config_{payload_id}.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)

            # For demonstration, create a dummy APK file
            # In real implementation, this would be the modified template
            with open(output_path, 'wb') as f:
                f.write(b"APK_TEMPLATE_MODIFIED_" + json.dumps(config).encode())

            return {
                "success": True,
                "payload_id": payload_id,
                "apk_path": output_path,
                "download_url": f"/download/{output_filename}",
                "config": config
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_payloads_list(self):
        """Get list of created payloads"""
        try:
            payloads = []
            if os.path.exists(self.output_dir):
                for file in os.listdir(self.output_dir):
                    if file.endswith('.json') and file.startswith('config_'):
                        config_path = os.path.join(self.output_dir, file)
                        with open(config_path, 'r') as f:
                            config = json.load(f)
                            payloads.append(config)
            return payloads
        except Exception as e:
            return []

# Global instance
template_builder = TemplateAPKBuilder()