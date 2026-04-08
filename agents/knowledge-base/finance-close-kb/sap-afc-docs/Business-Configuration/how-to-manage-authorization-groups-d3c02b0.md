<!-- loiod3c02b0e04f74433abc3856f3b224c2e -->

# How to Manage Authorization Groups

Use authorization groups to grant object-specific access.



<a name="loiod3c02b0e04f74433abc3856f3b224c2e__prereq_dgq_crk_htb"/>

## Prerequisites

Your user must have a role collection assigned that includes one of the following role templates:

-   `AFC_Config`

-   `AFC_UserRoles`

-   `AFC_AuthGroupsApp`


For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

You can use authorization groups to grant access to specific objects, that is, either to tasks or to task list templates and task lists. Additionally, you need to assign the authorization group to a user role in order to grant access.

> ### Example:  
> **Quick Demo: Create and Assign an Authorization Group**
> 
> The following quick demo shows how to create an authorization group performing the steps described below, and how to assign it to a user role as mentioned under *Next Steps*:
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

3.  To create a new authorization group, choose *Create* in the table toolbar.

4.  Provide a unique name.

5.  Under *Applied To*, select the object type that you want this group to be used for.

    For example, if you want to use this authorization group to grant access to specific task lists, select *Task List Template / Task List*.

6.  You can also add a description for this group.

7.  Choose *Create* in the footer to create the authorization group.




<a name="loiod3c02b0e04f74433abc3856f3b224c2e__result_fzj_xbq_gtb"/>

## Results

You have now created an authorization group.



<a name="loiod3c02b0e04f74433abc3856f3b224c2e__postreq_jqb_ybq_gtb"/>

## Next Steps

You can now make the necessary assignments to grant access to specific objects. Perform the following steps:

1.  Add the authorization group to a user role to define the authorizations you want to grant using this group.

2.  Assign the authorization group to an object of the type you specified in the authorization group.


> ### Remember:  
> For more information about the use cases, refer to the following information:
> 
> -   For the *Task List Creation* scope, see [How to Grant Access to Specific Objects](../User-Management/how-to-grant-access-to-specific-objects-822ddcf.md).
> 
> -   For the *Task Processing* scope, see [How to Grant Access to Specific Objects](../User-Management/how-to-grant-access-to-specific-objects-1d6de41.md).

