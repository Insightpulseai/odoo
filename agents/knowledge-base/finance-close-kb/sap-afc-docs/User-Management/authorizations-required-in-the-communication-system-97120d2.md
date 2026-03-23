<!-- loio97120d2d25344f8ea9c576fc3a05ea69 -->

# Authorizations Required in the Communication System

Find more information about authorizations users need to have in the communication system.

For some actions, users need authorizations in the connected communication system in addition to those they have in SAP Advanced Financial Closing. You can find information about which authorizations are needed and how to grant them below. System administrators need to grant these authorizations to users performing the specific actions in the affected communication systems.



<a name="loio97120d2d25344f8ea9c576fc3a05ea69__section_p1j_zg2_32c"/>

## SAP S/4HANA Cloud Public Edition

You can grant authorizations in communication systems of type SAP S/4HANA Cloud Public Edition in two ways, using a business catalog or using an IAM app. For more information about how to assign a business catalog or IAM app, see [How to Maintain Business Roles](https://help.sap.com/viewer/7a732dca39e2412cb8661b769277bcbb/SHIP/en-US/eb0f7719da404f1ca48f28a4cba06f35.html "Use business catalogs and IAM apps to grant authorizations.") :arrow_upper_right:.

****


<table>
<tr>
<th valign="top" rowspan="2">

Action

</th>
<th valign="top" align="center" colspan="2">

Authorization Required

</th>
</tr>
<tr>
<th valign="top" align="center">

Business Catalog

</th>
<th valign="top" align="center">

IAM App

</th>
</tr>
<tr>
<td valign="top">

Scheduling of Tasks

</td>
<td valign="top">

`SAP_FIN_BC_AFC_APJ_PROC_PC` \(Advanced Financial Closing - Job Processor\)

</td>
<td valign="top">

`FCCX_APJ_PROCESSOR_TRAN` \(Schedule jobs for advanced financial closing tasks\)

</td>
</tr>
<tr>
<td valign="top">

Display Task Models in SAP Advanced Financial Closing

</td>
<td valign="top">

`SAP_FIN_BC_AFC_TMM_DSP_PC` \(SAP Advanced Financial Closing - Display Task Models\)

</td>
<td valign="top">

`FCCX_TMM_03_TRAN` \(Read authorization for task model management in SAP Advanced Financial Closing\)

</td>
</tr>
<tr>
<td valign="top">

Launchpad Tile in SAP S/4HANA Cloud Public Edition for Direct Navigation to SAP Advanced Financial Closing

</td>
<td valign="top">

`SAP_FIN_BC_AFC_APPS_PC` \(Finance - Manage Advanced Financial Closing\)

</td>
<td valign="top">

`U0233_TRAN` \(Manage Advanced Financial Closing\)

</td>
</tr>
</table>

**Parent topic:**[User Management](user-management-ae7fa30.md "Understand how you can manage users and their authorizations in SAP Advanced Financial Closing.")

**Next:**[User Access Management](user-access-management-d974847.md "You can control and grant access to task list templates, task lists, and tasks in SAP Advanced Financial Closing. By default, users don't have access to these objects.")

