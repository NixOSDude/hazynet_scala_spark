# 🛡️ Project HazyNet: The Private Cloud Lakehouse
### *Architecting a 100GB+ Functional Data Pipeline on Custom Hybrid Infrastructure*

This project implements a **Production-Grade Medallion Architecture** on a custom-built private cloud. It bridges dedicated server-grade storage with a high-concurrency, GPU-accelerated workstation to process NYC’s massive taxi datasets using **Pure Functional Scala**.



## 🏗️ The Infrastructure (The "HazyNet" Stack)

* **The Lakehouse (Master & Storage): Dell Latitude E5570**
    * **Specs:** Intel i7 | 24GB RAM | 1TB SSD
    * **Role:** NFS/SSHFS Master Node and Permanent Lakehouse Storage.
* **The Engine (Compute Worker): WSL2 (Ubuntu 22.04 LTS)**
    * **Specs:** 20 Cores | 60GB RAM | **NVIDIA RTX 3060 (12GB VRAM)**
* **The Cockpit (IDE): Apache Zeppelin**
    * **Role:** GPU-accelerated Spark SQL queries and real-time data visualization.
* **The Data Bridge:** Encrypted **SSHFS Tunneling** across the local network.

---

## 🗺️ The Professional Syllabus

### Module 1: Infrastructure, GPU Integration & The Bronze Layer
* **Hybrid Networking:** Configuring SSHFS between WSL2 and the Dell E5570.
* **GPU-Ready Zeppelin:** Utilizing the **RTX 3060** for accelerated Parquet scanning.
* **Idempotent Ingestion:** Developing resumable shell scripts for 100GB+ datasets.

### Module 2: The Silver Layer & Functional Hardening
* **Schema Unification:** Designing a **Unified Trip Trait** (No Nulls).
* **The "Total Function" Pattern:** Managing the 2024-2025 **Congestion Fee Schema Shift**.
* **Data Cleansing:** Pure predicates for data fidelity.

### Module 3: The Golden Layer & High-Performance Analytics
* **Broadcast Join Optimization:** Avoiding the "Shuffle-Geddon."
* **Vectorized UDFs:** Leveraging the **RTX 3060** for high-speed math.
* **Resource Management:** Tuning 60GB RAM for large-scale joins.

### Module 4: Operational Excellence
* **Performance Benchmarking:** CPU vs. GPU execution analysis.
* **Unit Testing with FP:** Deterministic, side-effect free Spark tests.

---

## 📊 Verified Infrastructure Benchmarks (Internal Audit)
*Logged: February 12, 2026*

| Component | Verified Status | Metric / Specification |
| :--- | :--- | :--- |
| **GPU Acceleration** | **ACTIVE** | NVIDIA GeForce RTX 3060 |
| **Compute Power** | **VERIFIED** | 20 Cores | 50GB Spark Executor Memory |
| **Ingestion Speed** | **ELITE** | **19,663,930 records processed in 2.85s** |

