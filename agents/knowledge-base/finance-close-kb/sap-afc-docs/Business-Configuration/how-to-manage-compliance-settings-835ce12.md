<!-- loio835ce12f7d4f4e8cab5df36537aea3c1 -->

# How to Manage Compliance Settings

The compliance settings apply to all apps that are part of SAP Advanced Financial Closing.



<a name="loio835ce12f7d4f4e8cab5df36537aea3c1__prereq_bxw_m3y_rjb"/>

## Prerequisites

Your user must have a role collection assigned that includes the role template `AFC_Compliance`.

For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

The following settings are available:

**Compliance Settings**


<table>
<tr>
<th valign="top">

Field

</th>
<th valign="top">

Effect

</th>
</tr>
<tr>
<td valign="top">

*Anonymize Names in Emails*

</td>
<td valign="top">

Specify whether you want real names to be removed from emails sent by the notification service of SAP Advanced Financial Closing. The default value is `No`.

</td>
</tr>
<tr>
<td valign="top">

*Anonymize Completed Task Lists After*

</td>
<td valign="top">

Define a number of months as the time offset after which user names are removed from completed task lists. The default value is `18` months.

> ### Note:  
> If you enter `0`, no anonymization is applied.
> 
> To enable anonymization, the minimum value is `6` months.



</td>
</tr>
<tr>
<td valign="top">

*Notify User Before Task Is Due*

</td>
<td valign="top">

To help ensure that tasks are completed before their scheduled end date, you can arrange for email and SAP Fiori notifications to be sent to the processing user or user responsible. Define how many minutes before a task is due users are reminded about the task. The minimum value is `10` minutes.

> ### Note:  
> To enable email notifications for a task, an email notification configuration including the scenario *Planned End Time of Task Approaching* must be assigned.



</td>
</tr>
<tr>
<td valign="top">

*Enforce SOX Requirements*

</td>
<td valign="top">

Determine whether the Sarbanes-Oxley Act \(SOX\) compliance applies. The default value is `Yes`. If the selection is set to *Yes*, the following rules apply:

-   User responsible and processing user of a task or folder must not be the same.

-   Responsible user group and processing user group of a task or folder must not be the same.

-   If a user group contains only one user and the group is assigned as the responsible user group or processing user group, the user of the group must not be the same user as the one maintained for the other role.

    This rule is checked only during the consistency check.


> ### Note:  
> If you deactivate this option, no checks for compliance with the SOX requirements will be run anymore. If you activate this option again, only objects created after activating this setting will be checked for SOX requirements. To ensure SOX compliance of existing task list templates, you need to run a consistency check. Task lists that were generated before SOX compliance was required might still not fulfill the SOX requirements. However, during task approval, a check ensures that the approving user is not the same as the processing user.
> 
> For more information about the consistency check, see [How to Perform Checks on Templates](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/bd90b43614b841f48796e068fb1fcb6c.html "Check whether your templates fulfill all requirements.") :arrow_upper_right:.



</td>
</tr>
</table>



## Procedure

1.  Go to the *Manage Compliance Settings* app.

2.  Choose *Edit*.

3.  Make your settings and save the changes.




<a name="loio835ce12f7d4f4e8cab5df36537aea3c1__result_ofp_5nt_3mb"/>

## Results

The compliance settings for your SAP Advanced Financial Closing have been updated.

