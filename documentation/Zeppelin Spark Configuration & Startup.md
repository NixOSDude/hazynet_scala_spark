## **1\. Master-Worker Architecture**

| Role | Hardware | Network IP |
| :---- | :---- | :---- |
| **Spark Master** | Dell Lakehouse Server | 192.168.68.56 |
| **Spark Worker** | Ultra 7 (WSL Instance) | 172.19.213.155 |
| **Spark Driver** | Zeppelin (WSL Instance) | 172.19.213.155 (Bound to 192.168.68.52) |

## ---

**2\. Zeppelin Spark Interpreter Configuration**

You must enter these exact properties into the Zeppelin Interpreter settings (http://172.19.213.155:8090/\#/setting). This configuration mirrors your "Locked-In" terminal shell.

### **A. Core Spark Infrastructure**

| Property | Value | Description |
| :---- | :---- | :---- |
| SPARK\_HOME | /opt/spark | Path to Spark distribution. |
| spark.master | spark://192.168.68.56:7077 | Connects directly to the Dell Master. |
| spark.submit.deployMode | client | Launches driver locally in WSL. |
| spark.driver.memory | 12g | High-buffer for local notebook results. |
| spark.executor.memory | 50g | Max RAM for the Ultra 7 Worker. |
| spark.executor.cores | 16 | High-performance core allocation. |

### **B. RAPIDS GPU & Networking (The "HazyNet" Layer)**

These settings enable the **RTX 3060** and fix the communication bridge.

| Property | Value |

| :--- | :--- |

| **spark.driver.host** | **192.168.68.52** |

| **spark.driver.bindAddress** | **0.0.0.0** |

| spark.plugins | com.nvidia.spark.SQLPlugin |

| spark.rapids.sql.enabled | true |

| spark.jars | /opt/spark/jars/rapids-4-spark\_2.12-24.12.0.jar |

| spark.executor.resource.gpu.amount | 1 |

| spark.task.resource.gpu.amount | 0.1 |

| spark.rapids.sql.allowMultipleJars | ALWAYS |

| spark.memory.offHeap.enabled | true |

| spark.memory.offHeap.size | 8g |

### **C. JVM Reflection Opens (Static Headers)**

Necessary for the RAPIDS plugin to access system memory directly.

* **spark.driver.extraJavaOptions**: \-Duser.timezone=UTC \--add-opens=java.base/java.lang=ALL-UNNAMED \--add-opens=java.base/java.net=ALL-UNNAMED \--add-opens=java.base/java.nio=ALL-UNNAMED \--add-opens=java.base/java.util=ALL-UNNAMED \--add-opens=java.base/sun.nio.ch=ALL-UNNAMED  
* **spark.executor.extraJavaOptions**: \-Duser.timezone=UTC \--add-opens=java.base/java.lang=ALL-UNNAMED \--add-opens=java.base/java.net=ALL-UNNAMED \--add-opens=java.base/java.nio=ALL-UNNAMED \--add-opens=java.base/java.util=ALL-UNNAMED \--add-opens=java.base/sun.nio.ch=ALL-UNNAMED

## ---

**3\. Daily Startup Protocol**

To prevent the "0% Hang," the Worker must be registered with the Master **before** Zeppelin is accessed.

### **Step 1: Clean & Register Worker (On Ultra 7 / WSL)**

Bash

\# Clean any ghost sessions  
pkill \-f spark; pkill \-f java;

\# Set Environment and Start Worker  
export SPARK\_LOCAL\_IP=172.19.213.155;  
export SPARK\_WORKER\_OPTS="-Dspark.worker.resource.gpu.amount=1 \-Dspark.worker.resource.gpu.discoveryScript=/opt/spark/examples/src/main/scripts/getGpusResources.sh";

/opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \\  
  spark://192.168.68.56:7077 \\  
  \--cores 20 \--memory 60G &

### **Step 2: Verify Master UI**

Open http://192.168.68.56:8080.

* Ensure **Alive Workers: 1** is displayed.  
* Ensure the GPU resource is listed under the Ultra 7 worker.

### **Step 3: Start Zeppelin**

Bash

/opt/zeppelin/bin/zeppelin-daemon.sh start

## ---

**4\. The Gold Layer Verification Script**

Use this block in a %spark cell to confirm the cluster is ready for the **42M row** load.

Scala

%spark  
import org.apache.spark.sql.functions.\_

// Path to Dell Lakehouse via verified WSL mount  
val goldPath \= "/home/thedude/hazynet-lakehouse/gold/retail\_sales\_final"

// Load and trigger GPU Scan  
val salesDF \= spark.read.parquet(goldPath)  
val rowCount \= salesDF.count()

println(s"SUCCESS: HazyNet GPU Cluster Active.")  
println(s"Total Records: $rowCount")

// Verify GpuScan in the physical plan  
salesDF.explain()

This document is now the "Source of Truth" for your project. **Would you like me to create a second document specifically for the XGBoost GPU-training parameters once you finish verifying the Gold load?**