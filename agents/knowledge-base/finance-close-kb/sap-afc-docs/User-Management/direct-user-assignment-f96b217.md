<!-- loiof96b217748304780966e86b8063dc41d -->

# Direct User Assignment

Grant access by directly assigning a user or user group to an object.



<a name="loiof96b217748304780966e86b8063dc41d__section_c1c_t5v_rrb"/>

## About This Access

Users who are maintained as **owners of a task list template** or who belong to an assigned owner group have write access to the specific object in the *Manage Closing Task Lists* app.

Users who are maintained as the **user responsible** for a **folder**, **task list**, or **task**, or who belong to a responsible user group always have write access to the respective object. They don't need to have a user role assigned in addition.

Users who are maintained as the **processing user** of a **task** or who belong to a processing user group always have access to the respective task. To be able to process the respective task, they don't need to have a user role assigned in addition.

> ### Note:  
> A substitute of an owner, of a user responsible, or of a processing user only inherits access to the objects to which the respective owner, user responsible, or processing user has been assigned individually and not as part of a user group.

Users who are maintained as **owners of a task group template** or who belong to an assigned owner group have write access to the specific object in the *Manage Task Group Templates* app.

> ### Note:  
> For task group templates that are assigned to a task list template, the user authorizations apply as described below for the *Task List Creation* scope and later, in the task list, as described for the *Task Processing* scope. The task group owner doesn't get any authorization in the task list template or task list.

Find out how to manage user groups under [How to Manage User Groups](how-to-manage-user-groups-45bb6c9.md).



<a name="loiof96b217748304780966e86b8063dc41d__section_x4f_lmd_w2c"/>

## Actions Allowed Based on Direct Assignment

****


<table>
<tr>
<th valign="top">

Scope Affected

</th>
<th valign="top">

Action

</th>
<th valign="top">

Owner / Owner Group \(Task List Template\)

</th>
<th valign="top">

Owner / Owner Group \(Task Group Template\)

</th>
<th valign="top">

User / User Group Responsible \(Task List Template / Task List\)

</th>
<th valign="top">

User / User Group Responsible \(Organizational Unit Folder\)

</th>
<th valign="top">

User / User Group Responsible \(Task\)

</th>
<th valign="top">

Processing User / User Group

</th>
<th valign="top">

Interested User / User Group \(Folder\)

</th>
<th valign="top">

Interested User / User Group \(Task\)

</th>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Read

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Create Task List Templates

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Copy Task List Templates

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Edit Task List Templates and Task Lists \(incl. creating, copying, and moving tasks\)

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Activate/Deactivate Tasks

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Delete Task List Templates and Task Lists with Status *Not Released* 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Generate Task Lists

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Change Task List Status

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Delete Task Lists

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Change User Assignments \(Quick Actions\)

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Check SOX Compliance

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task List Creation*

</td>
<td valign="top">

Check Compatibility

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Read

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Download Results

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Change Task Status

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Process

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Schedule

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Cancel Run

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Start Test Run

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Cancel Test Run

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Edit Attachments/Notes

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Change Planned Start

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Change Planned Duration

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Change Parameters

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Change User Assignments

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Approve

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Processing*

</td>
<td valign="top">

Reject

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Group Management*

</td>
<td valign="top">

Read

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Group Management*

</td>
<td valign="top">

Create

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Group Management*

</td>
<td valign="top">

Copy

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Group Management*

</td>
<td valign="top">

Edit

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Group Management*

</td>
<td valign="top">

Delete

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Task Group Management*

</td>
<td valign="top">

Change Log \(in *Change Log* app\)

</td>
<td valign="top">

 

</td>
<td valign="top">

`X`

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
</table>



<a name="loiof96b217748304780966e86b8063dc41d__section_ljb_rmc_qrb"/>

## How to Manage Access in This Scope

Find more information about how to manage direct access in the following document:

-   **[How to Grant Access by Direct Assignment](how-to-grant-access-by-direct-assignment-7ac9d63.md "Grant access by directly assigning a user to a task list template, task list, or
		task.")**  
Grant access by directly assigning a user to a task list template, task list, or task.

**Related Information**  


[Allowed Attribute Changes Depending on Task List Status](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/21e491bf621d499fbeef037c2ee55742.html "See which attributes you can change in which app depending on the task list status.") :arrow_upper_right:

