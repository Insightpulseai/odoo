<!-- loioddf490b678744eb5891854f9862c807a -->

# How to Grant General Access

Grant general access by assigning one or more authorizations available within this scope.



<a name="loioddf490b678744eb5891854f9862c807a__prereq_drt_ws3_qrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_Config`

    -   `AFC_UserRoles`

    -   `AFC_UserRolesSingleApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You've familiarized yourself with the information under [Task Model Management Scope](task-model-management-scope-c951f94.md) to ensure that you're using the right means to grant access.




## Context

You can grant access that applies to all objects within the scope, independently of the related communication system. However, you can still decide which authorizations to grant. This means that even though user access isn't restricted to specific objects, general access doesn't necessarily mean that users can perform all actions on task models.



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

    5.  Under *Restriction*, select *Unrestricted*.


6.  Choose *Create* in the dialog footer. The user role is created and opened right away.

    > ### Remember:  
    > For users who have this role assignment, *Read* authorization applies across all task models.

7.  Whenever you made a change to a user role, choose *Activate* in the header.

    This activates the user role and, if users were already assigned, this also synchronizes any changes with the users assigned.




<a name="loioddf490b678744eb5891854f9862c807a__result_frf_sz3_qrb"/>

## Results

You have now created a user role for general access within the *Task Model Management* scope.



<a name="loioddf490b678744eb5891854f9862c807a__postreq_k4s_q1j_qrb"/>

## Next Steps

Grant users this access by assigning them to the user role or the role to them. For more information, see [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

