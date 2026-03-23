<!-- loio6e1af2743721420782fcb82472c9ce86 -->

# Overview

Get an overview of SAP Advanced Financial Closing.



<a name="loio6e1af2743721420782fcb82472c9ce86__section_ur1_hlm_scb"/>

## About This Guide

This administration guide describes the steps you need to perform as an administrator to set up and run SAP Advanced Financial Closing. It covers application-specific information only. For general information about SAP Business Technology Platform \(SAP BTP\), see the [documentation on the SAP Help Portal](https://help.sap.com/docs/BTP?locale=en-US).

This guide addresses the following target audience:

-   System administrators

-   Accounting experts

-   Accounting managers




<a name="loio6e1af2743721420782fcb82472c9ce86__section_ow4_5lm_scb"/>

## About SAP Advanced Financial Closing

SAP Advanced Financial Closing supports you in planning, processing, monitoring, and analyzing financial closing tasks for the entities of your group. For more information about using the functions and features provided, see the [user guide](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/239ab375e0334c149082cc6851644e8b.html "Provides details about the changes made in each version of this document.") :arrow_upper_right:.

SAP Advanced Financial Closing is an SAP BTP application that runs in an SAP BTP subaccount. The SAP BTP subaccount is associated with an SAP BTP global account. Your organization may have several SAP BTP global accounts. Please clarify with your sales representative in which SAP BTP global account your entitlement to SAP Advanced Financial Closing should be contained. If you have no previous SAP BTP global account, a new one needs to be created. Your sales representative will assist you.

The following graphic shows a high-level architecture. The solution is an application on SAP BTP in the Cloud Foundry environment, which you can connect to SAP S/4HANA Cloud Public Edition, SAP S/4HANA Cloud Private Edition, SAP S/4HANA, or SAP ERP as your financial communication systems. The integration scenario to SAP systems uses OData services for SAP S/4HANA Cloud Public Edition, SAP S/4HANA Cloud Private Edition, and SAP S/4HANA systems, and a REST service for SAP ERP systems. SAP HANA is used as a database, and attachments are stored in the Object Store on SAP BTP. You must have an identity provider \(IdP\) to be able to configure your user management.

![Diagram of the solution's high-level architecture with an SAP Fiori UI, the SAP Advanced
                                                  Financial Closing
							back end, the SAP
                                                HANA
							database, as well as the object store on SAP BTP: Either
							an SAP IdP or a customer IdP serves as entry point to the SAP Advanced
                                                  Financial Closing back
							end. The system’s front end, back end, and databases are part of the
								SAP BTP
							subaccount for the Cloud Foundry environment on SAP side. The SAP
                                                HANA
							database and the object store on SAP BTP form
							the database component. The front end is represented by the SAP Fiori
							UI. The SAP Advanced
                                                  Financial Closing back
							end has two communication channels: one with SAP S/4HANA
                                                  Cloud Public Edition
							on SAP side and one with the customer’s SAP BTP
							subaccount. The customer’s SAP BTP
							subaccount contains three components: subscription to SAP Advanced
                                                  Financial Closing,
							security controlled through roles and role collections, and the
							connectivity component represented by destination service and cloud
							connectors. This connectivity component is connected to the customer’s
							system of type SAP S/4HANA
                                                  Cloud Private Edition, SAP
                                                S/4HANA
							or SAP ERP.
							Some of the graphic's areas are interactive and link to more information
							within this administration guide.](images/AFC_High-Level_Architecture_Diagram_726b4eb.png)

-   **[Data Flow from and to SAP Advanced Financial Closing](data-flow-from-and-to-sap-advanced-financial-closing-56103b0.md "Understand the data flow between SAP Advanced
                                                  Financial Closing and connected financial communication
		systems.")**  
Understand the data flow between SAP Advanced Financial Closing and connected financial communication systems.
-   **[Language Scope](language-scope-4f635b9.md "See in which languages SAP Advanced
                                                  Financial Closing is available.")**  
See in which languages SAP Advanced Financial Closing is available.

**Related Information**  


[Data Flow from and to SAP Advanced Financial Closing](data-flow-from-and-to-sap-advanced-financial-closing-56103b0.md "Understand the data flow between SAP Advanced Financial Closing and connected financial communication systems.")

[Language Scope](language-scope-4f635b9.md "See in which languages SAP Advanced Financial Closing is available.")

