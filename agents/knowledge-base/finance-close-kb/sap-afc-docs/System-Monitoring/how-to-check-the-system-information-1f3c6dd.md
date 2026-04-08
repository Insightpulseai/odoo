<!-- loio1f3c6ddae438455f82ae2ec8191c35c8 -->

# How to Check the System Information

Check that the system information available is correct.



<a name="loio1f3c6ddae438455f82ae2ec8191c35c8__prereq_htj_xfh_fvb"/>

## Prerequisites

Your user must have a role collection assigned that includes one of the following role templates:

-   `AFC_MonitorSystemsApp`

-   `AFC_SystemAdmin`

-   `AFC_MonitorSystemsApp_Display`


For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

For systems that have an SAP Fiori launchpad, you can easily check whether the system information provided in the *Specify Communication Systems* app is correct. The check verifies that the UI domain, UI endpoint, and possibly UI parameters are correct and that they lead to the correct URL.

Additionally, you can check whether the Internet Transaction Server \(ITS\) settings for your **on-premise systems** are correct.



## Procedure

**Checking the UI Settings**

1.  Open the *Monitor Communication Systems* app.

2.  In the table listing all communication systems, select the communication system you want to check.

3.  In the table toolbar, choose *Check UI Settings*.

    The SAP Advanced Financial Closing application now uses the SAP Fiori launchpad information provided for the communication system in the *Specify Communication Systems* app and tries to call up the corresponding SAP Fiori launchpad.

    > ### Tip:  
    > You also have this option available in the communication system details in the *SAP Fiori Launchpad* section.

    1.  If the system successfully calls up the relevant SAP Fiori launchpad, no further action with regard to the system information is required.

    2.  If the system isn't able to call up the relevant SAP Fiori launchpad, check the system information and fix any issues that exist.

        > ### Note:  
        > Fixing issues with the system information may require you to have additional authorizations or to contact a system administrator who has the authorization required.



**Checking the ITS Settings** \(if applicable\)

4.  Open the *Monitor Communication Systems* app.

5.  In the table listing all communication systems, select the communication system you want to check.

6.  In the table toolbar, choose *Check ITS Settings*.

    > ### Tip:  
    > You also have this option available in the communication system details in the *SAP Internet Transaction Server* section.

    1.  If the check is successful, no further action with regard to the system information is required.

    2.  If the check isn't successful or doesn't show the expected results, check the system information and fix any issues that exist.

        > ### Note:  
        > The ITS settings information shown in SAP Advanced Financial Closing is read-only. If you need to make any adjustment to the ITS settings, make them in the corresponding communication system as described in the *SAP Advanced Financial Closing Local Settings Guide* under [How to Set Up ITS Navigation for Use with a Proxy Server](https://help.sap.com/viewer/a32675ceb29149fd9be78a66704da190/SHIP/en-US/f98438f63cf745dabf78cc33a32fbc1e.html "Set up ITS navigation if you use a proxy server.") :arrow_upper_right:.
        > 
        > Fixing issues with the system information may require you to have additional authorizations or to contact a system administrator who has the authorization required.





<a name="loio1f3c6ddae438455f82ae2ec8191c35c8__result_h4v_vfh_fvb"/>

## Results

You have now checked the system information available for a specific communication system.

