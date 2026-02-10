# Hazynet Scala Spark Lakehouse 🚀

An authentic, industrial-grade Big Data pipeline built with **Scala 2.12**, **Apache Spark 3.x**, and a strict adherence to **Pure Functional Programming (FP)**.

## 🏛 The 4 Tenets of our FP Architecture
This repository is governed by four strict principles to ensure data honesty and system reliability:
1. **Immutability Only**: All fields use immutable values; state changes are handled via copy-on-write transformations.
2. **No Nulls**: We utilize `Option[T]` and `na.fill` to eliminate null pointer risks.
3. **Total Functions**: Every function returns a value; `if` statements always include an `else`.
4. **Separation of Concerns**: Data structures (Case Classes) are strictly decoupled from behavior (Pure Functions).

## 🛠 System Configuration
* **System**: WSL2 (Ubuntu) acting as the Compute Node.
* **Storage**: Dell Lakehouse (Parquet/Delta format).
* **IDE/Environment**: Apache Zeppelin (Port: `8090`).
* **JDK**: 21.0.8.9-hotspot.

## 📂 Repository Structure
* `📁 documentation/`: The "Finalized Vault" containing evolution retrospectives and detailed Big O analysis.
* `📁 notebooks/`: Zeppelin notebook exports for the Bronze, Silver, and Gold layer transformations.

## 🚀 Getting Started
To start the environment on the WSL box, use the locked-in daemon command:
```bash
export ZEPPELIN_ADDR="172.19.213.155" && export ZEPPELIN_PORT="8090" && /opt/zeppelin/bin/zeppelin-daemon.sh start
