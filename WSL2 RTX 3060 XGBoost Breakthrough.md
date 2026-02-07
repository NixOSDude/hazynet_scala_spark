## **🛠️ System Configuration: The "WSL2 Stability" Layer**

The biggest hurdle was the **NCCL failure**. Because WSL2 is a virtualized environment, XGBoost's default GPU communication methods (P2P and Shared Memory) crash the kernel.

### **1\. The Environment File**

We locked these settings into the Zeppelin daemon to ensure the Spark Interpreter inherits them every time it starts.

**File Path:** /opt/zeppelin/conf/zeppelin-env.sh

**Command to Update:**

sudo tee /opt/zeppelin/conf/zeppelin-env.sh \<\<EOF  
export SPARK\_HOME=/opt/spark  
export ZEPPELIN\_PORT=8090  
export ZEPPELIN\_ADDR=0.0.0.0  
export ZEPPELIN\_MEM="-Xmx4g \-Xms1g"

\# Java 17 Unlocks for Spark 3.x  
export ZEPPELIN\_JAVA\_OPTS="-Djava.net.preferIPv4Stack=true \\  
  \--add-opens java.base/java.lang=ALL-UNNAMED \\  
  \--add-opens java.base/java.util=ALL-UNNAMED \\  
  \--add-opens java.base/java.lang.reflect=ALL-UNNAMED \\  
  \--add-opens java.base/java.util.concurrent=ALL-UNNAMED \\  
  \--add-opens java.base/sun.nio.ch=ALL-UNNAMED \\  
  \--add-opens java.base/java.math=ALL-UNNAMED \\  
  \--add-opens java.base/java.io=ALL-UNNAMED \\  
  \--add-opens java.base/java.net=ALL-UNNAMED \\  
  \--add-opens java.base/java.nio=ALL-UNNAMED"

\# WSL2 RTX 3060 Stability Flags (The "Secret Sauce")  
export NCCL\_P2P\_DISABLE=1  
export NCCL\_SHM\_DISABLE=1  
export NCCL\_SOCKET\_IFNAME=lo  
export NCCL\_DEBUG=INFO  
EOF

### **2\. Service Management Commands**

To apply changes or clear "hangs" on the **WSL Box**:

\# Restart Zeppelin  
/opt/zeppelin/bin/zeppelin-daemon.sh restart

\# Kill ghost Spark processes if the GPU hangs  
sudo pkill \-f zeppelin  
sudo pkill \-f spark

## ---

**🚀 The Successful Training Code (Hybrid Mode)**

We discovered that tree\_method \-\> gpu\_hist is currently unstable on WSL2. The solution is **Hybrid Mode**: Build the tree structure on the CPU and offload the heavy math/predictions to the GPU.

**Run in Zeppelin:**

Scala

%spark  
import ml.dmlc.xgboost4j.scala.{DMatrix, XGBoost \=\> NativeXGBoost}  
import org.apache.spark.sql.functions.\_  
import org.apache.spark.sql.types.\_

// 1\. DATA PREP  
val goldPath \= "/home/thedude/hazynet-lakehouse/gold/retail\_sales\_final"  
val df \= spark.read.parquet(goldPath)

// 2\. FEATURE ENGINEERING  
val localRows \= df.select(  
    col("total\_with\_tax").cast(FloatType),  
    col("tx\_id").cast(FloatType)  
).collect()

val labels \= localRows.map(r \=\> if(r.getFloat(0) \> 100) 1.0f else 0.0f)  
val features \= localRows.flatMap(r \=\> Array(r.getFloat(1), r.getFloat(0)))  
val dmat \= new DMatrix(features, localRows.length, 2, Float.NaN)  
dmat.setLabel(labels)

// 3\. STABLE WSL PARAMS  
val params: Map\[String, Any\] \= Map(  
  "objective" \-\> "binary:logistic",  
  "tree\_method" \-\> "hist",          // Builds on CPU (Bypasses NCCL)  
  "predictor" \-\> "gpu\_predictor",   // Heavy math on RTX 3060  
  "gpu\_id" \-\> 0,  
  "eta" \-\> 0.1,  
  "max\_depth" \-\> 8  
)

// 4\. TRAIN AND SAVE  
val nativeModel \= NativeXGBoost.train(dmat, params, 50)  
nativeModel.saveModel("/home/thedude/hazynet-lakehouse/models/wsl\_stable\_3060.model")

## ---

**📊 The Streamlit Integration (Python)**

**Server to run on:** WSL Box

**File:** /home/thedude/projects/hazynet-suite/app.py

Python

import streamlit as st  
import xgboost as xgb  
import numpy as np

\# Load the model we trained in Zeppelin  
model\_path \= "/home/thedude/hazynet-lakehouse/models/wsl\_stable\_3060.model"  
bst \= xgb.Booster()  
bst.load\_model(model\_path)

st.title("HazyNet Retail Predictor")  
st.write("Using RTX 3060 for Inference")

\# UI for user input  
tx\_id \= st.number\_input("Transaction ID", value=3690000)  
total \= st.number\_input("Transaction Total", value=150.0)

if st.button("Predict High Value"):  
    \# Prep data for XGBoost  
    data \= np.array(\[\[tx\_id, total\]\])  
    dtest \= xgb.DMatrix(data)  
      
    \# Predict  
    prediction \= bst.predict(dtest)\[0\]  
      
    if prediction \> 0.5:  
        st.success(f"High Value Target\! Probability: {prediction:.2f}")  
    else:  
        st.warning(f"Standard Transaction. Probability: {prediction:.2f}")

## ---

**✅ Summary of Success**

* **Data Source**: Dell Lakehouse Parquet Files.  
* **Compute**: WSL2 Ubuntu 22.04 with RTX 3060\.  
* **Key Discovery**: NCCL\_P2P\_DISABLE=1 and tree\_method=hist with gpu\_predictor is the only way to stay stable on WSL2.  
* **Artifact**: Binary model saved and verified at 10KB+.

