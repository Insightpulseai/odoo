<!-- loio7b0898e60c434895ae596832529d29d9 -->

# How to Tackle Connection Issues

Check the connection status of your communication system and tackle any existing issues.



<a name="loio7b0898e60c434895ae596832529d29d9__prereq_u4p_lc5_ytb"/>

## Prerequisites

Your user must have a role collection assigned that includes one of the following role templates:

-   `AFC_MonitorSystemsApp`

-   `AFC_SystemAdmin`


For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

The connection status is checked regularly. However, the frequency depends on the status that was set during the last check. The status is checked as follows:

**Connection Status Checks**


<table>
<tr>
<th valign="top">

Status During Last Check

</th>
<th valign="top">

Time Period After Status Was Set

</th>
<th valign="top">

Check Frequency

</th>
</tr>
<tr>
<td valign="top">

*OK*

</td>
<td valign="top">

Always

</td>
<td valign="top">

Every three hours

</td>
</tr>
<tr>
<td valign="top" rowspan="3">

*Error*

</td>
<td valign="top">

First 24 hours

</td>
<td valign="top">

Every 15 minutes

</td>
</tr>
<tr>
<td valign="top">

Days 1 to 30

</td>
<td valign="top">

Decreasing frequency between every hour and every 12 hours

</td>
</tr>
<tr>
<td valign="top">

After 30 Days

</td>
<td valign="top">

Every 24 hours

</td>
</tr>
</table>

> ### Note:  
> Connection issues can also be detected outside any scheduled checks, for example, when a user tries to schedule a task in the corresponding communication system. If an issue is detected this way, but the connection status is *OK* based on the last connection check, an additional connection check is scheduled to happen within the next 15 minutes. You can then find the results in the *Monitor Communication Systems* app.
> 
> The following graphic illustrates this process:
> 
> ![Graphic depicting the process leading to an additional connection check: First, a regular check is successful and set the connection status to OK. Then, a user tries to schedule a job in the same communication system. The scheduling fails due to connection issues. Accordingly, an additional connection check is planned to start within the next 15 minutes. If this check is successful, the connection status stays in status OK. If the check fails, the connection status for this system is set to Error.](images/Image_Extraordinary_Connection_Check_f12b958.png)

> ### Remember:  
> If the connection check doesn't show any successful result for three hours, the following processes are deactivated until the connection check is successful again:
> 
> -   Synchronization of master data
> 
> -   Scheduling of *Job* tasks
> 
> 
> In this case, the *Synchronization* tile and the *Scheduling* tile show status *Paused*.

Connection issues can originate from different sources within the environment. The following components are possible sources of errors:

-   Destination Service

-   Connectivity Service

-   Cloud Connector

-   ABAP Back-End Connectivity




## Procedure

1.  Open the *Monitor Communication Systems* app.

2.  From the table, open the system details of a communication system.

3.  In the *Status* section, check the *Connection Check* tile for more details:


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
    
    *Status*
    
    </td>
    <td valign="top">
    
    Shows the status of the connection. The status you see was set after the last connection check. The following statuses are possible:

    -   *OK*

    -   *Error*



    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Last Checked On*
    
    </td>
    <td valign="top">
    
    Shows the date and time of the last attempt to perform a connection check, independently of whether the check was successful or not.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Status Changed On*
    
    </td>
    <td valign="top">
    
    Shows the date and time of when the current status was set.
    
    </td>
    </tr>
    </table>
    
4.  If issues exist, performing a new connection check may already resolve the issues. You can start a new connection check manually by choosing *Check Connection* in the *Connection Check* tile.

    1.  If this check is successful, no further action is required.

    2.  If the check still fails, see the error message for more details and check whether your communication system is running as expected.

        As soon as the issues are fixed, you can start a new connection check.





<a name="loio7b0898e60c434895ae596832529d29d9__result_yrf_dd5_ytb"/>

## Results

You have now checked the connection status of your communication system and tackled any issues.

