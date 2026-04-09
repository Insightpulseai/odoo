<!-- loiodc592124d31a4f72bb354cc003629bcf -->

# Supported Use Cases

Overview of the SAP Advanced Financial Closing use cases supported by SAP Task Center.

The following use cases of SAP Advanced Financial Closing are supported by SAP Task Center:


<table>
<tr>
<th valign="top">

Use Case

</th>
<th valign="top">

Release Date

</th>
</tr>
<tr>
<td valign="top">

Task Approval

</td>
<td valign="top">

December 9, 2023

</td>
</tr>
<tr>
<td valign="top">

Task Rejection

</td>
<td valign="top">

December 9, 2023

</td>
</tr>
</table>

> ### Note:  
> To use this capability, you need to set up the SAP Task Center integration for SAP Advanced Financial Closing as described on the following pages.



<a name="loiodc592124d31a4f72bb354cc003629bcf__section_m4m_wmd_nzb"/>

## Restrictions

The following aspects have restrictions when SAP Task Center is being used for the SAP Advanced Financial Closing use cases:



### Initial Synchronization with SAP Task Center

When you first set up the SAP Task Center for SAP Advanced Financial Closing, a synchronization ensures that tasks are displayed in SAP Task Center for the relevant users. This synchronization, however, covers only the last three months up to the day of this initial synchronization.



### User Assignment on Task

Only users assigned through direct assignment - individually or as part of a user group - see tasks they're responsible for in SAP Task Center. An assignment on a higher hierarchy level isn't sufficient.



### User Group Assignments

If you assign user groups to tasks, be aware that changes in the user group may not be reflected in SAP Task Center simultaneously. The following options exist:


<table>
<tr>
<th valign="top">

User Group Management Option

</th>
<th valign="top">

Restrictions

</th>
</tr>
<tr>
<td valign="top">

User groups are managed in SAP Advanced Financial Closing

</td>
<td valign="top">

If changes to user groups - that is, adding or removing users to or from the group - are made **after a task has been synchronized** to SAP Task Center, the group changes aren't reflected in the task in SAP Task Center.

This means that users who have been removed from a user group may still see a task in SAP Task Center even though they're no longer part of the user group. Similarly, users who have been added to a user group might not see a task in SAP Task Center even though they're now part of the group responsible for the task.

</td>
</tr>
<tr>
<td valign="top">

User groups are managed using SAP Cloud Identity Services - Identity Authentication

</td>
<td valign="top">

No restrictions apply. User group changes are always reflected in SAP Task Center.

</td>
</tr>
</table>



### Substitute Assignments

Users assigned as substitutes in SAP Advanced Financial Closing don't see the tasks of users they're substituting for in SAP Task Center. If you want to approve or reject tasks as a substitute, you need to do so directly in SAP Advanced Financial Closing.

