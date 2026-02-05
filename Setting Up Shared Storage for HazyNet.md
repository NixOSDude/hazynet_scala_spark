### ---

**1\. Finalize the WSL Mount (Ultra 7\)**

\# This uses the Windows credentials   
sudo mount \-t drvfs '\\\\192.168.68.56\\hazynet-core' /mnt/hazynet-core

### **2\. Verify the Data Bridge**

Once mounted, check to see if the project files (like build.sbt) appear in Linux:

Bash

ls \-la /mnt/hazynet-core

### ---

**3\. The "HazyNet" Project Workflow**

* **Development:** Write Scala code in your IDE on the **Ultra 7**.  
* **Compilation:** Run sbt package or sbt assembly on the **Ultra 7**. Because of the mount, the resulting JAR file will automatically "land" on the Dell server's disk.  
* **Execution:** Run spark-submit from either machine, pointing to the shared path.

### **Updated Git Documentation (Shared Storage)**

\#\# 5\. Shared Storage Architecture (Samba \+ DrvFS)  
To eliminate manual file transfers (SCP), a shared project volume was established.

\* **\*\*Server:\*\*** Dell Lighthouse (Samba share on \`/home/thedude/projects/hazynet-core\`)  
\* **\*\*Client:\*\*** Ultra 7 Muscle (WSL2 mount via \`drvfs\`)  
\* **\*\*Mount Point:\*\*** \`/mnt/hazynet-core\`

**\*\*Hurdle:\*\*** "Host is down" / "Authentication failure."  
**\*\*Resolution:\*\*** Forced Windows to cache credentials by mapping the drive in File Explorer using the IP-prefix user format: \`192.168.68.56\\thedude\`.  
