# **Whitepaper: Implementing Hardware-Accelerated Distributed Computing**

**Project:** HazyNet-GPU-Stress-Build

**Lead Engineer:** thedude

**Date:** February 6, 2026

**Stack:** Spark 3.5.3, RAPIDS 24.12.0, CUDA 12.x, Ubuntu (WSL2) \+ Remote Master

## ---

**1\. Executive Summary**

The objective was to transform a standard CPU-bound Spark cluster into a GPU-accelerated powerhouse. By integrating the NVIDIA RAPIDS Accelerator for Apache Spark, we successfully offloaded heavy SQL and DataFrame operations to an RTX 3060\. The result is a hybrid cluster where a Windows-based WSL2 node provides the GPU "muscle" to a remote Linux-based Spark Master.

## ---

**2\. The Hurdles & Obstacles (The "Battlefield")**

### **❌ Obstacle 1: The Version Mismatch (The "Shim" Trap)**

* **The Issue:** Spark 3.5.3 is cutting-edge. Using older RAPIDS versions caused "Shim" errors because the plugin couldn't find the correct hooks in the Spark source code.  
* **The Fix:** Upgraded to **RAPIDS 24.12.0**, which explicitly supports Spark 3.5.x, ensuring the classloader could correctly "shim" the execution engine.

### **❌ Obstacle 2: The Network Identity Crisis**

* **The Issue:** WSL2 operates on a virtualized network. The Spark Master on the Dell server could see the Driver, but the Driver couldn't route data back to the WSL2 internal IP.  
* **The Fix:** Explicitly binding the environment using SPARK\_LOCAL\_IP and spark.driver.host to 172.19.213.155. This forced the cluster to acknowledge the WSL2 bridge.

### **❌ Obstacle 3: The Timezone Fallback**

* **The Issue:** Even with the GPU active, Spark was falling back to the CPU for certain operations. The logs revealed that the America/Phoenix timezone caused incompatible "ToPrettyString" expressions.  
* **The Fix:** Standardized the entire cluster to **UTC** using JVM extra options and Spark session configs. This "unified" the data format and kept the workload on the GPU.

## ---

**3\. The Success: Technical Architecture**

We successfully deployed a **Heterogeneous Cluster** with the following specifications:

| Component | Specification |
| :---- | :---- |
| **Spark Master** | Remote Dell Server (192.168.68.56) |
| **GPU Executor** | RTX 3060 12GB (via WSL2 / Ubuntu) |
| **Compute Engine** | Apache Spark 3.5.3 |
| **Acceleration** | NVIDIA RAPIDS \+ CUDF 24.12.0 |
| **Data Throughput** | \~42 Million Rows per 4.8 seconds |

### **The "Golden" Submit Command**

The final, optimized entry point for the cluster:

Bash

/opt/spark/bin/spark-submit \\  
  \--master spark://192.168.68.56:7077 \\  
  \--conf "spark.plugins=com.nvidia.spark.SQLPlugin" \\  
  \--conf "spark.rapids.sql.enabled=true" \\  
  \--conf "spark.sql.session.timeZone=UTC" \\  
  \--jars /opt/spark/jars/rapids-4-spark\_2.12-24.12.0.jar \\  
  /path/to/hazynetcore.jar

## ---

**4\. Performance Results**

* **Zero-Copy Execution:** The RAPIDS plugin successfully transitioned Row-based CPU data into Columnar GPU batches.  
* **Hardware Utilization:** Observed significant GPU memory allocation and core utilization during the GpuFilter and GpuHashAggregate stages.  
* **Scalability:** The system is now configured to handle up to 10 concurrent tasks per GPU (spark.task.resource.gpu.amount=0.1), maximizing the RTX 3060's parallel processing capabilities.

## ---

**5\. Conclusion**

The project successfully demonstrates that high-end consumer hardware (RTX 3060\) can be effectively integrated into a professional Spark environment via WSL2. This setup provides a cost-effective alternative to expensive cloud GPU instances for data stress-testing and development.

