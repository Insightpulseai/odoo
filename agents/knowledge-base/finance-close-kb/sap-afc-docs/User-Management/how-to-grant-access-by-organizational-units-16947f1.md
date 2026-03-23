<!-- loio16947f19a23d41ba832e1fa1314aca43 -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# How to Grant Access by Organizational Units

Grant access to specific organizational units by assigning one or more authorizations available within this scope.



<a name="loio16947f19a23d41ba832e1fa1314aca43__prereq_snv_r4l_qrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_Config`

    -   `AFC_UserRoles`

    -   `AFC_UserRolesSingleApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You've familiarized yourself with the information under [Task Processing Scope](task-processing-scope-b4f8ec6.md) to ensure that you're using the right means to grant access.




## Context

![Graphic depicting the relationship between objects and user roles: A user is assigned to a user role, which in turn has authorizations assigned. Additionally, organizational units are assigned to the user role and to folders in the task lists at the same time. This assignment on both sides (user role and task list) establishes the relationship between user and object and it grants access. Access to the folder automatically grants access to tasks.You can grant access that is restricted to specific organizational units. The authorizations then only apply to tasks of the selected organizational units. The following graphic explains the relationship between the aspects involved:](images/Image_New_Auth_Concept_-_PROC_Access_to_Org_Units_ced8f0f.png)

The abstraction level between user roles and specific objects enables you to grant access to collections of objects, for example, according to the domain of expertise.

> ### Example:  
> **Quick Demo: Access to Specific Organizational Units Within the *Task Processing* Scope**
> 
> The following quick demo shows how to create a user role within the *Task Processing* scope granting *Parameters* access to specific organizational units performing the steps described below:
> 
> > ### Note:  
> > The following multimedia content displays screens and interfaces in English only. It shows sequences based on the UI as delivered standard by SAP.
> > 
> > Interfaces may differ slightly depending on the version of your apps.



## Procedure

1.  Open the *Configuration* app.

    The next screen lists all the configuration apps you're allowed to access.

2.  Choose *User Roles* from the list.

    This brings you to the *Manage User Roles* app.

3.  Go to the *Scoped User Roles* tab.

4.  Choose *Create* in the table toolbar.

5.  Provide the following information:

    1.  Under *Name*You can grant access that is restricted to specific organizational units. The authorizations, freely define a name for your user role.

    2.  Under *Description*, you can add a description for your user role.

    3.  Under *Scope*, select *Task Processing*.

    4.  Under *Type*, select *System-Dependent*.

    5.  Under *Restriction*, select *Restricted*.


6.  Choose *Create* in the dialog footer. The user role is created and opened right away.

7.  Under *Authorizations*, choose *Add* and select an authorization you want to add.

    > ### Note:  
    > *Read* authorization is the minimum authorization required for all user roles. Accordingly, it is added to each user role automatically from the beginning.

    > ### Remember:  
    > Users who have this role assignment have the authorizations across all task list templates and task lists.

    **Authorizations for Task Processing**


    <table>
    <tr>
    <th valign="top">

    Authorization
    
    </th>
    <th valign="top">

    Description
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    *Read*
    
    </td>
    <td valign="top">
    
    Read authorization within the scope of this user role. This is the minimum authorization, and it's included in all others.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Process*
    
    </td>
    <td valign="top">
    
    Authorization to process tasks. This authorization covers actions related to task status changes, scheduling, test runs, attachments, and notes. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Plan*
    
    </td>
    <td valign="top">
    
    Authorization to change attributes that relate to the planning of a task. This authorization covers changes to the planned start and planned duration as well as path recalculation. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Parameters*
    
    </td>
    <td valign="top">
    
    Authorization to change parameters within the scope of this user role. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *User Assignment*
    
    </td>
    <td valign="top">
    
    Authorization to change processing users or user groups, and users responsible or responsible user groups within the scope of this user role. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Approve / Reject*
    
    </td>
    <td valign="top">
    
    Authorization to approve and reject tasks that require approval. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    </table>
    
8.  Repeat the previous step to assign additional authorizations.

9.  To remove an authorization, choose the corresponding *Delete* icon :x:.

    > ### Remember:  
    > Some authorizations include others. When removing authorizations, you need to start with the broader authorization, since the included authorization is a minimum for the broader one.

10. Under *Assigned Company Codes*, *Assigned Controlling Areas*, and *Assigned Plants*, add the organizational unit to which this role grants access.

    > ### Note:  
    > You can add several organizational units if the selected authorizations need to be applied to several organizational units. Keep in mind that all users who have this role assignment have access to **all objects** of these organizational units.

    > ### Caution:  
    > The organizational units you maintain in the role are independent of each other and always give access to the specific organizational unit and all underlying organizational units. This means that if you add a controlling area to this role, you can't restrict the access to specific company codes within this controlling area by additionally assigning these company codes. You can, however, add several company codes to one role, even without adding a controlling area or plant. In that case, you only grant access to the specific company codes and all their underlying organizational units.

11. Whenever you made a change to a user role, choose *Activate* in the header.

    This activates the user role and, if users were already assigned, this also synchronizes any changes with the users assigned.




<a name="loio16947f19a23d41ba832e1fa1314aca43__result_vfx_jsl_qrb"/>

## Results

You have now created a user role within the *Task Processing* scope for access restricted to tasks of the organizational units selected.



<a name="loio16947f19a23d41ba832e1fa1314aca43__postreq_ugr_ssl_qrb"/>

## Next Steps

Grant users this access by assigning them to the user role or the role to them. For more information, see [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

