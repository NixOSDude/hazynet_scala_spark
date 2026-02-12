# Olympic Data

```scala
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._

// --- PURE FUNCTIONAL SCALA PROGRAMMING ---

// PURE LOADER: Specific for Athlete Data
val loadAthleteData: (String) => DataFrame = (path) => {
  val DF = spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(path)
        
  if (DF.isEmpty) {
    spark.emptyDataFrame
  } else {
    DF
  }
}

// PURE LOADER: Specific for Regions Data
val loadRegionsData: (String) => DataFrame = (path) => {
  val DF = spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(path)
  
  if (DF.isEmpty) {
    spark.emptyDataFrame
  } else {
    // Rule: Total If/Else logic using when/otherwise
    // Replacing NA/Nulls in regions with "none"
    DF.withColumn("notes",
      when(col("notes").isNull || col("notes") === "NA", lit("none"))
      .otherwise(col("notes"))
    )
  }
}

// after running head -n 20 athlete_events.csv (in linux - bash/terminal) I realized that for "medal" if
// an athlete never won a medal it has NA - so I decioded to replace with "no-medal" for logical readability
// other than that the csv seemed clean and strucured
// SAMPLE: 
// "1","A Dijiang","M",24,180,80,"China","CHN","1992 Summer",1992,"Summer","Barcelona","Basketball","Basketball Men's Basketball",NA

// Rule: Total If/Else logic using when/otherwise
// Rule: Replace NA with "no-medal" (String) and 0 (Numeric)
// Rule: O(n) complexity - single pass over the data

// --- PURE TRANSFORMER ---

val sanitizeAthletes: (DataFrame) => DataFrame = (df) => {
  if (df.isEmpty) {
    df
  } else {
    df.withColumn("Medal",  when(col("Medal") === "NA", lit("no-medal")).otherwise(col("Medal")))
      .withColumn("Height", when(col("Height") === "NA", lit(0)).otherwise(col("Height")))
      .withColumn("Weight", when(col("Weight") === "NA", lit(0)).otherwise(col("Weight")))
  }
}

// --- EXECUTION PIPELINE ---

val athleteRawPath = "/home/thedude/hazynet-lakehouse/raw/olympic_data/athlete_events.csv"
val regionsRawPath = "/home/thedude/hazynet-lakehouse/raw/olympic_data/noc_regions.csv"

// Loading using the pure functions
val athleteDF = sanitizeAthletes(loadAthleteData(athleteRawPath))
val regionsDF = loadRegionsData(regionsRawPath)

// write to cleaned dir on lakehouse
val cleanedAthletePath = "/home/thedude/hazynet-lakehouse/cleaned/olympic_athletes_functional"
val cleanedRegionsPath = "/home/thedude/hazynet-lakehouse/cleaned/olympic_regions_functional"

athleteDF.write.mode("overwrite").parquet(cleanedAthletePath)
regionsDF.write.mode("overwrite").parquet(cleanedRegionsPath)

println(s"SUCCESS: Data structured and saved to $cleanedAthletePath")
athleteDF.select("Name", "Medal", "Height").show(5)
```


```scala
import org.apache.spark.sql.DataFrame
import org.apache.spark.sql.functions._

// PURE FUNCTION: Joining with a Broadcast Hint to maintain O(n)
val enrichAthletesWithRegions: (DataFrame, DataFrame) => DataFrame = (athletes, regions) => {
  if (athletes.isEmpty || regions.isEmpty) {
    athletes // Return original if either is empty (Tenet: Always return a value)
  } else {
    // We use 'broadcast()' to force the small table into memory on all cores
    // This avoids the O(n log n) shuffle
    val joined = athletes.join(broadcast(regions), Seq("NOC"), "left")
    
    // Tenet: No Nulls. If an athlete's NOC isn't in the region table, fill it.
    joined.na.fill(Map(
      "region" -> "unknown-region",
      "notes" -> "none"
    ))
  }
}

// EXECUTION
// We are using the DataFrames we already loaded and cleaned in the previous step
val goldOlympicsDF = enrichAthletesWithRegions(athleteDF, regionsDF)

// Write to the Gold Layer on the Dell Lakehouse
val goldPath = "/home/thedude/hazynet-lakehouse/gold/olympics_enriched"
goldOlympicsDF.write.mode("overwrite").parquet(goldPath)

println(s"GOLD LAYER CREATED: $goldPath")
goldOlympicsDF.select("Name", "NOC", "region", "Medal").show(10)
```


```scala
import org.apache.spark.sql.{DataFrame, Column}
import org.apache.spark.sql.functions._
import scala.annotation.tailrec

// 1. Define our target medals
val medalTypes = List("Gold", "Silver", "Bronze")

// 2. The Tail-Recursive Function
// Accumulates columns for each medal type in a single pass
@tailrec
def countMedalsRecursive(df: DataFrame, medals: List[String]): DataFrame = {
  if (medals.isEmpty) {
    df
  } else {
    val medalName = medals.head
    // Add a column that acts as a binary flag (1 if won, 0 if not)
    // Mandatory else: otherwise(lit(0))
    val updatedDf = df.withColumn(s"is_$medalName", 
      when(col("Medal") === medalName, lit(1)).otherwise(lit(0))
    )
    
    // Tail call: passing the updated DF and the remaining list
    countMedalsRecursive(updatedDf, medals.tail)
  }
}

// 3. Execution
// Step A: Flag the medals using recursion
val flaggedDf = countMedalsRecursive(goldOlympicsDF, medalTypes)

// Step B: Aggregate at O(n)
val medalTallies = flaggedDf
  .groupBy("region")
  .agg(
    sum("is_Gold").as("Gold_Total"),
    sum("is_Silver").as("Silver_Total"),
    sum("is_Bronze").as("Bronze_Total")
  )
  .na.fill(0) // Tenet: No Nulls

// 4. Save the Final Analytics
medalTallies.write.mode("overwrite").parquet("/home/thedude/hazynet-lakehouse/gold/medal_tallies_by_region")

println("RECURSIVE TALLY COMPLETE: Metadata-driven aggregation achieved.")
medalTallies.orderBy(desc("Gold_Total")).show(10)
```


```scala

```

