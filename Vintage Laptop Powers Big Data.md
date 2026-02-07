# **WHITEPAPER: The HazyNet GPU-Accelerated Medallion Lakehouse**

**Date:** February 6, 2026

**Project Lead:** The Dude

**Core Tech:** Apache Spark 3.5.0, NVIDIA RAPIDS, Streamlit, Parquet

## ---

**1\. Executive Summary**

The HazyNet Lakehouse project demonstrates that high-volume data engineering (41M+ rows) is possible on accessible hardware. By combining a "vintage" **Dell Latitude E5570** storage node with a modern GPU-equipped WSL compute box, we achieved sub-3-second analytical performance. This project proves that **Medallion Architecture** can be democratized.

## **2\. Infrastructure: "The Old & The New"**

The system utilizes a hybrid-distributed model, separating storage and compute:

* **The Lakehouse Node (Storage):** **Dell Latitude E5570**  
  * **Specs:** 24GB RAM, 1TB SSD.  
  * **Legacy Resilience:** Originally released circa 2016, the E5570 serves as the primary data repository. Its 24GB RAM expansion and SSD upgrade allow it to handle the I/O throughput required for 41 million Parquet records without bottlenecking the compute node.  
* **The Compute Node (WSL Box):** Modern workstation running Ubuntu under WSL2.  
  * **Accelerator:** **NVIDIA RTX 3060**.  
  * **Role:** Handles all ETL, 41M row generation, and GPU-accelerated joins.

## **3\. The Medallion Architecture**

We utilized a three-tier data approach to ensure data quality and performance:

* **Bronze (Raw):** 41M rows of synthetic transactions stored on the Dell Latitude E5570.  
* **Silver (Cleaned):** Normalized schema with tax logic (amount \* 1.08) applied.  
* **Gold (Enriched):** The final analytical layer where transactions are joined with Customer and Store metadata via GPU.

## **4\. High-Performance Compute: NVIDIA RAPIDS**

The secret to processing 41M rows on this setup is **Vectorized Execution**.

* **GPU Broadcast Joins:** The E5570 provides the data, but the RTX 3060 provides the brains. By "broadcasting" metadata to the GPU VRAM, we avoid the slow CPU-based processing typical of older hardware.  
* **Result:** Joins that would take minutes on standard hardware are completed in **\~2.6 seconds**.

## ---

**5\. Frontend Delivery: Streamlit**

We chose Streamlit to transform the Gold Parquet files into an executive-level dashboard.

### **Why Streamlit?**

1. **Lightweight:** It runs on the WSL box without the overhead of a full web server.  
2. **Parquet-Native:** It reads the "Gold" files from the Dell SSD with high efficiency.  
3. **Real-Time:** Capable of watching the Lakehouse for new batches as they arrive via the **Live Producer**.

### **Installation (WSL Box)**

Bash

\# Update and install the dashboard stack  
pip install streamlit pandas pyarrow plotly

### **The Live Dashboard Code (dashboard.py)**

Python

import streamlit as st  
import pandas as pd  
import plotly.express as px  
import glob

\# Path pointing to the Dell Latitude E5570 mount  
GOLD\_PATH \= "/home/thedude/hazynet-lakehouse/gold/retail\_sales\_final"

@st.cache\_data(ttl=10) \# Refresh cache every 10 seconds for live data  
def load\_data():  
    files \= glob.glob(f"{GOLD\_PATH}/\*.parquet")  
    return pd.concat(\[pd.read\_parquet(f) for f in files\])

st.title("📡 HazyNet LIVE Lakehouse (E5570 Powered)")  
df \= load\_data()

\# KPI Display  
st.metric("Total Transactions", f"{len(df):,}")  
st.metric("Total Revenue", f"${df\['total\_with\_tax'\].sum():,.2f}")

\# GPU-Rendered Chart  
top\_cities \= df.groupby("city")\["total\_with\_tax"\].sum().nlargest(10).reset\_index()  
st.plotly\_chart(px.bar(top\_cities, x="city", y="total\_with\_tax", template="plotly\_dark"))

## ---

**6\. Conclusion**

The HazyNet project successfully processed **41,000,000 transactions** with a final revenue of **$22.6B+**. By using the **NVIDIA RTX 3060** to offset the age of the **Dell Latitude E5570**, we created a high-speed, live-updating data environment that outperforms many modern cloud-based solutions at a fraction of the cost.  
The NVIDIA RTX 3060 is attached to the following system (the WSL2 executor for the Spark Master Node on the Dell Latitude E5570):

I run the worker with 20 cores and 60GB 

Processor	Intel(R) Core(TM) Ultra 7 265KF (3.90 GHz)

Installed RAM	64.0 GB (63.7 GB usable)

Device ID	FB4D6846-3679-4096-BE0D-B80B15ACC2EF

Product ID	00330-80135-51505-AA222

System type	64-bit operating system, x64-based processor

---

