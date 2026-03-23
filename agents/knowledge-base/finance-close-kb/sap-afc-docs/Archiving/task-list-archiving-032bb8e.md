<!-- loio032bb8ec94fe4e8a9ff21c156d965060 -->

# Task List Archiving

Understand how archiving and restoring in SAP Advanced Financial Closing works.

In SAP Advanced Financial Closing, generated task lists are archived automatically after a specific **time of inactivity**, independently of their status. The time after which a task list is archived depends on the closing type and on the value set for the *Is Production Task List* indicator. You define this time in the *Manage General Settings* app. The **highest values possible** - which are also the default values delivered by SAP - are defined as follows:




<table>
<tr>
<th valign="top">

Closing Type

</th>
<th valign="top">

Production Task Lists

</th>
<th valign="top">

Non-Production Task Lists

</th>
</tr>
<tr>
<td valign="top">

Month-End Closing

</td>
<td valign="top">

Six months

</td>
<td valign="top">

Three months

</td>
</tr>
<tr>
<td valign="top">

Quarter-End Closing

</td>
<td valign="top">

Nine months

</td>
<td valign="top">

Three months

</td>
</tr>
<tr>
<td valign="top">

Year-End Closing

</td>
<td valign="top">

18 months

</td>
<td valign="top">

Three months

</td>
</tr>
<tr>
<td valign="top">

Special-End Closing

</td>
<td valign="top">

Six months

</td>
<td valign="top">

Three months

</td>
</tr>
</table>

> ### Note:  
> The reference date for this time is either the date when the task list or any of its tasks was last updated or the date when the task list was last restored from the archive.
> 
> Task lists with status *Obsolete* are archived after one month, independently of the *Is Production Task List* indicator.
> 
> For more information about how to **define the archiving times** for task lists, see [How to Manage General Settings](../Business-Configuration/how-to-manage-general-settings-a4be7f7.md).

When a task list is archived, it no longer appears in any of the SAP Advanced Financial Closing apps, except for the *Manage Archived Closing Task Lists* app. In this app, you restore task lists from the archive as described below.

-   **[Manage Archived Closing Task Lists](manage-archived-closing-task-lists-9d9c629.md "You use the Manage Archived
                                                  Closing Task Lists
		app to display and restore archived task lists.")**  
You use the *Manage Archived Closing Task Lists* app to display and restore archived task lists.

<a name="task_mx3_j2r_gxb"/>

<!-- task\_mx3\_j2r\_gxb -->

## How to Restore Task Lists from the Archive

Restore archived task lists.



<a name="task_mx3_j2r_gxb__prereq_lg1_m2r_gxb"/>

## Prerequisites

Your user must have a role collection assigned that includes the role template `AFC_Archiving`.

For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

> ### Note:  
> If your user has the role template `AFC_Archiving_Display` assigned instead, you can see which task lists are archived, but you can't restore them.



<a name="task_mx3_j2r_gxb__context_qqv_l2r_gxb"/>

## Context

Restoring a task list from the archive makes it visible in other apps again. This allows you and other users to continue working on the task list and make changes that are allowed for task lists based on the current task list status.



<a name="task_mx3_j2r_gxb__steps_w5f_m2r_gxb"/>

## Procedure

1.  Open the *Manage Archived Closing Task Lists* app.

2.  In the *Archived Task Lists* table, search for the task list you want to restore.

3.  Select the task list and choose *Restore* in the table toolbar.




<a name="task_mx3_j2r_gxb__result_zyk_m2r_gxb"/>

## Results

The task list is restored from the archive and disappears from the list in the *Manage Archived Closing Task Lists* app.

> ### Note:  
> There may be a small delay until the restored task list is visible in other apps again.



<a name="task_mx3_j2r_gxb__postreq_jsp_m2r_gxb"/>

## Next Steps

You can now make changes to the task list or process tasks it contains.

> ### Note:  
> Restored task lists are archived automatically again after the default time defined for archiving.

**Related Information**  


[Allowed Attribute Changes Depending on Task List Status](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/21e491bf621d499fbeef037c2ee55742.html "See which attributes you can change in which app depending on the task list status.") :arrow_upper_right:

