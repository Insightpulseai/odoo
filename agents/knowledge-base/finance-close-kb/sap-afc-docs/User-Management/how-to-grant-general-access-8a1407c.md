<!-- loio8a1407c498574d4d8dd5a2e611695afd -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# How to Grant General Access

Grant general access by assigning one or more authorizations available within this scope.



<a name="loio8a1407c498574d4d8dd5a2e611695afd__prereq_drt_ws3_qrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_Config`

    -   `AFC_UserRoles`

    -   `AFC_UserRolesSingleApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You've familiarized yourself with the information under [Task Group Management Scope](task-group-management-scope-12ebd1d.md) to ensure that you're using the right means to grant access.




## Context

You can grant access that applies to all objects within the scope. However, you can still decide which authorizations to grant. This means that even though user access isn't restricted to specific objects, general access doesn't necessarily mean that users can perform all actions on task group templates.



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

    3.  Under *Scope*, select *Task Group Management*.

    4.  *Type* \(read-only\):

        For scope *Task Group Management*, this is always *System-Independent*.

    5.  *Restriction* \(read-only\):

        For scope *Task Group Management*, this is always *Unrestricted*.


6.  Choose *Create* in the dialog footer. The user role is created and opened right away.

7.  Under *Authorizations*, choose *Add* and select an authorization you want to add.

    > ### Note:  
    > *Read* authorization is the minimum authorization required for all user roles. Accordingly, it is added to each user role automatically from the beginning.

    > ### Remember:  
    > For users who have this role assignment, the authorizations selected apply across all task group templates.

    **Authorizations for Task Group Management**


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
    
    *Create*
    
    </td>
    <td valign="top">
    
    Authorization to create and copy task group templates. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Write*
    
    </td>
    <td valign="top">
    
    Authorization to edit task group templates. This authorization always includes *Read* authorization.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Delete*
    
    </td>
    <td valign="top">
    
    Authorization to delete task group templates. This authorization always includes *Read* authorization.
    
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




<a name="loio8a1407c498574d4d8dd5a2e611695afd__result_frf_sz3_qrb"/>

## Results

You have now created a user role for general access within the *Task Group Management* scope.



<a name="loio8a1407c498574d4d8dd5a2e611695afd__postreq_k4s_q1j_qrb"/>

## Next Steps

Grant users this access by assigning them to the user role or the role to them. For more information, see [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

