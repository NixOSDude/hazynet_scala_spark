## ---

**🏗️ Technical Log: HazyNet "Lighthouse" Node Setup**

**Environment:** Ubuntu 22.04 LTS (Headless) | **Hardware:** Dell Laptop (Server)

**Goal:** Establish a Master Node for a Heterogeneous Spark Cluster.

### ---

**Phase 1: The JVM Foundation**

**Action:** Installed OpenJDK 17\.

* **Command:** sudo apt install openjdk-17-jdk \-y  
* **Reasoning:** Spark 3.5.x is optimized for Java 17\. Java provides the JVM (Java Virtual Machine) environment necessary for Spark to manage memory and execute distributed tasks across the cluster. It is the "bedrock" of the entire stack.

### **Phase 2: Spark Engine Deployment**

**Action:** Manual installation of Apache Spark 3.5.8 (LTS).

* **Command:** wget and tar to /opt/spark.  
* **Reasoning:** Placing Spark in /opt/ follows the **Filesystem Hierarchy Standard (FHS)** for optional software packages. We chose **Spark 3.5.8** specifically because it is the latest maintenance release of the 3.5 branch, ensuring we have the most stable API for our Scala integration.

### **Phase 3: The Functional Programming Layer (Scala & sbt)**

**Action:** Installed Scala 2.12.18 and sbt via **Coursier**.

* **Command:** cs setup and cs install scala:2.12.18 sbt.  
* **Reasoning:** \* **Scala 2.12.18:** This version is binary-compatible with the pre-compiled JARs inside Spark 3.5.8. Using any other version (like Scala 3\) would lead to ClassNotFound or MethodNotFound exceptions during runtime.  
  * **sbt (Scala Build Tool):** Essential for dependency management. It allows us to build "Uber-JARs" (assembly JARs) that can be submitted to any Spark cluster.

### **Phase 4: Path Sovereignty (Environment Configuration)**

**Action:** Configured \~/.bashrc for global tool availability.

* **Reasoning:** By explicitly adding SPARK\_HOME and the Coursier bin to the $PATH, we ensure that any automation—like a Gitea CI/CD runner—can execute spark-submit or sbt without needing absolute paths. This makes the node "headless-friendly."

### **Phase 5: The "Handshake" Validation**

**Action:** Built and ran a Tail-Recursive Spark job.

* **Logic:**  
  Scala  
  @tailrec  
  def sumRange(n: Long, accum: Long \= 0): Long \= { ... }

* **Reasoning:** \* **Tail Recursion:** We used the @tailrec annotation to ensure the compiler optimizes the function into a loop. This prevents a StackOverflowError when processing massive datasets, which is a hallmark of senior-level functional programming.  
  * **Spark-Submit:** Running the job via spark-submit verified that the **Driver** could initialize, the **BlockManager** could allocate memory, and the **TaskScheduler** could execute our code successfully.

## ---

**📊 Summary of Infrastructure**

| Component | Version | Role |
| :---- | :---- | :---- |
| **Java (JDK)** | 17 | Runtime Environment |
| **Spark** | 3.5.8 | Distributed Analytics Engine |
| **Scala** | 2.12.18 | Primary Programming Language |
| **sbt** | 1.10.x | Build and Dependency Manager |

### 