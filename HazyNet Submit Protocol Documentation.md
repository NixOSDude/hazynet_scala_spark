# **TECHNICAL BRIEF: The HazyNet "Locked-In" Submit Protocol**

**Configuration Reference:** HZ-2026-02-06

**Environment:** WSL2 (Ubuntu) → Dell Latitude E5570 (Spark Master/Lakehouse)

## ---

**1\. Network Topology**

To ensure the Spark Master on the **E5570** can talk back to the **WSL Box**, the driver host must be explicitly bound to the WSL virtual interface.

* **Spark Master:** 192.168.68.56 (Dell Latitude E5570)  
* **Driver Host (WSL):** 172.19.213.155

## **2\. The GPU Acceleration Stack**

The protocol utilizes the **NVIDIA RAPIDS 24.12.0** plugin to offload the JVM processing to the RTX 3060 CUDA cores.

* **Plugin Path:** /opt/spark/jars/rapids-4-spark\_2.12-24.12.0.jar  
* **Key Constraint:** spark.rapids.sql.enabled=true must be set to bypass standard CPU execution.

## ---

**3\. The Standard Submit Command**

This is the immutable command used to deploy the **RetailDirtySeeder** and all subsequent Gold-layer processing jobs.

\# Set Local IP for WSL Callback  
export SPARK\_LOCAL\_IP=172.19.213.155

\# Execution Command  
/opt/spark/bin/spark-submit \\  
  \--master spark://192.168.68.56:7077 \\  
  \--class RetailDirtySeeder \\  
  \--conf "spark.driver.host=172.19.213.155" \\  
  \--conf "spark.plugins=com.nvidia.spark.SQLPlugin" \\  
  \--conf "spark.rapids.sql.enabled=true" \\  
  \--conf "spark.executor.resource.gpu.amount=1" \\  
  \--conf "spark.task.resource.gpu.amount=0.1" \\  
  \--conf "spark.sql.session.timeZone=UTC" \\  
  \--conf "spark.driver.extraJavaOptions=-Duser.timezone=UTC" \\  
  \--conf "spark.executor.extraJavaOptions=-Duser.timezone=UTC" \\  
  \--driver-memory 10G \\  
  \--executor-memory 40G \\  
  \--jars /opt/spark/jars/rapids-4-spark\_2.12-24.12.0.jar \\  
  /home/thedude/hazynet-stress-build/target/scala-2.12/hazynetcore\_2.12-1.0.jar

## ---

**4\. Hardware Resource Allocation**

| Parameter | Setting | Purpose |
| :---- | :---- | :---- |
| **Driver Memory** | 10G | Handles the metadata broadcast for Gold-layer joins. |
| **Executor Memory** | 40G | Provides headroom for 41M row partitions on the Dell node. |
| **GPU Amount** | 1.0 | Dedicates the RTX 3060 entirely to the Spark Executor. |
| **Task GPU** | 0.1 | Allows for 10 concurrent GPU tasks per executor. |

## ---

**5\. Storage Mapping (Dell Lakehouse)**

All output is routed to the **E5570** via the local mount point to maintain the Medallion integrity:

* **Silver Layer:** /home/thedude/hazynet-lakehouse/cleaned/  
* **Gold Layer:** /home/thedude/hazynet-lakehouse/gold/

---

