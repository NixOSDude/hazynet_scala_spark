## **Hazynet Lakehouse: Medallion Pipeline & FP Documentation**

This document captures the end-to-end transformation logic used to process user and Olympic data on the WSL environment, adhering to the **4 Tenets of Functional Programming**: Immutability, No Nulls, Total Functions (always returning a value), and Pure Functions.

### ---

**1\. Bronze to Silver: The User Ingestion (dirty\_users\_01)**

We began by ingesting raw, inconsistent data and forcing it into a predictable, clean format.

* **The Problem:** The name column contained erratic whitespace (ALEX smith), inconsistent casing (jessica JONES), and placeholder values (Unknown). The active column used mixed types (TRUE, false, 1, 0).  
* **The Specialist Fix:** \* Applied trim and regexp\_replace(col("name"), "\\\\s+", " ") to collapse internal whitespace.  
  * Used initcap to standardize name casing (e.g., "Jessica Jones").  
  * Implemented a **Total Function** via when/otherwise logic to map 1, 0, TRUE, and false into a strict Boolean is\_active column.  
* **Result:** A clean Silver table where "Unknown" became NA and types were strictly enforced.

### ---

**2\. Silver to Gold: The Olympic Enrichment**

This phase focused on **Type Honesty** and **Data Relational Integrity**.

* **The Schema Conflict:** Casting to the OlympicHost Case Class initially failed due to:  
  1. **Type Error:** year was a String in Parquet but required an Int in Scala.  
  2. **Naming Error:** The file used City (uppercase), but the Case Class required city (lowercase).  
* **The Specialist Fix:** \* Standardized types using .withColumn("year", col("year").cast("int")).  
  * Aligned the schema using .select(col("City").as("city")).  
* **The Join (Relational Enrichment):** \* **Logic:** .join(nocDF, Seq("NOC"), "left") joined the athlete data with noc\_regions.csv.  
  * **Issue:** The CSV used old Mac-style line endings (\\r), causing parsing failures.  
  * **Fix:** Explicitly set .option("lineSep", "\\r") to correctly parse all 230+ regions.

### ---

**3\. The Mechanics of $O(n)$ Joins**

In Big Data, not all joins are created equal. We maintained linear performance through Spark optimizations.

* **The Broadcast:** Spark sends the tiny noc\_regions table (230 rows) to every executor node.  
* **The Hash Map:** Each executor builds an in-memory Hash Map of the regions.  
* **The Stream:** Spark streams the $n$ athlete records. For every record, it performs a Hash Map lookup.  
* **Complexity:** Since Hash Map lookups are $O(1)$, doing this $n$ times results in **$O(n)$** total complexity.  
* **Why this fits our Tenets:** Unlike a Sort-Merge Join ($O(n \\log n)$), which requires network shuffling and sorting, the Broadcast Join maintains linear performance, ensuring the pipeline stays fast as the data grows.

### ---

**4\. Gold Insights: Transformation & Aggregation**

We applied pure functional transformations to extract business value from the enriched data.

* **Pure Function transformhosts:**  
  * **Predicate:** Filtered for years \> 2014 (validating that our code handles non-empty results and empty sets with equal reliability).  
  * **Immutability:** Used .map(host \=\> host.copy(city \= host.city.toUpperCase)) to create new objects rather than mutating existing ones.  
* **Aggregation:** Grouped the 13,688 records by country to count athlete participation.  
* **The Conclusion:** The USA (719), Brazil (583), and China (546) emerged as the top participants in the post-2014 window.

### ---

**Final System State**

| Layer | Path | Format | Status |
| :---- | :---- | :---- | :---- |
| **Bronze** | \~/hazynet-lakehouse/raw/ | CSV | Raw / Untrusted |
| **Silver** | In-Memory / DataFrames | DF | Cleaned / Standardized |
| **Gold** | \~/gold/participation\_summary | Parquet | **Pinned & Verified** |

Code for bronze/silver layer:

import org.apache.spark.sql.functions.\_

val bronzePath \= "/home/thedude/hazynet-lakehouse/raw/dirty\_users.csv"

val rawDF \= spark.read  
  .option("header", "true")  
  .option("sep", "|")  
  .option("inferSchema", "true")  
  .csv(bronzePath)  
    
val silverDF \= rawDF.select(  
  col("user\_id").as("id"),  
    
  when(trim(col("name")) \=== "Unknown", "NA")  
    .otherwise(  
        initcap(  
          regexp\_replace(trim(col("name")), "\\\\s+", " ")  
        )  
    )  
    .as("full\_name"),  
    
  col("signup\_date"),  
    
  when(trim(col("active")) \=== "1" || upper(trim(col("active")))  \=== "TRUE", true)  
    .otherwise(false)  
    .as("is\_active")  
      
)  
    
rawDF.show()  
rawDF.printSchema()

silverDF.show()  
silverDF.printSchema()

\+-------+---------------+-----------+------+  
|user\_id|           name|signup\_date|active|  
\+-------+---------------+-----------+------+  
|    101|   SCOTT baker | 2026-01-01|  TRUE|  
|    102|    ALEX  smith| 2026-02-15| false|  
|    103| jessica JONES | 2025-12-25|     1|  
|    104|        Unknown| 2026-01-10|     0|  
\+-------+---------------+-----------+------+

root  
 |-- user\_id: integer (nullable \= true)  
 |-- name: string (nullable \= true)  
 |-- signup\_date: date (nullable \= true)  
 |-- active: string (nullable \= true)

\+---+-------------+-----------+---------+  
| id|    full\_name|signup\_date|is\_active|  
\+---+-------------+-----------+---------+  
|101|  Scott Baker| 2026-01-01|     true|  
|102|   Alex Smith| 2026-02-15|    false|  
|103|Jessica Jones| 2025-12-25|     true|  
|104|           NA| 2026-01-10|    false|  
\+---+-------------+-----------+---------+

root  
 |-- id: integer (nullable \= true)  
 |-- full\_name: string (nullable \= true)  
 |-- signup\_date: date (nullable \= true)  
 |-- is\_active: boolean (nullable \= false)

import org.apache.spark.sql.functions.\_  
bronzePath: String \= /home/thedude/hazynet-lakehouse/raw/dirty\_users.csv  
rawDF: org.apache.spark.sql.DataFrame \= \[user\_id: int, name: string ... 2 more fields\]  
silverDF: org.apache.spark.sql.DataFrame \= \[id: int, full\_name: string ... 2 more fields\]

Gold layer code:

import org.apache.spark.sql.Dataset  
import org.apache.spark.sql.functions.\_

case class OlympicHost(  
      
    year: Int,  
    city: String,  
    country: Option\[String\]  
      
    )  
      
val goldPath \= "/home/thedude/hazynet-lakehouse/gold/olympics\_enriched"  
val nocPath \= "/home/thedude/hazynet-lakehouse/raw/olympic\_data/noc\_regions.csv"

val nocDF \= spark.read  
  .option("header", "true")  
  .option("lineSep", "\\r")  
  .csv(nocPath)  
  .select(  
      col("NOC"),  
      col("region").as("country")  
  )  
  

val baseDF \= spark.read.parquet(goldPath)

val hostDS: Dataset\[OlympicHost\] \= baseDF  
  .join(nocDF, Seq("NOC"), "left")  
  .select(  
      col("year").cast("int"),  
      col("City").as("city"),  
      col("country")  
    )  
      .as\[OlympicHost\]  
    
hostDS.show()

def transformhosts (ds:Dataset\[OlympicHost\]): Dataset\[OlympicHost\] \= {  
      
    ds  
      .filter(host \=\> host.year \> 2014\)  
      .map(host \=\> host.copy(city \= host.city.toUpperCase))  
      
}  
\+----+-----------+-----------+  
|year|       city|    country|  
\+----+-----------+-----------+  
|1992|  Barcelona|      China|  
|2012|     London|      China|  
|1920|  Antwerpen|    Denmark|  
|1900|      Paris|    Denmark|  
|1988|    Calgary|Netherlands|  
|1988|    Calgary|Netherlands|  
|1992|Albertville|Netherlands|  
|1992|Albertville|Netherlands|  
|1994|Lillehammer|Netherlands|  
|1994|Lillehammer|Netherlands|  
|1992|Albertville|        USA|  
|1992|Albertville|        USA|  
|1992|Albertville|        USA|  
|1992|Albertville|        USA|  
|1994|Lillehammer|        USA|  
|1994|Lillehammer|        USA|  
|1994|Lillehammer|        USA|  
|1994|Lillehammer|        USA|  
|1992|Albertville|        USA|  
|1992|Albertville|        USA|  
\+----+-----------+-----------+  
only showing top 20 rows

val finalGoldDS \= transformhosts(hostDS)  
finalGoldDS.show()  
println(s"Records after 2014: ${finalGoldDS.count()}")  
\+----+--------------+-----------+  
|year|          city|    country|  
\+----+--------------+-----------+  
|2016|RIO DE JANEIRO|    Romania|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Spain|  
|2016|RIO DE JANEIRO|      Italy|  
|2016|RIO DE JANEIRO| Azerbaijan|  
|2016|RIO DE JANEIRO|     France|  
|2016|RIO DE JANEIRO|    Algeria|  
|2016|RIO DE JANEIRO|    Bahrain|  
|2016|RIO DE JANEIRO|Netherlands|  
|2016|RIO DE JANEIRO|       Iraq|  
|2016|RIO DE JANEIRO|    Ireland|  
|2016|RIO DE JANEIRO|    Ireland|  
|2016|RIO DE JANEIRO|        USA|  
|2016|RIO DE JANEIRO|      Egypt|  
|2016|RIO DE JANEIRO|      Egypt|  
\+----+--------------+-----------+

val participationCounts \= finalGoldDS  
  .groupBy("country")  
  .count()  
  .orderBy(desc("count"))

participationCounts.show(10)

\+---------+-----+  
|  country|count|  
\+---------+-----+  
|      USA|  719|  
|   Brazil|  583|  
|    China|  546|  
|  Germany|  536|  
|Australia|  518|  
|   France|  512|  
|       UK|  478|  
|    Japan|  436|  
|   Russia|  406|  
|   Canada|  405|  
\+---------+-----+

// Define the destination for our final gold insights  
val finalSummaryPath \= "file:///home/thedude/hazynet-lakehouse/gold/participation\_summary"

// Save using our FP tenets (Overwrite mode for idempotency)  
participationCounts.write  
  .mode("overwrite")  
  .parquet(finalSummaryPath)

println(s"Specialist Insight saved to: $finalSummaryPath")

