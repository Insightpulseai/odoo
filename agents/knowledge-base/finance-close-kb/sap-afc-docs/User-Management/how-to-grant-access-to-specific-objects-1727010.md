<!-- loio1727010ff7724f56bbcd0e71d0e1f759 -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# How to Grant Access to Specific Objects

Grant access to task models located in specific communication systems.



<a name="loio1727010ff7724f56bbcd0e71d0e1f759__prereq_hx5_kzj_qrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates or role template combinations:

    -   `AFC_Config`

    -   `AFC_UserRoles`

    -   `AFC_UserRolesSingleApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You've familiarized yourself with the information under [Task Model Management Scope](task-model-management-scope-c951f94.md) to ensure that you're using the right means to grant access.




## Context

You can grant access that is restricted to task models in specific communication systems.



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

    3.  Under *Scope*, select *Task Model Management*.

    4.  *Type* \(read-only\):

        For scope *Task Model Management*, this is always *System-Independent*.

    5.  Under *Restriction*, select *Restricted*.


6.  Choose *Create* in the dialog footer. The user role is created and opened right away.

7.  Under *Authorizations*, choose *Add* and select an authorization you want to add.

    **Authorizations for Task Model Management**


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
    
    Read authorization within the scope of this user role.
    
    </td>
    </tr>
    </table>
    
8.  Repeat the previous step to assign additional authorizations.

9.  To remove an authorization, choose the corresponding *Delete* icon :x:.

10. Under *Assigned Communication Systems*, add the communication systems where the task models for which you want to grant authorization are located.

11. Whenever you made a change to a user role, choose *Activate* in the header.

    This activates the user role and, if users were already assigned, this also synchronizes any changes with the users assigned.




<a name="loio1727010ff7724f56bbcd0e71d0e1f759__result_mcz_31k_qrb"/>

## Results

You have now created a user role within the scope *Task Model Management* for access restricted to task models located in specific communication systems.



<a name="loio1727010ff7724f56bbcd0e71d0e1f759__postreq_ibf_k1k_qrb"/>

## Next Steps

Grant users this access by assigning them to the user role or the role to them. For more information, see [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

