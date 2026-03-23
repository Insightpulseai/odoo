<!-- loiof30be05fb2d3419c838256dae727d5b2 -->

# How to Check the Overall System Status

Check the overall statuses of your connected communication systems.



<a name="loiof30be05fb2d3419c838256dae727d5b2__prereq_gnx_kzt_ytb"/>

## Prerequisites

Your user must have a role collection assigned that includes one of the following role templates:

-   `AFC_MonitorSystemsApp`

-   `AFC_SystemAdmin`


For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

You can easily get an overview of the overall system status. In the case of any errors, you can then tackle the related issues.



### Overall System Status

The following system statuses are possible:

**Overall System Status**


<table>
<tr>
<th valign="top">

System Status

</th>
<th valign="top">

Description

</th>
</tr>
<tr>
<td valign="top">

*OK*

</td>
<td valign="top">

No connection or synchronization issues were detected. No further action required.

</td>
</tr>
<tr>
<td valign="top">

*Warning*

</td>
<td valign="top">

Warnings for this system exist. Check the *Status Source* column and the system details for more information.

</td>
</tr>
<tr>
<td valign="top">

*Error*

</td>
<td valign="top">

One or more issues were detected. Check the *Status Source* column and the system details for more information. Tackle any issues and restart the check or synchronization run affected.

</td>
</tr>
</table>



## Procedure

1.  Open the *Monitor Communication Systems* app.

2.  In the table, check the system statuses of the connected communication systems.

    1.  If the status is set to *Error*, check the *Status Source* column to see where the error comes from.

    2.  Open the system details for more information and follow the relevant steps described in the following sections:

        -   [How to Tackle Connection Issues](how-to-tackle-connection-issues-7b0898e.md)

        -   [How to Tackle Synchronization Issues](how-to-tackle-synchronization-issues-ed8c4ec.md)






<a name="loiof30be05fb2d3419c838256dae727d5b2__result_vvl_x1p_g5b"/>

## Results

You have now checked the overall status of your communication systems.

