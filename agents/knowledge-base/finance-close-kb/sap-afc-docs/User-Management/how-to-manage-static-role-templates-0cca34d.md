<!-- loio0cca34d98080443b8ce7294e9b4977b4 -->

# How to Manage Static Role Templates

Define and bundle static roles and assign them to users.



<a name="loio0cca34d98080443b8ce7294e9b4977b4__prereq_gq2_n3n_sjb"/>

## Prerequisites

1.  You've performed onboarding.

    For more information, see [Onboarding](../Onboarding/onboarding-1987953.md).

2.  You've established trust and federation with the UAA.

    For more information, see [Trust and Federation with Identity Providers](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/cb1bc8f1bd5c482e891063960d7acd78.html).




<a name="loio0cca34d98080443b8ce7294e9b4977b4__context_lxm_n3n_sjb"/>

## Context

As a prerequisite for assigning roles to IdP users or user groups, you also need to configure role collections. A role collection consists of one or more roles from one or more applications and can be used to bundle authorizations within and across applications.

For more information about how to create roles and how to bundle them in role collections using the SAP BTP cockpit, see [Building Roles and Role Collections for Applications](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/eaa6a26291914b348e875a00b6beb729.html).

> ### Caution:  
> Users to whom you assign a static role for system administration, configuration, user management, or compliance can read and change all data in the respective apps. For other apps, access must be granted before users can read and change data. For more information, see [User Access Management](user-access-management-d974847.md).



### What is the Purpose of Static Roles in SAP Advanced Financial Closing?

Static role templates are assigned to users to grant them access to apps that are part of SAP Advanced Financial Closing. In the end, these role templates allow the corresponding app tiles to be shown on a user's launchpad.



<a name="loio0cca34d98080443b8ce7294e9b4977b4__steps_uj3_43n_sjb"/>

## Procedure

1.  Familiarize yourself with the available role templates that are described under [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

2.  Additionally, decide whether you want to use the available composite role templates.


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
    
3.  Create role collections from the role templates provided by SAP Advanced Financial Closing. Follow the steps under [Maintain Role Collections](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/d5f1612d8230448bb6c02a7d9c8ac0d1.html).

    > ### Caution:  
    > To ensure a separation of concerns, you might want to avoid combining the role templates `AFC_Define` and `AFC_Process` into one role collection.

    > ### Note:  
    > When creating role collections, keep in mind that an app may link to objects in another app. For example, the *Closing Task Completion* app links to tasks in the *Process Closing Tasks* app. You can create a role collection that includes the role template `AFC_Reporting` but not the role template `AFC_Process`. However, users with this role collection won't be able to follow the link to the task details in the *Process Closing Tasks* app.

4.  Assign role collections to users. Follow the steps under [Mapping Role Collections in the Subaccount](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/9e1bf57130ef466e8017eab298b40e5e.html).

5.  Add roles to role collections. Follow the steps under [Add Roles to Role Collections on the Application Level](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/7596a0bdab4649ac8a6f6721dc72db19.html).


-   **[Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md "Static roles enable users to see the affected apps on their SAP Fiori
		launchpad.")**  
Static roles enable users to see the affected apps on their SAP Fiori launchpad.

**Parent topic:**[User Management](user-management-ae7fa30.md "Understand how you can manage users and their authorizations in SAP Advanced Financial Closing.")

**Previous:**[How to Manage Users](how-to-manage-users-c338b30.md "Upload new users to SAP Advanced Financial Closing and update certain user attributes.")

**Related Information**  


[User Access Management](user-access-management-d974847.md "You can control and grant access to task list templates, task lists, and tasks in SAP Advanced Financial Closing. By default, users don't have access to these objects.")

