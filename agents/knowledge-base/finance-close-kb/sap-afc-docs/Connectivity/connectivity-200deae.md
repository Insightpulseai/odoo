<!-- loio200deaea523b48da939c33fcf8f2e0e4 -->

# Connectivity

Connect your financial cloud or on-premise systems to SAP Advanced Financial Closing.

You can connect SAP Advanced Financial Closing to the following solutions:

-   SAP S/4HANA Cloud Public Edition

-   SAP S/4HANA Cloud Private Edition 2020 and all following releases

-   SAP S/4HANA 1809 SPS04 and higher

-   SAP S/4HANA 1909 FPS02 and higher

-   SAP S/4HANA 2020 and all following releases

-   SAP ERP 6.0, enhancement package 4 and higher


> ### Note:  
> Some functions may be available only as of higher SPs or back-end releases.

For more information about connectivity, see the SAP BTP documentation under [Connectivity in the Cloud Foundry Environment](https://help.sap.com/viewer/cca91383641e40ffbe03bdc78f00f681/Cloud/en-US/34010ace6ac84574a4ad02f5055d3597.html).



<a name="loio200deaea523b48da939c33fcf8f2e0e4__section_j4f_b4j_rkb"/>

## Use

The connection allows you to do the following, for example:

-   In the *Manage Closing Task Lists* app:

    -   You can assign communication systems to your task list templates. Business attributes, such as the factory calendar or ledger, are then governed by the financial communication system specified and are incorporated into the task list template.


-   In the *Process Closing Tasks* app:

    -   When you process tasks of type *SAP Fiori Application* in a task list defined for the respective communication system, you’re automatically forwarded to the app in the respective system's launchpad.

        > ### Note:  
        > If the closing business transaction type refers to a transaction and not to a semantic object and action, you automatically navigate to the transaction rendered as html GUI. In this case, the following rules apply:
        > 
        > -   The Internet Transaction Server \(ITS\) has to be active in your communication system. This is set up by default.
        > 
        > -   The user processing the task needs to have a user in the communication system and be authenticated, ideally using single sign-on \(SSO\).
        > 
        > -   Context parameters such as fiscal year, fiscal year period and company code are **not** handed over to the target window.


    -   When you process tasks of type *Job* that are run in the communication system, the status and results of these scheduling jobs are returned to SAP Advanced Financial Closing. You can see the details for each task in the *Monitor Business Logs* app. For more information, see [Logging](../Monitoring-and-Troubleshooting/logging-57375b8.md).





<a name="loio200deaea523b48da939c33fcf8f2e0e4__section_lkp_by3_s5b"/>

## What Does This Documentation Cover?

The following graphic lists the documentation for connectivity and system monitoring:

![Graphic depicting different text boxes: The text boxes list the documentation available for this app. For connections to
							communication systems, find more information under SAP S/4HANA Cloud Public Edition, SAP S/4HANA Cloud Private Edition,
							SAP S/4HANA, and SAP ERP. For communication system management, find more information about monitoring communication
							systems and about deleting the connection to communication systems. For more details about the synchronization with
							communication systems, find more information under Synchronization of Communication Systems.](images/Image_Map_Cover_for_Connectivity_Section_d09ddd1.png)

-   **[Specify Communication Systems](specify-communication-systems-7e2136a.md "You use the Specify Communication
                                                  Systems app
		to connect your communication systems to SAP Advanced
                                                  Financial Closing.")**  
You use the *Specify Communication Systems* app to connect your communication systems to SAP Advanced Financial Closing.
-   **[Requirements for Communication Systems](requirements-for-communication-systems-12f664f.md "Understand which system releases and SAP Notes are required for SAP Advanced
                                                  Financial Closing to run
		correctly.")**  
Understand which system releases and SAP Notes are required for SAP Advanced Financial Closing to run correctly.
-   **[SAP S/4HANA Cloud Public Edition](sap-s-4hana-cloud-public-edition-60448a7.md "Connect to your financial cloud system to retrieve information about organizational
		units, the factory calendar, and so on.")**  
Connect to your financial cloud system to retrieve information about organizational units, the factory calendar, and so on.
-   **[SAP S/4HANA Cloud Private Edition](sap-s-4hana-cloud-private-edition-66be898.md "Connect to your financial cloud system to retrieve information about organizational
		units, the factory calendar, and so on.")**  
Connect to your financial cloud system to retrieve information about organizational units, the factory calendar, and so on.
-   **[SAP S/4HANA](sap-s-4hana-15a3a5b.md "Perform the following steps to connect SAP Advanced
                                                  Financial Closing to your SAP
                                                S/4HANA system. Perform the last
		two steps only if they apply to your use case.")**  
Perform the following steps to connect SAP Advanced Financial Closing to your SAP S/4HANA system. Perform the last two steps only if they apply to your use case.
-   **[SAP ERP](sap-erp-7b85121.md "Perform the following steps to connect SAP Advanced
                                                  Financial Closing to your SAP ERP system. Perform the last
		step only if it applies to your use case.")**  
Perform the following steps to connect SAP Advanced Financial Closing to your SAP ERP system. Perform the last step only if it applies to your use case.
-   **[SAP Build Process Automation](sap-build-process-automation-7385663.md "Perform the following steps to connect SAP Advanced
                                                  Financial Closing to your SAP Build
                                                  Process Automation system.")**  
Perform the following steps to connect SAP Advanced Financial Closing to your SAP Build Process Automation system.
-   **[SAP Accounting Automation by BlackLine](sap-accounting-automation-by-blackline-ce92690.md "Perform the following steps to connect SAP Advanced
                                                  Financial Closing to SAP
                                                Accounting Automation by BlackLine.")**  
Perform the following steps to connect SAP Advanced Financial Closing to SAP Accounting Automation by BlackLine.
-   **[External Systems](external-systems-9ca3083.md "Connect to your external financial system to retrieve information about organizational
		units, the factory calendar, and so on.")**  
Connect to your external financial system to retrieve information about organizational units, the factory calendar, and so on.
-   **[How to Delete the Connection to a Communication System](how-to-delete-the-connection-to-a-communication-system-9c0a0d9.md "Delete the connection between SAP Advanced
                                                  Financial Closing and the communication
		system.")**  
Delete the connection between SAP Advanced Financial Closing and the communication system.
-   **[Synchronization of Communication Systems](synchronization-of-communication-systems-a86348d.md "Get an overview of the synchronization and validation of data.")**  
Get an overview of the synchronization and validation of data.
-   **[Disrupted System Connection](disrupted-system-connection-42df991.md "")**  


