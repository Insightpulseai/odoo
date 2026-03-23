<!-- loio7b790c6bc43345d4a6496f7b500e65f6 -->

# How to Connect to a BlackLine System as a Communication System

Connect to SAP Accounting Automation by BlackLine to include BlackLine processes in your financial close in SAP Advanced Financial Closing.



<a name="loio7b790c6bc43345d4a6496f7b500e65f6__prereq_lrk_shn_sjb"/>

## Prerequisites

-   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_SpecifySystemsApp`


    For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   The destination in the SAP BTP cockpit has already been created as described under [How to Create the Destination in the SAP BTP Cockpit](how-to-create-the-destination-in-the-sap-btp-cockpit-9633df8.md).




<a name="loio7b790c6bc43345d4a6496f7b500e65f6__steps_bwt_shn_sjb"/>

## Procedure

1.  In SAP Advanced Financial Closing, go to the *Specify Communication Systems* app.

2.  Choose *Create* \> *Create BlackLine System* in the table toolbar.

    > ### Note:  
    > This communication system can't be added to task list templates as communication system folder. Instead, once the connection between SAP Advanced Financial Closing and BlackLine is set up as described below, processes in BlackLine are automatically available to be added as tasks in the task list template.

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
    </table>
    
    > ### Tip:  
    > You can check whether the connection with the communication system works as expected. Choose *Check Connection*. This will check whether the back-end connection works and whether the system communicates as expected.

4.  Save.

5.  Under *Notifications*, you can set up notifications about system errors. Follow the steps described under [How to Set Up Notifications About Communication System Errors](../System-Monitoring/how-to-set-up-notifications-about-communication-system-errors-835b2a2.md).


**Parent topic:**[SAP Accounting Automation by BlackLine](sap-accounting-automation-by-blackline-ce92690.md "Perform the following steps to connect SAP Advanced Financial Closing to SAP Accounting Automation by BlackLine.")

**Next:**[How to Create the Destination in the SAP BTP Cockpit](how-to-create-the-destination-in-the-sap-btp-cockpit-9633df8.md "Create a destination in your SAP BTP cockpit for an integration with SAP Accounting Automation by BlackLine.")

