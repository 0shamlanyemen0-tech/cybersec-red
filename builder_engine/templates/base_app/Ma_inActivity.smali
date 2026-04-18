# builder_engine/templates/base_app/smali/com/example/app/MainActivity.smali
.class public Lcom/example/app/MainActivity;
.super Landroid/app/Activity;

.field private static final TAG:Ljava/lang/String; = "BaseApp"

# Direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 12
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    return-void
.end method

# Virtual methods
.method protected onCreate(Landroid/os/Bundle;)V
    .locals 2

    .prologue
    .line 17
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 19
    const v0, 0x7f030001  # layout/activity_main
    invoke-virtual {p0, v0}, Lcom/example/app/MainActivity;->setContentView(I)V

    .line 21
    const-string v0, "BaseApp"
    const-string v1, "Application started"
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 23
    # Start background service
    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/example/app/BackgroundService;
    invoke-direct {v0, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    invoke-virtual {p0, v0}, Lcom/example/app/MainActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    .line 25
    return-void
.end method

.method protected onDestroy()V
    .locals 0

    .prologue
    .line 30
    invoke-super {p0}, Landroid/app/Activity;->onDestroy()V

    .line 31
    return-void
.end method