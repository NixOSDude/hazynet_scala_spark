# 🛡️ Project HazyNet: NYC Taxi Private Cloud Lakehouse 🚀

An authentic, industrial-grade Big Data pipeline built with **Scala 2.12**, **Apache Spark 3.x**, and a strict adherence to **Pure Functional Programming (FP)**. This project leverages a custom-built hybrid cloud to process 100GB+ of NYC Taxi data.

---

## 🏛 The 4 Tenets of our FP Architecture
Every line of code in this repository is governed by:
1. **Immutability Only**: All fields use immutable values; state changes are handled via copy-on-write.
2. **No Nulls**: Total elimination of null pointer risks using functional types.
3. **Total Functions**: Every function returns a value; `if` statements always include an `else`.
4. **Separation of Concerns**: Case Classes (Data) are decoupled from Pure Functions (Behavior).

---

## 🏗️ Hybrid Local Cloud Architecture
We utilize a **Hardware-Software Co-design** to optimize $O(n)$ data throughput.

* **The Lakehouse (Master & Storage): Dell Latitude E5570**
    * *Specs:* Intel i7 | 24GB RAM | 1TB SSD
    * *Role:* Permanent storage node and master coordinator.
* **The Engine (Compute Worker): WSL2 Ubuntu 22.04 LTS**
    * *Specs:* 20 Cores | 60GB RAM | **NVIDIA RTX 3060 (12GB VRAM)**
    * *Role:* GPU-accelerated Spark execution and high-concurrency transformations.
* **The Cockpit:** Apache Zeppelin (Port: `8090`) with GPU-integrated interpreters.

---

## 📂 Repository & Project Links
* [**📜 Master Project Syllabus**](./SYLLABUS.md) - *Detailed roadmap & hardware benchmarks.*
* [**📄 Scott Baker's Resume**](./scott_baker_resume.md) - *Data Engineering & Systems Architecture Profile.*
* `📁 documentation/`: Detailed Big O analysis and evolution retrospectives.
* `📁 notebooks/`: Zeppelin exports for Bronze, Silver, and Gold layers.

---

## 📊 Verified Baseline Performance
* **Throughput:** ~19.6 Million records processed in **2.85 seconds**.
* **Engine Power:** 50GB Spark Executor memory allocation on 20 logic cores.

## 🚀 Getting Started
To start the environment on the WSL box, use the locked-in daemon command:
```bash
export ZEPPELIN_ADDR="172.19.213.155" && export ZEPPELIN_PORT="8090" && /opt/zeppelin/bin/zeppelin-daemon.sh start
