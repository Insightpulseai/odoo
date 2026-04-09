<!-- loio9de0a5c2ec9241f2b3362c34cc3af7b9 -->

# How to Connect to an SAP Build Process Automation System as a Communication System

Connect to your SAP Build Process Automation system to include workflows from SAP Build Process Automation in your financial close in SAP Advanced Financial Closing.



<a name="loio9de0a5c2ec9241f2b3362c34cc3af7b9__prereq_lrk_shn_sjb"/>

## Prerequisites

-   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_SpecifySystemsApp`


    For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   The destination in the SAP BTP cockpit has already been created as described under [How to Create the Destination in the SAP BTP Cockpit](how-to-create-the-destination-in-the-sap-btp-cockpit-3ba6624.md).




<a name="loio9de0a5c2ec9241f2b3362c34cc3af7b9__steps_bwt_shn_sjb"/>

## Procedure

1.  In SAP Advanced Financial Closing, go to the *Specify Communication Systems* app.

2.  Choose *Create* \> *Create SAP Build Process Automation System* in the table toolbar.

    > ### Note:  
    > This communication system can't be added to task list templates as communication system folder. Instead, once the connection between SAP Advanced Financial Closing and SAP Build Process Automation is set up as described below, workflows in SAP Build Process Automation are automatically available to be added as tasks in the task list template.

3.  Enter the following information:


    <table>
    <tr>
    <th valign="top">

    Field
    
    </th>
    <th valign="top">

    Description
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    *Name*
    
    </td>
    <td valign="top">
    
    Enter a name for the communication system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Name of Destination Configuration*
    
    </td>
    <td valign="top">
    
    Enter the name of the destination configuration that was configured in the SAP BTP cockpit.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *System URL*
    
    </td>
    <td valign="top">
    
    Enter the UI URL of your SAP Build Process Automation application. The URL follows a specific pattern: `https://<subdomain>.<landscape>.build.cloud.sap`.

    > ### Example:  
    > The subdomain of your subaccount is **`example-company`**.
    > 
    > Your SAP Build Process Automation application is in the landscape **`EU10`**.
    > 
    > **Result:** Your UI URL is **`https://example-company.eu10.build.cloud.sap`**.


    
    </td>
    </tr>
    </table>
    
4.  Save.

5.  Verify that the system URL entered is correct by choosing the *Open SAP Build Process Automation* button in the *SAP Build Process Automation* section.

6.  Check whether the connection between SAP Advanced Financial Closing and SAP Build Process Automation works by choosing the *Check Connection* button in the header bar.

7.  **Optional:** Under *Notifications*, you can set up notifications about system errors. Follow the steps described under [How to Set Up Notifications About Communication System Errors](../System-Monitoring/how-to-set-up-notifications-about-communication-system-errors-835b2a2.md).




<a name="loio9de0a5c2ec9241f2b3362c34cc3af7b9__postreq_l3x_1js_bhc"/>

## Next Steps

To finalize the setup, return to the steps described under [How to Set Up the SAP Build Process Automation Integration for SAP Advanced Financial Closing](../Integration-Capabilities/how-to-set-up-the-sap-build-process-automation-integration-for-sap-advanced-financial-cl-0d8e37f.md).

**Parent topic:**[SAP Build Process Automation](sap-build-process-automation-7385663.md "Perform the following steps to connect SAP Advanced Financial Closing to your SAP Build Process Automation system.")

**Next:**[How to Create the Destination in the SAP BTP Cockpit](how-to-create-the-destination-in-the-sap-btp-cockpit-3ba6624.md "Create a destination for your SAP Build Process Automation system in your SAP BTP cockpit.")

