## ---

**🛠️ HazyNet-Core: The "Zero-Friction" Cluster Docs**

### **1\. The Problem: The "Triple-Wall" Obstacle**

I faced three distinct hurdles that prevented the Ultra 7 (Driver) from talking to the Dell (Worker):

1. **The Network Isolation:** WSL2 lives on a private virtual network (172.x.x.x). The Dell Worker (192.x.x.x) couldn't "see" it to send data back.  
2. **The Filesystem Conflict:** Running sbt on a Windows-mounted drive (/mnt/c/...) caused permission errors because Linux couldn't manage file locks on a Windows partition.  
3. **The Visibility Gap:** The History Server on the Dell was looking at its own local disk, but the logs Ire being generated inside the isolated WSL environment.

### **2\. The Solutions: How I Won**

#### **A. The Network Bridge (The Tunnel)**

I used a **Netsh Port Proxy** on the Windows Host. This acted as a "receptionist." When the Dell knocks on the Windows IP, the request is instantly forwarded into the WSL virtual machine.

#### **B. The Native Workspace (The Speed)**

I implemented an rsync workflow. By syncing code from /mnt/ to a native Linux path (/home/thedude/), I allowed the Linux kernel to handle file operations natively, fixing the FileSystemException and speeding up compilation.

#### **C. The Automated Log-Sync (The History)**

To get the History Server working:

* Generated **SSH Keys** (ssh-keygen) to allow the Ultra 7 to talk to the Dell without passwords.  
* Added an **SCP** step to the submission script to automatically "teleport" the event logs to the Dell's watching directory.

### **3\. The Final Architecture**

| Component | Role | Network Identity |
| :---- | :---- | :---- |
| **Ultra 7 (WSL2)** | **Spark Driver** | 172.19.213.155 (Internal) |
| **Ultra 7 (Win)** | **Bridge/Proxy** | 192.168.68.52 (LAN) |
| **Dell Server** | **Spark Master/Worker** | 192.168.68.56 (LAN) |

### ---

**4\. Summary of "Zero-Friction" Script Features**

* ✅ **Auto-Build:** Packages the Scala JAR in a native Linux environment.  
* ✅ **IP Masking:** Forces the Spark Driver to advertise the LAN IP so the Dell knows where to respond.  
* ✅ **Port Consistency:** Uses fixed ports (38619, 34327\) to match the Windows firewall/proxy rules.  
* ✅ **Passwordless Sync:** Uses SSH keys to push logs to the History Server instantly.  
* ✅ **UI Keep-Alive:** Uses a 60-second sleep so you can actually inspect the DAG on port 4040\.

### **5\. Success Metrics**

* **Job Time:** \~0.25 seconds for 47-word count.  
* **Manual Steps:** 0 (Fully automated via bash spark-submit-cluster.sh).  
* **Status:** **FULLY OPERATIONAL.**

---

