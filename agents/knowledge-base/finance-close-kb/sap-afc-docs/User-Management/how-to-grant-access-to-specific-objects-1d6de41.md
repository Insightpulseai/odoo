<!-- loio1d6de4177efd46eab7dc83ad456cf53a -->

<link rel="stylesheet" type="text/css" href="../css/sap-icons.css"/>

# How to Grant Access to Specific Objects

Grant access to specific task list templates, task lists, or tasks by assigning one or more authorizations available within this scope.



<a name="loio1d6de4177efd46eab7dc83ad456cf53a__prereq_hx5_kzj_qrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates or role template combinations:

    -   `AFC_Config`

    -   `AFC_UserRoles`

    -   `AFC_UserRolesSingleApp` and `AFC_AuthGroupsApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You've familiarized yourself with the information under [Task Processing Scope](task-processing-scope-b4f8ec6.md) to ensure that you're using the right means to grant access.




## Context

You can grant access that is restricted to specific task list template, task lists, or tasks. The authorizations you select for this user role then only apply to templates, task lists, and tasks to which the selected authorization groups are assigned. The following graphics explain the relationship between the aspects involved:


<table>
<tr>
<th valign="top">

Access to Task List Templates and Task Lists

</th>
<th valign="top">

Access to Tasks

</th>
</tr>
<tr>
<td valign="top">

![Graphic depicting the relationship between objects and user roles: A user is assigned to a user role, which in turn has authorizations assigned. Additionally, authorization groups are assigned to the user role and to task lists at the same time. This assignment on both sides (user role and task list) establishes the relationship between user and object and it grants access. Access to the task list automatically grants access to underlying tasks.](images/Image_New_Auth_Concept_-_PROC_Access_to_Specific_Task_Lists_Templates_fbedd15.png)

</td>
<td valign="top">

![Graphic depicting the relationship between objects and user roles: A user is assigned to a user role, which in turn has authorizations assigned. Additionally, authorization groups are assigned to the user role and to tasks at the same time. This assignment on both sides (user role and task) establishes the relationship between user and object and it grants access.](images/Image_New_Auth_Concept_-_PROC_Access_to_Specific_Tasks_8e356bb.png)

</td>
</tr>
</table>

The abstraction level between user roles and specific objects enables you to grant access to collections of objects, for example, according to the domain of expertise.

> ### Example:  
> **Quick Demo: Access to Specific Objects Within the *Task Processing* Scope**
> 
> The following quick demo shows how to create a user role within the *Task Processing* scope granting *Parameters* access to specific object types performing the steps described below:
> 
> > ### Note:  
> > The following multimedia content displays screens and interfaces in English only. It shows sequences based on the UI as delivered standard by SAP.
> > 
> > Interfaces may differ slightly depending on the version of your apps.



## Procedure

1.  Open the *Configuration* app.

    The next screen lists all the configuration apps you're allowed to access.

2.  Choose *Authorization Groups* from the list.

    This brings you to the *Manage Authorization Groups* app.

3.  Choose *Create* in the table toolbar.

4.  Provide the following information:

    1.  Under *Name*, freely define a name for your authorization group.

    2.  Under *Applied To*, select one of the following:

        -   *Task List Template / Task List* to grant access to task list templates or task lists.

        -   *Task* to grant access to tasks.


    3.  Under *Description*, you can add a description for your authorization group.


5.  Save.

6.  Go back to the *Configuration* app and choose *User Roles*.

7.  Go to the *Scoped User Roles* tab.

8.  Choose *Create* in the table toolbar.

9.  Provide the following information:

    1.  Under *Name*, freely define a name for your user role.

    2.  Under *Description*, you can add a description for your user role.

    3.  Under *Scope*, select *Task Processing*.

    4.  Under *Type*, select *System-Independent*.

    5.  Under *Restriction*, select *Restricted*.


10. Choose *Create* in the dialog footer. The user role is created and opened right away.

11. Under *Authorizations*, choose *Add* and select an authorization you want to add.

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
    
12. Repeat the previous step to assign additional authorizations.

13. To remove an authorization, choose the corresponding *Delete* icon :x:.

    > ### Remember:  
    > Some authorizations include others. When removing authorizations, you need to start with the broader authorization, since the included authorization is a minimum for the broader one.

14. Under *Task Lists* and *Tasks*, add the authorization group you created before for the respective object type.

    > ### Note:  
    > You can add several authorization groups if the selected authorizations need to be applied to several authorization groups. Keep in mind that all users who have this role assignment have access to **all objects** that these authorization groups are assigned to on task list level.

15. Whenever you made a change to a user role, choose *Activate* in the header.

    This activates the user role and, if users were already assigned, this also synchronizes any changes with the users assigned.




<a name="loio1d6de4177efd46eab7dc83ad456cf53a__result_mcz_31k_qrb"/>

## Results

You have now created a user role within the scope *Task Processing* for access restricted to task list templates, task lists, and tasks that have the selected authorization groups assigned.



<a name="loio1d6de4177efd46eab7dc83ad456cf53a__postreq_ibf_k1k_qrb"/>

## Next Steps

Grant users this access by assigning them to the user role or the role to them. For more information, see [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

