<!-- loiob92a2411e4164270964903c502e22340 -->

# Static Roles for SAP Advanced Financial Closing

Static roles enable users to see the affected apps on their SAP Fiori launchpad.



<a name="loiob92a2411e4164270964903c502e22340__section_y4b_2xk_21c"/>

## Context

Static role templates are assigned to users to grant them access to apps that are part of SAP Advanced Financial Closing. In the end, these role templates allow the corresponding app tiles to be shown on a user's launchpad.



## Available Role Templates

> ### Note:  
> Some role templates have a corresponding **display-only** role template, which grants access to the same app but with restricted authorizations. In general, the display-only role templates allow users to view and export information, but not to create, upload, edit, or delete any information.
> 
> For detailed information, see the corresponding columns in the following table.

**Role Templates**


<table>
<tr>
<th valign="top">

Role Template

</th>
<th valign="top">

Description

</th>
<th valign="top">

Tiles on SAP Fiori Launchpad

</th>
<th valign="top">

Display-Only Role Template

</th>
<th valign="top">

Description for Display-Only Role

</th>
</tr>
<tr>
<td valign="top">

`AFC_SystemAdmin` 

</td>
<td valign="top">

-   Maintains solution-specific settings, for example, a connection to financial communication systems

-   Monitors system statuses and tackles any issues with connected systems \(additionally, the role template `Business_Process_Specialist_BL_AccessAll` is needed\)

-   Maintains and deletes users

-   Adapts the UI of apps for customer-specific use \(additionally, the role template `FlexKeyUser` is needed\).

    For more information about UI adaptation, see [Adapting the UI](https://help.sap.com/docs/BTP/3d99fdeadde04524bdd33d35f1e13777/d868950a1e8c4b0f9b9453176939a19b.html?locale=en-US) in the SAP Fiori Launchpad documentation.

-   Creates public views \(additionally, the role template `FlexKeyUser` is needed\).

    For more information, see [How to Manage Views](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/2fee7b5a83294d748953a9db5cc96326.html "Save, manage, and share views.") :arrow_upper_right:.


**App Details:**

-   [Manage Users](../Business-Configuration/manage-users-85bfe2f.md)
-   [Specify Communication Systems](../Connectivity/specify-communication-systems-7e2136a.md)
-   [Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md)



</td>
<td valign="top">

System administration:

-   *Manage Users*
-   *Specify Communication Systems*
-   *Monitor Communication Systems*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_SpecifySystemsApp` 

</td>
<td valign="top">

Maintains connections to financial communication systems

**App Details:**

[Specify Communication Systems](../Connectivity/specify-communication-systems-7e2136a.md)

</td>
<td valign="top">

-   *Specify Communication Systems*



</td>
<td valign="top">

`AFC_SpecifySystemsApp_Display`

</td>
<td valign="top">

-   Views and exports system information

-   Views and exports in-app change logs

-   Checks the connection of communication systems

-   **Cannot** maintain or edit communication systems

-   **Cannot** delete the connection to communication systems




</td>
</tr>
<tr>
<td valign="top">

`AFC_MonitorSystemsApp` 

</td>
<td valign="top">

-   Monitors system statuses

-   Tackles issues with connected systems

-   Synchronizes communication systems


To be able to view synchronization logs, a user additionally requires role template `Business_Process_Specialist_BL_AccessAll`.

**App Details:**

[Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md)

</td>
<td valign="top">

-   *Monitor Communication Systems*



</td>
<td valign="top">

`AFC_MonitorSystemsApp_Display`

</td>
<td valign="top">

-   Views and exports system information

-   Checks the connection of communication systems

-   **Cannot** synchronize communication systems




</td>
</tr>
<tr>
<td valign="top">

`AFC_Migration` 

</td>
<td valign="top">

Migrates data if a migration from SAP Advanced Financial Closing as part of SAP S/4HANA Cloud Public Edition to the SAP BTP solution takes place.

**App Details:**

-   [Migrate Configuration Data \(read-only\)](../Migration-from-Advanced-Financial-Closing-as-Part-of-SAP-S/4HANA-Cloud-Optional/migrate-configuration-data-read-o-643f4e8.md)
-   [Migrate Closing Task Lists \(read-only\)](../Migration-from-Advanced-Financial-Closing-as-Part-of-SAP-S/4HANA-Cloud-Optional/migrate-closing-task-lists-read-o-45712c6.md)



</td>
<td valign="top">

-   *Migrate Configuration Data \(read-only\)*
-   *Migrate Closing Task Lists \(read-only\)*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_Compliance` 

</td>
<td valign="top">

Maintains general compliance settings

**App Details:**

[Manage Compliance Settings](../Business-Configuration/manage-compliance-settings-73412af.md)

</td>
<td valign="top">

-   *Manage Compliance Settings*



</td>
<td valign="top">

`AFC_Compliance_Display`

</td>
<td valign="top">

-   Views compliance settings

-   Views and exports in-app change logs

-   **Cannot** change compliance settings




</td>
</tr>
<tr>
<td valign="top">

`AFC_UserAdmin` 

</td>
<td valign="top">

-   Maintains users and the assignments between users and roles.

-   Maintains user groups


**App Details:**

-   [Manage Users](../Business-Configuration/manage-users-85bfe2f.md)
-   [Manage User Role Assignments](../Business-Configuration/manage-user-role-assignments-c606666.md)
-   [Manage User Groups](../Business-Configuration/manage-user-groups-3e8208b.md)



</td>
<td valign="top">

-   *Manage Users*
-   *Manage User Role Assignments*
-   *Manage User Groups* \(Configuration\)



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_API_Access` 

</td>
<td valign="top">

Uses the UI to access API information and documentation

</td>
<td valign="top">

*Public API*

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_Config` 

</td>
<td valign="top">

Maintains application-specific data, for example, configuration settings, or master data

**App Details:**

-   [Manage Authorization Groups](../Business-Configuration/manage-authorization-groups-0ea3430.md)
-   [Manage Country/Region Groups \(Deprecated\)](../Business-Configuration/manage-country-region-groups-deprecated-e130df4.md)
-   [Manage Email Notification Configurations](../Business-Configuration/manage-email-notification-configurations-6f4c0b4.md)
-   [Manage User Groups](../Business-Configuration/manage-user-groups-3e8208b.md)
-   [Manage User Roles](../Business-Configuration/manage-user-roles-a6e1ae0.md)
-   [Manage Status Change Settings](../Business-Configuration/manage-status-change-settings-2b788b3.md)



</td>
<td valign="top">

-   *Manage Authorization Groups* \(Configuration\)
-   *Manage Country/Region Groups \(Deprecated\)* \(Configuration\)
-   *Manage Email Notification Configurations* \(Configuration\)
-   *Manage User Groups* \(Configuration\)
-   *Manage User Roles* \(Configuration\)
-   *Manage Status Change Settings*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_Settings` 

</td>
<td valign="top">

Maintains application-specific settings, such as notifications and country/region groups

**App Details:**

-   [Manage Country/Region Groups \(Deprecated\)](../Business-Configuration/manage-country-region-groups-deprecated-e130df4.md)
-   [Manage Email Notification Configurations](../Business-Configuration/manage-email-notification-configurations-6f4c0b4.md)



</td>
<td valign="top">

-   *Manage Country/Region Groups \(Deprecated\)* \(Configuration\)
-   *Manage Email Notification Configurations* \(Configuration\)



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_GeneralSettings` 

</td>
<td valign="top">

Maintains general settings, such as archiving settings, applying to objects in SAP Advanced Financial Closing.

**App Details:**

[Manage General Settings](../Business-Configuration/manage-general-settings-661b757.md)

</td>
<td valign="top">

*Manage General Settings*

</td>
<td valign="top">

`AFC_GeneralSettings_Display`

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_StatusChangeConstraintApp` 

</td>
<td valign="top">

Maintains settings to define whether comments are required for specific status changes.

**App Details:**

[Manage Status Change Settings](../Business-Configuration/manage-status-change-settings-2b788b3.md)

</td>
<td valign="top">

*Manage Status Change Settings*

</td>
<td valign="top">

`AFC_StatusChangeConstraintApp_Display`

</td>
<td valign="top">

Views status change settings

</td>
</tr>
<tr>
<td valign="top">

`AFC_UserRoles` 

</td>
<td valign="top">

Maintains user roles and authorization groups

**App Details:**

-   [Manage User Roles](../Business-Configuration/manage-user-roles-a6e1ae0.md)
-   [Manage Authorization Groups](../Business-Configuration/manage-authorization-groups-0ea3430.md)



</td>
<td valign="top">

-   *Manage User Roles* \(Configuration\)
-   *Manage Authorization Groups* \(Configuration\)



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_AuthGroupsApp` 

</td>
<td valign="top">

Maintains authorization groups

**App Details:**

[Manage Authorization Groups](../Business-Configuration/manage-authorization-groups-0ea3430.md)

</td>
<td valign="top">

-   *Manage Authorization Groups* \(Configuration\)



</td>
<td valign="top">

`AFC_AuthGroupsApp_Display`

</td>
<td valign="top">

-   Views and exports authorization group information

-   Views and exports in-app change logs

-   **Cannot** create, edit, or delete authorization groups




</td>
</tr>
<tr>
<td valign="top">

`AFC_CountryGroupsApp` 

</td>
<td valign="top">

Maintains country/region groups

**App Details:**

[Manage Country/Region Groups \(Deprecated\)](../Business-Configuration/manage-country-region-groups-deprecated-e130df4.md)

</td>
<td valign="top">

-   *Manage Country/Region Groups \(Deprecated\)* \(Configuration\)



</td>
<td valign="top">

`AFC_CountryGroupsApp_Display`

</td>
<td valign="top">

-   Views and exports country/region group information

-   Views and exports in-app change logs

-   **Cannot** create, edit, or delete country/region groups




</td>
</tr>
<tr>
<td valign="top">

`AFC_CompanyCodeGroupsApp`

</td>
<td valign="top">

Maintains company code groups

**App Details:**

[Manage Company Code Groups](../Business-Configuration/manage-company-code-groups-90a2ae4.md)

</td>
<td valign="top">

-   *Manage Company Code Groups* \(Configuration\)



</td>
<td valign="top">

`AFC_CompanyCodeGroupsApp_Display`

</td>
<td valign="top">

-   Views and exports information about company code group assignments
-   Views and exports in-app change logs
-   **Cannot** create, edit, or delete company code group assignments



</td>
</tr>
<tr>
<td valign="top">

`AFC_NotificationsApp` 

</td>
<td valign="top">

Maintains email notification configurations

**App Details:**

[Manage Email Notification Configurations](../Business-Configuration/manage-email-notification-configurations-6f4c0b4.md)

</td>
<td valign="top">

-   *Manage Email Notification Configurations* \(Configuration\)



</td>
<td valign="top">

`AFC_NotificationsApp_Display`

</td>
<td valign="top">

-   Views and exports information about email notification configurations

-   Views and exports in-app change logs

-   **Cannot** create, edit, or delete email notification configurations




</td>
</tr>
<tr>
<td valign="top">

`AFC_UserGroupsApp` 

</td>
<td valign="top">

Maintains user groups

**App Details:**

[Manage User Groups](../Business-Configuration/manage-user-groups-3e8208b.md)

</td>
<td valign="top">

-   *Manage User Groups* \(Configuration\)



</td>
<td valign="top">

`AFC_UserGroupsApp_Display`

</td>
<td valign="top">

-   Views and exports user group information

-   Views and exports in-app change logs

-   **Cannot** upload, create, edit, or delete user groups

-   **Cannot** upload user-to-group assignments

-   **Cannot** download the template for user-to-group assignment creation




</td>
</tr>
<tr>
<td valign="top">

`AFC_UserRolesSingleApp` 

</td>
<td valign="top">

Maintains user roles

**App Details:**

[Manage User Roles](../Business-Configuration/manage-user-roles-a6e1ae0.md)

</td>
<td valign="top">

-   *Manage User Roles* \(Configuration\)



</td>
<td valign="top">

`AFC_UserRolesSingleApp_Display`

</td>
<td valign="top">

-   Views and exports user role information

-   Views and exports in-app change logs

-   **Cannot** create, edit, or delete user roles




</td>
</tr>
<tr>
<td valign="top">

`AFC_ManageUsersApp` 

</td>
<td valign="top">

Maintains and deletes users

**App Details:**

[Manage Users](../Business-Configuration/manage-users-85bfe2f.md)

</td>
<td valign="top">

-   *Manage Users*



</td>
<td valign="top">

`AFC_ManageUsersApp_Display`

</td>
<td valign="top">

-   Views and exports user information

-   Views and exports in-app change logs

-   **Cannot** upload, edit, or delete users

-   **Cannot** download the template for user creation




</td>
</tr>
<tr>
<td valign="top">

`AFC_UserManagement` 

</td>
<td valign="top">

Maintains assignments between user and roles

**App Details:**

[Manage User Role Assignments](../Business-Configuration/manage-user-role-assignments-c606666.md)

</td>
<td valign="top">

-   *Manage User Role Assignments*



</td>
<td valign="top">

`AFC_UserManagement_Display`

</td>
<td valign="top">

-   Views and exports user-to-role assignment information

-   Views and exports in-app change logs

-   **Cannot** upload, edit, or delete user-to-role assignments

-   **Cannot** download the template for user-to-role assignment creation




</td>
</tr>
<tr>
<td valign="top">

`AFC_Archiving`

</td>
<td valign="top">

Restores task lists from archive

**App Details:**

[Manage Archived Closing Task Lists](../Archiving/manage-archived-closing-task-lists-9d9c629.md)

</td>
<td valign="top">

-   *Manage Archived Closing Task Lists*



</td>
<td valign="top">

`AFC_Archiving_Display`

</td>
<td valign="top">

Views archived task lists

</td>
</tr>
<tr>
<td valign="top">

`AFC_Define` 

</td>
<td valign="top">

Maintains task list templates and task lists

**App Details:**

-   [Manage Closing Task Lists](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/c197c2fef140441dac407f5b4d7877f7.html "You use this app to model, plan, and start a workflow comprising all activities required to close your entities.") :arrow_upper_right:
-   [Change Log](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/e08df37697ed4d8c8b3e4826c203dc6e.html "") :arrow_upper_right:



</td>
<td valign="top">

-   *Manage Closing Task Lists*
-   *Change Log*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_TaskGroups`

</td>
<td valign="top">

Maintains task group templates

**App Details:**

-   [Manage Task Group Templates](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/cad9588f735949cf89d88f7d216130c7.html "") :arrow_upper_right:
-   [Change Log](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/e08df37697ed4d8c8b3e4826c203dc6e.html "") :arrow_upper_right:



</td>
<td valign="top">

-   *Manage Task Group Templates*
-   *Change Log*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_TaskModels_Manage`

</td>
<td valign="top">

Views task models, task model types, and job variants by communication system.

**App Details:**

[Manage Task Models](../Business-Configuration/manage-task-models-cfbdd1f.md)

</td>
<td valign="top">

*Manage Task Models*

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_Process` 

</td>
<td valign="top">

Processes task lists and tasks

**App Details:**

-   [Process Closing Tasks](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/ae51205499f549558eadd8a2c190d1b5.html "You use the Process Closing Tasks app to manually process, schedule, or automate your closing tasks.") :arrow_upper_right:
-   [Change Log](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/e08df37697ed4d8c8b3e4826c203dc6e.html "") :arrow_upper_right:



</td>
<td valign="top">

-   *Process Closing Tasks*
-   *Change Log*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_Approve` 

</td>
<td valign="top">

Approves tasks

**App Details:**

-   [Approve Closing Tasks](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/0080c46144184fd7941121527575f2cd.html "You use the Approve Closing Tasks app to check and approve critical closing tasks.") :arrow_upper_right:
-   [Change Log](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/e08df37697ed4d8c8b3e4826c203dc6e.html "") :arrow_upper_right:



</td>
<td valign="top">

-   *Approve Closing Tasks*
-   *Change Log*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_Reporting` 

</td>
<td valign="top">

Monitors overall progress of closing activities and tracks task completion

**App Details:**

-   [Financial Close Overview (Deprecated)](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/4f84841c40384a4dbb9d3841f3a0b5a3.html "This app enables you to access key information and KPIs to monitor the completion of closing tasks.") :arrow_upper_right:
-   [Closing Task Completion (Deprecated)](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/b83de37c24b34c14a6cae849b3161fab.html "This app enables you to analyze the status and the completion rate of active closing tasks as a summary.") :arrow_upper_right:



</td>
<td valign="top">

-   *Financial Close Overview \(Deprecated\)*
-   *Closing Task Completion \(Deprecated\)*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_ReportingTaskView`

</td>
<td valign="top">

Monitors overall progress of closing activities and tracks the financial close with focus on task overall status

**App Details:**

-   [Financial Close Overview - Task View](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/3da7158ea6674b70bf7ba3cbd83c8c25.html "You use the Financial Close Overview - Task View app to do your reporting based on the overall task statuses.") :arrow_upper_right:
-   [Closing Task Completion - Task View](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/92dd6f8e5e8e49ce831381fbb1d9908d.html "You use the Closing Task Completion - Task View app to do your detailed reporting based on the overall task statuses.") :arrow_upper_right:



</td>
<td valign="top">

-   *Financial Close Overview - Task View*
-   *Closing Task Completion - Task View*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_ReportingOrgUnitView`

</td>
<td valign="top">

Monitors overall progress of closing activities and tracks the financial close with focus on task execution statuses

**App Details:**

-   [Financial Close Overview - Organizational Unit View](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/22861d7f90764ac3b48d60cc96d9e55e.html "You use the Financial Close Overview - Organizational Unit View app to do your reporting based on the individual task execution statuses.") :arrow_upper_right:
-   [Closing Task Completion - Organizational Unit View](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/8c7230c7cbd7410ea8a26682afb4657e.html "You use the Closing Task Completion - Organizational Unit View app to do your detailed reporting based on the individual task execution statuses.") :arrow_upper_right:



</td>
<td valign="top">

-   *Financial Close Overview - Organizational Unit View*
-   *Closing Task Completion - Organizational Unit View*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`Business_Process_Specialist_BL_AccessAll` 

</td>
<td valign="top">

Reviews logs as an administrator

</td>
<td valign="top">

-   *Monitor Business Logs*



</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`AFC_KeyUser` 

</td>
<td valign="top">

-   Adapts the UI of apps for customer-specific use \(additionally, the role template `FlexKeyUser` is needed\).

    For more information about UI adaptation, see [Adapting the UI](https://help.sap.com/docs/BTP/3d99fdeadde04524bdd33d35f1e13777/d868950a1e8c4b0f9b9453176939a19b.html?locale=en-US) in the SAP Fiori Launchpad documentation.

    > ### Caution:  
    > With the *Adapt UI* function, you can customize the user interface behavior, but some of the available options may be restricted by the application. Additionally, be careful not to adjust the user interface in a way that will restrict functionality. Examples of adjustments that might restrict the functionality:
    > 
    > -   Visibility of view management
    > -   Visibility of sorting and filtering
    > -   Selection limit

-   Creates public views \(additionally, the role template `FlexKeyUser` is needed\).

    For more information, see [How to Manage Views](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/2fee7b5a83294d748953a9db5cc96326.html "Save, manage, and share views.") :arrow_upper_right:.




</td>
<td valign="top">

All apps in SAP Advanced Financial Closing

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

`FlexKeyUser` 

</td>
<td valign="top">

-   Adapts the UI of apps for customer-specific use \(additionally, either the role template `AFC_SystemAdmin` or the role template `AFC_KeyUser` is needed\).

    For more information about UI adaptation, see [Adapting the UI](https://help.sap.com/docs/BTP/3d99fdeadde04524bdd33d35f1e13777/d868950a1e8c4b0f9b9453176939a19b.html?locale=en-US) in the SAP Fiori Launchpad documentation.

    > ### Caution:  
    > With the *Adapt UI* function, you can customize the user interface behavior, but some of the available options may be restricted by the application. Additionally, be careful not to adjust the user interface in a way that will restrict functionality. Examples of adjustments that might restrict the functionality:
    > 
    > -   Visibility of view management
    > -   Visibility of sorting and filtering
    > -   Selection limit

-   Creates public views \(additionally, either the role template `AFC_SystemAdmin` or the role template `AFC_KeyUser` is needed\).

    For more information, see [How to Manage Views](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/2fee7b5a83294d748953a9db5cc96326.html "Save, manage, and share views.") :arrow_upper_right:.




</td>
<td valign="top">

All apps in SAP Advanced Financial Closing

</td>
<td valign="top">

 

</td>
<td valign="top">

 

</td>
</tr>
</table>



<a name="loiob92a2411e4164270964903c502e22340__section_w3j_2c3_5qb"/>

## Available Composite Role Templates


<table>
<tr>
<th valign="top">

Role Template

</th>
<th valign="top">

Included Role Templates

</th>
</tr>
<tr>
<td valign="top">

`AFC_Expert`

</td>
<td valign="top">

-   `AFC_Define`
-   `AFC_Config`
-   `AFC_TaskGroups`



</td>
</tr>
<tr>
<td valign="top">

`AFC_Manager`

</td>
<td valign="top">

-   `AFC_ReportingTaskView`
-   `AFC_ReportingOrgUnitView`
-   `AFC_Approve`
-   `AFC_UserManagement`



</td>
</tr>
</table>

