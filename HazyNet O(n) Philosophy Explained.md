

Here is why my Spark-Scala code is adhering to my  O(n) philosophy:

### **1\. Join Complexity: O(n) vs O(n \\log n)**

In standard Spark, a join between two large tables usually triggers a **Sort-Merge Join**. This requires sorting both sides (O(n \\log n)) and a "Shuffle" (moving data across the network), which is the biggest performance killer.

* **Our Approach:** By using **Broadcast Joins** for your metadata (Customers and Cities), we avoided the sort entirely. The large 41M transaction table is simply scanned once, and each row is matched against a hash table in the GPU's memory. This turns a complex join into a **linear scan: O(n)**.

### **2\. Aggregation: Hash over Sort**

When we ran that 2.6-second revenue check, Spark used a **HashAggregate** strategy.

* **Why it's O(n):** Instead of sorting all 41 million rows to group them by city, the GPU built a hash map. It looks at each row exactly once, adds the value to the corresponding "bucket," and moves on.

* **The GPU Edge:** The RTX 3060 does this in parallel across thousands of CUDA cores, but the algorithmic complexity remains linear.

### **3\. Storage I/O: The Parquet Advantage**

Because we are using **Parquet**, we aren't just reading n (the whole file); we are reading n (only the specific columns we need).

* By skipping the columns we don't need for a specific query, we effectively reduce the constant factor of our O(n) operations, making the "linear" time feel even faster.

### ---

**The "O(n) Reality Check"**

| Operation | Traditional Spark | HazyNet Setup | Complexity |
| :---- | :---- | :---- | :---- |
| **Data Seeding** | Sequential Write | Parallelized Partitioning | O(n) |
| **Tax Calculation** | CPU Row-by-Row | GPU Vectorized | O(n) |
| **Enrichment (Join)** | Sort-Merge (O(n \\log n)) | **Broadcast Hash (O(n))** | **O(n)** |
| **Revenue Sum** | SortAggregate (O(n \\log n)) | **HashAggregate (O(n))** | **O(n)** |

**The HazyNet Mantra:** If you have to sort it, you've already lost. We don't sort; we hash and stream.

### ---

