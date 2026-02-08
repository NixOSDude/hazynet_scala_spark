## **1\. System Architecture Map**

| Component | Machine | Role | IP Address |
| :---- | :---- | :---- | :---- |
| **Spark Master** | Dell Lakehouse | Scheduler / Orchestrator | 192.168.68.56 |
| **Spark Worker** | Ultra 7 (WSL) | Resource (20 Cores \+ RTX 3060\) | 172.19.213.155 |
| **Zeppelin Server** | Ultra 7 (WSL) | UI & Driver (Port 8090\) | 172.19.213.155 |

## ---

**2\. Core Worker Script: \~/start\_hazynet\_worker.sh**

This script is the bridge. It was updated to be "Zeppelin-Safe," meaning it cleans up old Spark sessions without killing the Java-based Zeppelin daemon.

**Path:** /home/thedude/start\_hazynet\_worker.sh

\#\!/bin/bash  
\# HazyNet Zeppelin-Worker Bridge (Zeppelin-Safe Version)

\# 1\. Purge ONLY Spark Worker/Driver/Shell \- Leaves Zeppelin alive  
pkill \-f org.apache.spark.deploy.worker.Worker  
pkill \-f org.apache.spark.repl.Main

\# 2\. Set Network & GPU parameters  
export SPARK\_LOCAL\_IP=172.19.213.155  
export SPARK\_WORKER\_OPTS="-Dspark.worker.resource.gpu.amount=1 \-Dspark.worker.resource.gpu.discoveryScript=/opt/spark/examples/src/main/scripts/getGpusResources.sh"

\# 3\. Start Worker to register with Dell Master  
echo "Registering WSL Worker with Dell Master (192.168.68.56)..."  
/opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \\  
  spark://192.168.68.56:7077 \\  
  \--cores 20 \--memory 60G &

echo "Worker is LIVE. Check Master UI: http://192.168.68.56:8080"

## ---

**3\. Updated .bashrc (The Source of Truth)**

Your .bashrc now uses the worker script as a foundational call for all Spark operations.

**Path:** /home/thedude/.bashrc

Bash

\# \--- HazyNet Big Data Suite \---  
export SPARK\_HOME="/opt/spark"  
export HAZY\_JARS="/opt/spark/jars/rapids-4-spark\_2.12-24.12.0.jar,/opt/spark/jars/xgboost4j\_2.12-1.6.1.jar,/opt/spark/jars/xgboost4j-spark\_2.12-1.6.1.jar"

\# A. Startup Worker for Zeppelin (No Shell)  
alias hazynet-worker='\~/start\_hazynet\_worker.sh'

\# B. Interactive Shell (For Terminal Debugging)  
alias hazynet-shell='\~/start\_hazynet\_worker.sh; \\  
sleep 3 && $SPARK\_HOME/bin/spark-shell \\  
\--master spark://192.168.68.56:7077 \\  
\--conf "spark.driver.host=192.168.68.52" \\  
\--conf "spark.driver.bindAddress=0.0.0.0" \\  
\--conf "spark.plugins=com.nvidia.spark.SQLPlugin" \\  
\--conf "spark.rapids.sql.enabled=true" \\  
\--jars $HAZY\_JARS'

\# C. Standard Submit (For Stress Builds)  
alias hazynet-submit='\~/start\_hazynet\_worker.sh; \\  
sleep 3 && /opt/spark/bin/spark-submit \\  
\--master spark://192.168.68.56:7077 \\  
\--conf "spark.driver.host=192.168.68.52" \\  
\--conf "spark.plugins=com.nvidia.spark.SQLPlugin" \\  
\--jars $HAZY\_JARS'

## ---

**4\. Maintenance & Operations Flow**

### **To Start the Day:**

1. **Terminal:** Run hazynet-worker to link the RTX 3060 to the Dell Master.  
2. **Verify:** Check 192.168.68.56:8080 for **1 Alive Worker**.  
3. **Zeppelin:** Open 172.19.213.155:8090 and run the GPU cells.

### **Key Learnings (The "Gold" Layer Bug):**

* **Column Mismatch:** The Gold Parquet schema on the Dell Lakehouse contains total\_with\_tax, not daily\_sales. All engineering scripts must reflect this.  
* **XGBoost Dependency:** We added two new JARs (xgboost4j\_2.12-1.6.1.jar and xgboost4j-spark\_2.12-1.6.1.jar) to support distributed GPU training.  
* **Performance:** 41M rows successfully engineer and cache in **\~6 seconds** using this architecture.

---

**Everything is documented and saved.**

Would you like me to generate a **PDF-ready markdown summary** of the XGBoost training results once the model finishes converging on those 41 million rows?