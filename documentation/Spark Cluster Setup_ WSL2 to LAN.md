# **Distributed Spark Cluster Setup: Ultra 7 "Muscle" Node**

This document serves as the technical  setup guide for integrating a Windows 11 WSL2 (Ubuntu 22.04) environment as a dedicated Worker node into a physical Spark cluster.

## ---

**1\. Network Architecture**

* **Master Node (Lighthouse):** Physical Ubuntu Server (192.168.68.56)  
* **Worker Node (Muscle):** Ultra 7 WSL2 Instance (Host: 192.168.68.52)  
* **The Bridge:** Traffic must flow from the WSL2 virtual subnet (172.x.x.x) through the Windows Host adapter to the physical LAN.

## ---

**2\. Identified Obstacles & Hurdles**

### **I. Port Conflicts**

The Master Web UI (defaulting to 8080\) was originally blocked by a Docker-proxy service (Roundcube).

* **Solution:** Decommissioned Docker services and verified port availability using netstat \-tulnp.

### **II. WSL2 Loopback & Binding (The java.net.BindException)**

WSL2 does not "own" the Windows LAN IP. Attempting to bind Spark directly to 192.168.68.52 resulted in a failure to assign the requested address.

* **Hurdle:** Spark needs to listen internally but advertise externally.

### **III. Windows Firewall Silent Drops**

Even with ports open, the Windows Hyper-V firewall often filters traffic between the WSL virtual interface and external LAN IPs.

* **Symptom:** telnet to the Master IP on port 7077 hung on "Trying...".

## ---

**3\. Step-by-Step Configuration**

### **Step 1: Windows Host Preparation**

Run as **Administrator** in PowerShell to open the necessary communication gates:

PowerShell

\# Open inbound ports for Spark Master/Worker/UI communication  
New-NetFirewallRule \-DisplayName "Spark Cluster" \-Direction Inbound \-Action Allow \-Protocol TCP \-LocalPort 7077,8080,8081,4040

\# Disable firewall filtering on the WSL Virtual Ethernet adapter to allow LAN routing  
Set-NetFirewallProfile \-Profile Domain,Public,Private \-DisabledInterfaceAliases "vEthernet (WSL (Hyper-V firewall))"

### **Step 2: Spark Environment Config**

Located in /opt/spark/conf/spark-env.sh on the Ultra 7 node:

Bash

SPARK\_WORKER\_MEMORY=48G  
SPARK\_WORKER\_CORES=12

### **Step 3: Launching the Worker (The "Bond" Command)**

The Worker is launched using a specific configuration to resolve the WSL2 NAT issue. We use \-i to bind to the local WSL IP and \--host to advertise the reachable Windows IP to the Master.

Bash

/opt/spark/bin/spark-class org.apache.spark.deploy.worker.Worker \\  
  spark://192.168.68.56:7077 \\  
  \--host 192.168.68.52 \\  
  \-i $(hostname \-I | awk '{print $1}')

## ---

**4\. Success Verification**

### **Handshake Confirmation**

The Worker log must output the following to confirm successful registration:

INFO Worker: Successfully registered with master spark://192.168.68.56:7077

### **Cluster Statistics**

* **Master UI (http://192.168.68.56:8080):** Shows 1 Alive Worker.  
* **Available Resources:** 12 Cores, 48GB RAM.  
* **Worker UI (http://localhost:8081):** Displays the active connection to the Dell Lighthouse Master.

## ---

**5\. Distributed Test Execution**

To verify the data plane, a Pi calculation was executed via spark-shell, successfully distributing tasks across the network:

Scala

val count \= sc.parallelize(1 to 10000000).map { i \=\>  
  val x \= Math.random(); val y \= Math.random()  
  if (x\*x \+ y\*y \< 1) 1 else 0  
}.reduce(\_ \+ \_)  
println(s"Pi is roughly ${4.0 \* count / 10000000}")

**Result:** Cluster utilized all 12 cores on the Ultra 7 to return a distributed result:

/opt/spark/bin/spark-shell \--master spark://192.168.68.56:7077

26/02/05 13:07:29 WARN Utils: Your hostname, DESKTOP-UNU6EP2 resolves to a loopback address: 127.0.1.1; using 10.255.255.254 instead (on interface lo)

26/02/05 13:07:29 WARN Utils: Set SPARK\_LOCAL\_IP if you need to bind to another address

Setting default log level to "WARN".

To adjust logging level use sc.setLogLevel(newLevel). For SparkR, use setLogLevel(newLevel).

26/02/05 13:07:32 WARN NativeCodeLoader: Unable to load native-hadoop library for your platform... using builtin-java classes where applicable

Spark context Web UI available at http://10.255.255.254:4040

Spark context available as 'sc' (master \= spark://192.168.68.56:7077, app id \= app-20260205200732-0000).

Spark session available as 'spark'.

Welcome to

      \_\_\_\_              \_\_

     / \_\_/\_\_  \_\_\_ \_\_\_\_\_/ /\_\_

    \_\\ \\/ \_ \\/ \_ \`/ \_\_/  '\_/

   /\_\_\_/ .\_\_/\\\_,\_/\_/ /\_/\\\_\\   version 3.5.8

      /\_/

         

Using Scala version 2.12.18 (OpenJDK 64-Bit Server VM, Java 17.0.18)

Type in expressions to have them evaluated.

Type :help for more information.

scala\> val count \= sc.parallelize(1 to 10000000).map { i \=\>

     |   val x \= Math.random()

     |   val y \= Math.random()

     |   if (x\*x \+ y\*y \< 1\) 1 else 0

     | }.reduce(\_ \+ \_)

count: Int \= 7854381                                                          


scala\> println(s"Pi is roughly ${4.0 \* count / 10000000}")

