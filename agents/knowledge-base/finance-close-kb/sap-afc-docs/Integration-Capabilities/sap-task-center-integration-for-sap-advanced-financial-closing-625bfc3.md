<!-- loio625bfc3f35b24b2ba102384c691f3a32 -->

# SAP Task Center Integration for SAP Advanced Financial Closing

To use SAP Task Center together with your SAP Advanced Financial Closing subaccount, you need to configure a custom Identity Authentication service that supports global user IDs.



<a name="loio625bfc3f35b24b2ba102384c691f3a32__section_ltx_tjc_gzb"/>

## Use

SAP Task Center requires recipients of forms to be defined as global user IDs \(as individual users or as members of groups\).

The default identity provider does not support global user IDs. To use these IDs, you configure a trust relationship with a custom identity provider based on SAP Cloud Identity Services - Identity Authentication as the identity provider. This is the identity provider that you also use to manage access to the SAP Task Center application.

Depending on whether your SAP Advanced Financial Closing instance and SAP Task Center reside on the same subaccount or on different ones, the configuration procedure differs slightly. Find more information on the following pages:

-   **[Supported Use Cases](supported-use-cases-dc59212.md "Overview of the SAP Advanced
                                                  Financial Closing use
		cases supported by SAP Task
                                                  Center.")**  
Overview of the SAP Advanced Financial Closing use cases supported by SAP Task Center.
-   **[How to Set Up the SAP Task Center Integration Using the Same Subaccount](how-to-set-up-the-sap-task-center-integration-using-the-same-subaccount-0ad15cd.md "You have one subaccount in which SAP Advanced
                                                  Financial Closing and SAP Task
                                                  Center are set
		up.")**  
You have one subaccount in which SAP Advanced Financial Closing and SAP Task Center are set up.
-   **[How to Set Up the SAP Task Center Integration Using Different Subaccounts](how-to-set-up-the-sap-task-center-integration-using-different-subaccounts-98629e1.md "You have one subaccount in which SAP Advanced
                                                  Financial Closing is set up and another
		subaccount where SAP Task
                                                  Center
		is set up.")**  
You have one subaccount in which SAP Advanced Financial Closing is set up and another subaccount where SAP Task Center is set up.

