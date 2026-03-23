<!-- loio2d5fa55c30dc4767af47f624aca9ba7c -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# How to Grant General Access

Grant general access by assigning one or more authorizations available within this scope.



<a name="loio2d5fa55c30dc4767af47f624aca9ba7c__prereq_qx4_fqj_qrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_Config`

    -   `AFC_UserRoles`

    -   `AFC_UserRolesSingleApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You've familiarized yourself with the information under [Task Processing Scope](task-processing-scope-b4f8ec6.md) to ensure that you're using the right means to grant access.




## Context

You can grant access that applies to all objects within the scope, independently of the related communication system or authorization groups. However, you can still decide which authorizations to grant. This means that even though user access isn't restricted to specific objects or organizational units, general access doesn't necessarily mean that users can perform all actions.

> ### Example:  
> **Quick Demo: General Access Within the Task Processing Scope**
> 
> The following quick demo shows how to create a user role within the *Task Processing* scope granting general *User Assignment* access by performing the steps described below:
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

    1.  Under *Name*, freely define a name for your user role.

    2.  Under *Description*, you can add a description for your user role.

    3.  Under *Scope*, select *Task Processing*.

    4.  Under *Type*, select *System-Independent*.

    5.  Under *Restriction*, select *Unrestricted*.


6.  Choose *Create* in the dialog footer. The user role is created and opened right away.

7.  Under *Authorizations*, choose *Add* and select an authorization you want to add.

    > ### Note:  
    > *Read* authorization is the minimum authorization required for all user roles. Accordingly, it is added to each user role automatically from the beginning.

    > ### Remember:  
    > For users who have this role assignment, the authorizations selected apply across all task lists.

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
    
8.  Choose *Add* in the dialog footer.

9.  Repeat the previous steps to assign additional authorizations.

10. To remove an authorization, choose the corresponding *Delete* icon :x:.

    > ### Remember:  
    > Some authorizations include others. When removing authorizations, you need to start with the broader authorization, since the included authorization is a minimum for the broader one.

11. Whenever you made a change to a user role, choose *Activate* in the header.

    This activates the user role and, if users were already assigned, this also synchronizes any changes with the users assigned.




<a name="loio2d5fa55c30dc4767af47f624aca9ba7c__result_zbw_fqj_qrb"/>

## Results

You have now created a user role for general access within the *Task Processing* scope.



<a name="loio2d5fa55c30dc4767af47f624aca9ba7c__postreq_frb_gqj_qrb"/>

## Next Steps

Grant users this access by assigning them to the user role or the role to them. For more information, see [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

