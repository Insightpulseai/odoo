<!-- loio835b2a2c0c6a4682b66bb6fb4228ad78 -->

# How to Set Up Notifications About Communication System Errors

Maintain settings for notifications about communication system errors.



<a name="loio835b2a2c0c6a4682b66bb6fb4228ad78__prereq_fqk_kh5_hwb"/>

## Prerequisites

-   You've established a connection between SAP Advanced Financial Closing and the communication system for which you want to set up notifications.

    For information about how to set up the connection, see [Connectivity](../Connectivity/connectivity-200deae.md).

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_SpecifySystemsApp`





## Context

To stay on top of any issues that may occur with the connection between your communication system and SAP Advanced Financial Closing, you can define who should receive notifications if issues are detected.

Notifications can be sent for the following cases:

-   Connection errors

-   Master data synchronization errors


> ### Note:  
> These notifications are generally available as SAP Fiori and email notifications. However, the delivery method also depends on the user-specific settings that are described under [User Actions Menu](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/4c7939aa18954b2f96d2dfeb73d3fcbd.html "Find information about the user actions menu.") :arrow_upper_right:.



## Procedure

1.  Open the *Specify Communication Systems* app.

2.  From the table, open the system details of the communication system you want to maintain notification settings for.

3.  Choose *Edit* in the header bar.

4.  Go to the *Notifications* section.

5.  Choose *Add* in the table toolbar.

6.  In the *Add Scenario* dialog, provide the following information:

    1.  *Scenario*:

        Select the scenario for which you want to maintain recipients. The following scenarios are available:


        <table>
        <tr>
        <th valign="top">

        Scenario
        
        </th>
        <th valign="top">

        Description
        
        </th>
        </tr>
        <tr>
        <td valign="top">
        
        *Connection Error*
        
        </td>
        <td valign="top">
        
        Users who are selected as recipients receive notifications for connection errors only.

        A notification for this error is sent within 20 minutes after an issue was detected.
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        *Master Data Synchronization Error*
        
        </td>
        <td valign="top">
        
        Users who are selected as recipients receive notifications for master data synchronization errors only.
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        *All Errors*
        
        </td>
        <td valign="top">
        
        Users who are selected as recipients receive notifications for all scenarios available.
        
        </td>
        </tr>
        </table>
        
    2.  *User Type*:

        Decide whether you want to assign a single user or a user group to this scenario.

    3.  *User to Notify* or *User Group to Notify* respectively:

        Enter the user or user group you want to define as notification recipients for this scenario.

        > ### Tip:  
        > You can either start typing the name and select the corresponding user or group from the list that appears, or use the value help available to search for the user or group.

    4.  To confirm, choose *Add*.


7.  If you ever want to update the user assignment for a scenario, select the scenario entry in the *Assigned Scenarios* table and choose *Change*.

8.  If you ever want to remove a scenario entry from the *Assigned Scenarios* table, select the entry and choose *Delete* in the table toolbar.

9.  To confirm your changes, choose *Save* in the footer.




<a name="loio835b2a2c0c6a4682b66bb6fb4228ad78__result_rdk_vp5_hwb"/>

## Results

Users who have been assigned to a scenario - either individually or as part of a group - will receive notifications for this communication system if the selected scenario occurs.



<a name="loio835b2a2c0c6a4682b66bb6fb4228ad78__postreq_x4s_fq5_hwb"/>

## Next Steps

If a scenario occurs and an issue needs to be tackled, you can find more information under [Monitor Communication Systems](monitor-communication-systems-a215069.md).

