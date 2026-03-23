<!-- loio57375b87280a4ae8bfe2f622e2c2cbf4 -->

# Logging

Depending on what type of information you're looking for, go to one of the following apps.



<a name="loio57375b87280a4ae8bfe2f622e2c2cbf4__section_bzs_cbs_kjb"/>

## Change Log

The *Change Log* app shows you as a business user a change history of closing tasks, task lists, and templates.

You can see what was changed or deleted, by whom, and when. You can filter by *Type of Change* \(*Delete*, *Insert*, or *Change*\). And you can filter for changes made to a particular template, task list, or closing task or by a particular user.

For more information about using this app, see [Change Log](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/e08df37697ed4d8c8b3e4826c203dc6e.html "") :arrow_upper_right:.



### Change Logs for Configuration Objects

In addition to the changes logged in the *Change Log* app, information about changes to configuration objects is logged. To see these change logs, go to the corresponding configuration app and choose *Change Log* on either the list report page of the app or the object page of a specific object.

Change logs are available for the following apps:

> ### Note:  
> Any action that falls into the category *Delete* is only visible in the change log on the list report page of the app, not on the object page of a specific object.


<table>
<tr>
<th valign="top">

App

</th>
<th valign="top">

Logged Changes

</th>
</tr>
<tr>
<td valign="top">

*Manage Users*

</td>
<td valign="top">

-   User-specific changes, such as changes to a field belonging to a specific user

-   Upload and deletion of users




</td>
</tr>
<tr>
<td valign="top">

*Manage User Role Assignments*

</td>
<td valign="top">

-   Assignment-specific changes, such as changes to a field belonging to a specific user or role

-   Assignment actions




</td>
</tr>
<tr>
<td valign="top">

Configuration

-   *Manage Authorization Groups*

-   *Manage Country/Region Groups \(Deprecated\)*

-   *Manage Email Notification Configurations*

-   *Manage User Groups*

-   *Manage User Roles*




</td>
<td valign="top">

-   Object-specific changes, such as changes to a field belonging to a specific group or role

-   Deletion of an object




</td>
</tr>
</table>



<a name="loio57375b87280a4ae8bfe2f622e2c2cbf4__section_sjl_f2d_mjb"/>

## Monitor Business Logs

The *Monitor Business Logs* app shows you as an administrator logs of possible technical errors occurring in business-relevant activities. You can review the logs, for example, in the case of issues with the connection to a back-end system, with scheduling, or with status requests.

The following events are logged in the *Monitor Business Logs* app:

> ### Note:  
> Business logs are automatically deleted after 30 days.

****


<table>
<tr>
<th valign="top">

Logging Categories

</th>
<th valign="top">

What Is Being Logged?

</th>
</tr>
<tr>
<td valign="top">

Business configuration synchronization

</td>
<td valign="top">

-   Success, warning, and error messages during synchronization

-   Synchronized entities




</td>
</tr>
<tr>
<td valign="top">

Gateway feature synchronization

</td>
<td valign="top">

-   Missing authorizations of technical communication user

-   Timeout during system communication

-   Communication system not supported




</td>
</tr>
<tr>
<td valign="top">

Master data synchronization

</td>
<td valign="top">

-   Success, warning, and error messages during synchronization

-   Synchronized entities




</td>
</tr>
<tr>
<td valign="top">

Related to communication system

</td>
<td valign="top">

-   Errors during system communication, for example, missing destination




</td>
</tr>
<tr>
<td valign="top">

Related to task processing

</td>
<td valign="top">

-   Scheduling events

-   Success, warning, and error messages about job results




</td>
</tr>
<tr>
<td valign="top">

Related to task list templates and task lists

</td>
<td valign="top">

-   Deletion of task list templates and task lists
-   Consistency status changes of task list templates



</td>
</tr>
</table>

> ### Note:  
> Your user needs the correct role assignment as stated under [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

