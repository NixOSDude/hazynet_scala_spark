# ---

**🚀 HazyNet Cluster: Technical Retrospective**

**Date:** February 5, 2026

**Infrastructure:** Ultra 7 (Muscle/WSL2) \+ Dell (Lighthouse/Master)

## **🏗️ The Architecture**

The goal was to create a distributed Spark environment where code is written on a Windows host, synced to a Linux Master via Samba, and executed using the heavy-duty compute power of a WSL2 instance (The Muscle).

## **🚧 Hurdles & Obstacles**

### **1\. The "Mirror Reality" Pathing**

* **The Conflict:** The Dell saw the project at /home/thedude/projects/, while the Ultra 7 saw it at /mnt/hazynet-core/.  
* **The Fix:** We decoupled the **Build Path** from the **Submission Path**. We told Spark to look for the JAR using the Master's native file path while the Driver utilized the local mount.

### **2\. Samba Metadata Restrictions**

* **The Conflict:** sbt failed to compile because Samba wouldn't allow Linux to change file timestamps (Operation not permitted).  
* **The Fix:** We redirected the target folder to a local WSL directory (/tmp/hazynet-build). This moved the "heavy lifting" to the local SSD and only copied the final JAR to the share.

### **3\. The WSL2 Network Ghost**

* **The Conflict:** WSL2 lives behind a NAT. Spark tried to bind to a loopback address (127.x.x.x) or a hidden internal IP, making it invisible to the Dell Master.  
* **The Fix:** We implemented **Split-IP Configuration**:  
  * spark.driver.bindAddress: Bound to the internal WSL IP (172.19.213.155).  
  * spark.driver.host: Announced the Windows LAN IP (192.168.68.52) to the cluster.

### **4\. The "Empty JAR" Mystery**

* **The Conflict:** Spark reported Failed to load class even though the JAR existed.  
* **The Fix:** We discovered sbt ignores files not in the strict src/main/scala/ hierarchy. Moving the source code to the "Official" path allowed the compiler to actually package the code.

## **✅ Success Metrics**

* **Distributed Execution:** Confirmed 12 cores and 20GB RAM allocated to the job.  
* **Bridge Stability:** 0% packet loss between WSL2 and physical hardware.  
* **Build Speed:** Local SSD compilation reduced build times from "Samba-slow" to \~2 seconds.

## ---

**📅 The Road Map (Next Steps)**

Now that the foundation is poured, we are moving into the "Construction Phase."

### **A) The Memory: Spark History Server**

* **Goal:** Enable the Dell to record every job so you can review performance graphs even after the Ultra 7 is turned off.

### **B) The Logic: HazyNet Ingestion**

* **Goal:** Move beyond "Hello World" and start writing Scala code to process real data (Parquet/JSON) across the cluster.

### **C) The Scale: Expanding the Muscle**

* **Goal:** Optimizing the Ultra 7 to ensure it doesn't just run 12 cores, but saturates the NVMe throughput for maximum data speed.

---

