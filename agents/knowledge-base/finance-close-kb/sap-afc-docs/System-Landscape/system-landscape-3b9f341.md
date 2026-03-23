<!-- loio3b9f341b96864674b22e11925cb6a6bb -->

# System Landscape

Understand the system landscape of SAP Advanced Financial Closing.



<a name="loio3b9f341b96864674b22e11925cb6a6bb__section_x4j_hjp_psb"/>

## Overview

SAP Advanced Financial Closing is a cloud-based hub and can be connected to multiple system instances called communication systems. Therefore, SAP Advanced Financial Closing is only **one instance**. There is no separation into different instances - neither by type, such as development \(D\), quality \(Q\), or production \(P\) systems, nor by system, such as SAP S/4HANA Cloud Public Edition, SAP S/4HANA Cloud Private Edition, SAP S/4HANA, or SAP ERP. They're all connected to the same instance of SAP Advanced Financial Closing. The benefit of this architecture is that financial close cycles often require spontaneous and quick changes of closing tasks. With SAP Advanced Financial Closing as a single closing hub instance, no transport mechanism or change request is needed, which enables faster reaction times.



### Content

All access and reporting can be controlled for each communication system individually.

Task list templates and task lists are created for specific communication systems and can't be reassigned to other communication systems. Nodes within the closing structure are assigned to a specific communication system upon creation.

> ### Caution:  
> The assignment can't be changed later.

In addition to the production instance of SAP Advanced Financial Closing, you can acquire an additional license to use a test tenant too. You can then connect a non-production ERP system to this tenant.

> ### Tip:  
> For information about the release times for test and production tenant, see [Release Schedules and Maintenance Windows](https://help.sap.com/viewer/8958d29f959749afa3a30f9bf562aaca/SHIP/en-US/8256792f91704e89ac296ede87327510.html "More information about release schedules and maintenance windows") :arrow_upper_right:.

The following graphic shows the recommended system landscape if you're using a test tenant, that is, keeping the test tenant environment completely separated from the production tenant environment.

![Graphic depicting the individual communication arrangements of SAP Advanced
                                                  Financial Closing
								with the systems connected: On the left, the test tenant is shown
								connected to a non-production system, such as a sandbox or Q system.
								On the right, the production tenant is shown connected to three
								systems, a D system, a Q system, and a P system. Test and production
								tenant are kept completely separate.](images/Image_Map_System_Landscape_DQP_Test_Tenant_ff32915.png)

