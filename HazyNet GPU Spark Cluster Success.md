# **Whitepaper: Engineering the HazyNet GPU-Accelerated Spark Cluster**

**Status:** SUCCESS / OPERATIONAL

**Lead Engineer:** thedude

**Date:** February 6, 2026

## **1\. Project Objective**

The goal was to architect a high-performance, heterogeneous Spark cluster that leverages consumer-grade NVIDIA hardware (RTX 3060\) to accelerate large-scale data processing. The environment required bridging a virtualized Windows Subsystem for Linux (WSL2) node with a physical remote Spark Master.

## ---

**2\. Key Technical Hurdles & Resolutions**

### **🚧 The "Shim" Version Conflict**

**Obstacle:** Early attempts failed due to ShimLoader errors. Spark 3.5.3 changed internal APIs that the RAPIDS plugin uses to "shim" (replace) CPU operators with GPU ones.

**Resolution:** Upgraded to **RAPIDS 24.12.0**. This version provided the specific shims for the 3.5.x line, allowing the MutableURLClassLoader to successfully inject NVIDIA-specific classes.

### **🚧 The WSL2 Networking "Black Hole"**

**Obstacle:** Spark Executors on WSL2 could reach the Master, but the Master could not "talk back" because WSL2 lives behind a NAT.

**Resolution:** Explicitly defined the network topology using SPARK\_LOCAL\_IP and spark.driver.host. By pinning the Driver to the bridge IP (172.19.213.155), we established a bidirectional heartbeat between the Dell Server and the RTX 3060\.

### **🚧 The Timezone Fallback (The Silent Performance Killer)**

**Obstacle:** Even after successful GPU allocation, logs showed HashAggregateExec falling back to the CPU. The culprit was a timezone mismatch (America/Phoenix), which forced Spark to use Java-based string formatting incompatible with the GPU.

**Resolution:** Forced the entire cluster into **UTC** via spark.sql.session.timeZone and JVM extraJavaOptions. This unified the data format, ensuring a 100% GPU-native execution path.

## ---

**3\. Final Architecture & Performance**

### **The Software Stack**

* **Engine:** Apache Spark 3.5.3 (Scala 2.12)  
* **Accelerator:** NVIDIA RAPIDS 24.12.0  
* **JNI Layer:** CUDF 24.12.0 (CUDA 12 compatible)  
* **OS:** Ubuntu 22.04 (WSL2 Kernel 6.6.87)

### **Hardware Utilization**

* **GPU:** NVIDIA GeForce RTX 3060 (12GB VRAM)  
* **Parallelism:** Configured for **10 concurrent tasks per GPU** (0.1 GPU per task).  
* **Throughput:** Successfully processed **41,956,935 rows** with zero CPU fallbacks.

## ---

**4\. The "Golden" Deployment Command**

To replicate this success, the following command must be used to ensure network binding and GPU shimming:

Bash

export SPARK\_LOCAL\_IP=172.19.213.155

/opt/spark/bin/spark-submit \\  
  \--master spark://192.168.68.56:7077 \\  
  \--class ClusterTest \\  
  \--conf "spark.driver.host=172.19.213.155" \\  
  \--conf "spark.plugins=com.nvidia.spark.SQLPlugin" \\  
  \--conf "spark.rapids.sql.enabled=true" \\  
  \--conf "spark.executor.resource.gpu.amount=1" \\  
  \--conf "spark.task.resource.gpu.amount=0.1" \\  
  \--conf "spark.sql.session.timeZone=UTC" \\  
  \--conf "spark.driver.extraJavaOptions=-Duser.timezone=UTC" \\  
  \--conf "spark.executor.extraJavaOptions=-Duser.timezone=UTC" \\  
  \--jars /opt/spark/jars/rapids-4-spark\_2.12-24.12.0.jar \\  
  /home/thedude/hazynet-stress-build/target/scala-2.12/hazynetcore\_2.12-1.0.jar

## ---

**5\. Conclusion**

HazyNet is now a verified **GPU-Accelerated Spark Powerhouse**. We have successfully bridged consumer hardware with enterprise-grade data orchestration, creating a blueprint for high-speed, low-cost data engineering.

**Mission Accomplished.**