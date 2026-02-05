# **Distributed Cluster Persistence & Automation Log**

This document details the transition from manual command-line execution to system-level automation for the **Dell Lighthouse** (Master) and **Ultra 7 Muscle** (Worker).

## ---

**1\. The Dell "Lighthouse" (Master Node)**

### **The Automation Hurdle**

The primary challenge was systemd isolation. Unlike a manual terminal session, systemd operates in a restricted environment where PATH and JAVA\_HOME are not inherited.

**Initial Failures:**

* exit-code 1/FAILURE: Caused by Spark scripts being unable to find the java executable.  
* Start request repeated too quickly: Systemd's protective throttle after repeated environment-related crashes.

### **The Success Path: Systemd Service**

By explicitly defining the JAVA\_HOME and the full PATH within the service unit, we bypassed the environment isolation.

**Service Location:** /etc/systemd/system/spark-master.service

**Key Configuration:**

Ini, TOML

\[Service\]  
Type\=forking  
User\=thedude  
Environment\="JAVA\_HOME=/usr/lib/jvm/java-17-openjdk-amd64/"  
Environment\="SPARK\_HOME=/opt/spark"  
Environment\="PATH=/usr/lib/jvm/java-17-openjdk-amd64/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"  
ExecStart\=/opt/spark/sbin/start-master.sh \-h 192.168.68.56 \--webui-port 8080  
ExecStop\=/opt/spark/sbin/stop-master.sh  
Restart\=on\-failure

## ---

**2\. The Ultra 7 "Muscle" (Worker Node)**

### **The Persistence Hurdle**

WSL2 generates a new internal IP address on every restart. A hardcoded launch command would break the moment the WSL virtual network reset.

### **The Success Path: Dynamic Bridging Script**

We developed a "Dual-Homing" script that autodetects the internal WSL interface while advertising the static Windows LAN IP to the Master.

**The "Spark-Up" Logic:**

1. **Detection:** Uses hostname \-I to find the current WSL subnet IP.  
2. **Mapping:** Forwards the static Windows IP (192.168.68.52) as the reachable host.  
3. **Alias:** Bound to spark-up in .bashrc for one-touch deployment.

## ---

**3\. Final Cluster State**

| Feature | Configuration |
| :---- | :---- |
| **Master Persistence** | Fully Automated (Starts on Hardware Boot) |
| **Worker Persistence** | Semi-Automated (via spark-up command) |
| **Resource Pool** | 12 Cores / 48GB RAM |
| **Control Plane** | http://192.168.68.56:8080 |

## ---

**4\. Troubleshooting Checklist for Future Nodes**

* **Port Conflict:** Always run sudo fuser \-k 8080/tcp if the service fails to start.  
* **Firewall:** If telnet fails, re-verify the Windows WSL Interface filtering:  
  Set-NetFirewallProfile \-DisabledInterfaceAliases "vEthernet (WSL (Hyper-V firewall))"  
* **PID Stalls:** Delete stale PIDs in /tmp/ if Spark claims a process is already running.