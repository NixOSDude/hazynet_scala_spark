### 🌌 Project HazyNet

### **Local Area Network (LAN) Distributed Spark Cluster**
**Architecture:** Pure Scala & Apache Spark | **Cluster:** Linux-Windows Hybrid | **Logic:** Functional Programming

### 🎯 The Mission
Project HazyNet is a high-performance local laboratory designed to master **Apache Spark internals** and **Functional Programming (FP)**. By bypassing managed cloud services, I have engineered a bare-metal environment that allows for deep-level tuning of distributed memory, shuffle behavior, and $O(n)$ algorithmic efficiency.

**Current Status:** 🟢 Lighthouse Node (Master) Online | 🟡 Cluster Bonding in Progress

### 🏗️ Hardware Architecture: "The Bond"
I utilize a heterogeneous standalone cluster to distribute compute across my local network.

| Node | Hardware Profile | Operating System | Cluster Role |
| :--- | :--- | :--- | :--- |
| **Lighthouse** | i7 | 24GB RAM | Ubuntu 22.04 (Headless) | **Spark Master / Driver** |
| **Muscle** | Ultra 7 | 64GB DDR5 | RTX 3060 | Windows 11 | **Spark Worker (Compute)** |


### **The Bare Metal Advantage**
* **PCIe 5.0 Shuffle Storage:** Utilizing the Ultra 7's 5th Gen NVMe for shuffle spills to minimize I/O wait times.
* **Network Transparency:** Direct monitoring of data movement across the `192.168.68.x` subnet.
* **Resource Sovereignty:** Manual JVM heap allocation and thread management for maximum hardware utilization.


### 🛠️ Technical Stack & Philosophy
* **Language:** **Scala 2.12.18** (Chosen for 1:1 binary compatibility with the Spark engine).
* **Build Tool:** **sbt** (Scala Build Tool) for industrial-grade dependency management.
* **Engine:** **Apache Spark 3.5.8** (LTS Standalone Mode).
* **Functional Programming:** Heavy emphasis on **Immutability** and **Tail Recursion** (`@tailrec`) to ensure $O(1)$ stack space for deep data structures.


### 📂 Repository Structure
* `/src/main/scala`: Pure Functional Spark applications and algorithmic implementations.
* `/docs`: Detailed whitepapers on cluster configuration and network bonding.
* `/target`: Compiled "Uber-JARs" for distributed submission.
* `RESUME.md`: Professional history and certification details.

### 🚀 Standard Workflow
1.  **Develop:** Author pure functional Scala code on the **Muscle** node.
2.  **Compile:** Build optimized JARs using `sbt` on the **Lighthouse** node.
3.  **Execute:** Submit distributed jobs via the Spark Master.

```bash
# Example Job Submission
spark-submit \
  --class Main \
  --master spark://192.168.68.56:7077 \
  --executor-memory 48G \
  --total-executor-cores 12 \
  hazynet-core_2.12-1.0.jar

```

### 📜 Dissertation: Why  Matters

In distributed systems, efficiency isn't just about speed—it's about **cost and scalability**. By implementing linear-time algorithms and avoiding unnecessary shuffles, I ensure that data pipelines remain performant regardless of dataset size.





Are we ready to pivot back to the **Ultra 7** to get the Windows Spark environment configured so we can finalize the "Bond" between the two nodes?

```
