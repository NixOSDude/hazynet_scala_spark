## **🛰️ Project HazyNet: The War for Connectivity**

**Goal:** Run a high-performance Spark Cluster using a WSL2 Driver (Windows) and a Bare-Metal Worker (Dell Server).

### **🧱 Phase 1: The "Stupid" VM Router (The Routing Wall)**

**The Struggle:** Initially, we had a VM router named ubu\_router acting as a gatekeeper. Because WSL2 lives in its own virtualized "island" (a nested subnet), and the Dell server lives on your physical home network, the two couldn't see each other.

* **The Obstacle:** Spark executors on the Dell tried to "call home" to the WSL2 IP, but the packets hit a dead end or a loopback address.  
* **The "Hurdle":** We kept seeing Initial job has not accepted any resources because the Worker couldn't talk back to the Driver.  
* **The Fix:** We bypassed the complexity of the VM router by using **explicit binding**. We forced the Spark Driver to announce its *real* reachable IP (192.168.68.52) and mapped specific ports (4041, 4042\) so the Dell knew exactly which "door" to knock on.

### **📁 Phase 2: The Filesystem Phantom (WSL vs. Linux)**

**The Struggle:** Even after they were talking, we couldn't read data. We tried to use \--files to send stress\_test.txt.

* **The Obstacle:** WSL2 paths look like /mnt/c/... or /home/thedude/..., but the Dell server looks for those *locally* on its own hard drive. It resulted in the dreaded FileNotFoundException.  
* **The "Hurdle":** We considered scp (manual copying), but that's "stupid" and doesn't scale.  
* **The Fix:** **The JAR Resource Hack.** We moved the data into the src/main/resources folder of the Scala project. By baking the data *into* the JAR, Spark handles the transfer automatically. The data and the code became one.

### **🏎️ Phase 3: The Power Struggle (Resource Tuning)**

**The Struggle:** The cluster was running, but it was "sipping" power instead of "chugging" it. We were only using 2 cores and 1GB of RAM.

* **The Obstacle:** Default Spark settings are conservative. To do real work, we needed to override the defaults.  
* **The Fix:** We pushed the spark-submit command to the limit, specifically requesting **6 cores** and **16GB of RAM**, and we re-partitioned the data to **12 tasks** to ensure every CPU thread on that Dell was saturated.

## ---

**🏆 The Final Architecture (What Worked)**

| Obstacle | The "Stupid" Part | The HazyNet Solution |
| :---- | :---- | :---- |
| **Networking** | WSL2 IP was invisible to the Dell. | Used \--conf spark.driver.host=192.168.68.52. |
| **Data Access** | Dell couldn't find WSL2 file paths. | Embedded files into the **JAR Resources**. |
| **Performance** | Used only 10% of the Dell's power. | Forced \--executor-memory 16G and 12 partitions. |
| **Router** | ubu\_router complexity. | Simplified routing by direct IP binding. |

## ---

**📝 Lessons Learned**

1. **Don't trust hostnames**: Always use static IPs in a hybrid WSL2 environment.  
2. **The JAR is a Container**: If the worker needs it, put it in the JAR.  
3. **Parallelism is Manual**: If you want to use 6 cores, you have to tell Spark to split the data into at least 6 pieces (parallelize(data, 6)).

