<!-- copy81d47cfa65674b8c9f6cfb94b3167bbc -->

# How to Delete Users

Delete users that are no longer required.



<a name="copy81d47cfa65674b8c9f6cfb94b3167bbc__prereq_ysh_fzc_kkb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_UserAdmin`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   Assignments of the user to be deleted should be checked and updated beforehand:

    1.  In SAP Advanced Financial Closing, an authorized user needs to check existing task lists for assignments of the affected user and update them if required.

        > ### Caution:  
        > If a deleted user is assigned to a generated task list or its tasks and the user is required for task processing, the financial closing process may be disrupted.

    2.  An authorized user needs to check task list templates for assignments of the affected user and update them if required.

        > ### Note:  
        > If a deleted user is assigned to a task list template, the next consistency check will return error or warning messages. Task list generation may not be possible.

    3.  The user you're trying to delete must not be assigned to any user group.

        > ### Note:  
        > If such an assignment exists, you can set the user to *Deleted*, but you can't delete the user permanently.
        > 
        > **Restriction:** If the user is the last active user in a user group, the user can't be set to *Deleted* or even be deleted permanently.

    4.  The user you're trying to delete must not have any user role assignments.

        > ### Note:  
        > If such an assignment exists, you can set the user to *Deleted*, but you can't delete the user permanently.





## Context

> ### Caution:  
> To revoke all access to SAP Advanced Financial Closing from users, it is not enough to delete them using the *Manage Users* app. You need to **revoke further access rights**. For more information, see the procedure, results, and next steps described below.

When you delete users from SAP Advanced Financial Closing, there is no retention period, which means that the user data is deleted directly. Therefore, keep in mind the consequences and possible additional steps when you delete users. These steps are described in the prerequisites and in the procedure below.



## Procedure

**Deleting Users in SAP Advanced Financial Closing**

1.  To delete a user in SAP Advanced Financial Closing, open the *Manage Users* app.

2.  Select the user you want to delete and choose *Delete* in the table toolbar.

    > ### Tip:  
    > You can display all deleted users by selecting *Deleted* in the *Status* filter.

    **Result:** You have now deleted a user in SAP Advanced Financial Closing.

    > ### Remember:  
    > To revoke all access to SAP Advanced Financial Closing from users, it is not enough to delete them using the *Manage Users* app. You need to **revoke further access rights** in the SAP BTP cockpit as described below.


**Deleting Users from Role Collections in the SAP BTP Cockpit**

3.  To avoid the reactivation of a user through a new logon via the identity provider \(IdP\), you also need to unassign the user from all role collections **relevant for SAP Advanced Financial Closing**. This way, access to all apps for SAP Advanced Financial Closing is revoked. You can delete the user from role collections using the SAP BTP cockpit. For more information, see [Delete Users from Role Collections](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/4f8a242839a947f9a6f379650480c776.html).




<a name="copy81d47cfa65674b8c9f6cfb94b3167bbc__result_xhj_v4w_gnb"/>

## Results

-   The user's data is now removed from the system. The user is now displayed as a deleted user. The only information that remains is the user ID. However, keep in mind that users who have been deleted can be reactivated if you haven't deleted their role collection assignments in the SAP BTP cockpit.

-   A deleted user's ID might still be displayed in the system, for example, in logs or in relation to objects.




<a name="copy81d47cfa65674b8c9f6cfb94b3167bbc__postreq_e3k_rnw_gnb"/>

## Next Steps

-   To reactivate users, upload them again to match them to their previous ID. Alternatively, users can log in via the IdP to reactivate their account. After users have been reactivated, they are assigned to the same role collections and user roles as they were before the deletion.

-   To ensure that the deleted user isn't assigned in any task list templates anymore, an authorized user can run consistency checks on the templates and update any remaining assignments.

    > ### Tip:  
    > A new consistency check will detect assignments of deleted users in templates and return either an error or a warning message as described under [How to Perform Checks on Templates](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/bd90b43614b841f48796e068fb1fcb6c.html "Check whether your templates fulfill all requirements.") :arrow_upper_right:.


**Parent topic:**[User Management](user-management-ae7fa30.md "Understand how you can manage users and their authorizations in SAP Advanced Financial Closing.")

**Next:**[How to Manage Users](how-to-manage-users-c338b30.md "Upload new users to SAP Advanced Financial Closing and update certain user attributes.")

**Previous:**[User Access Management](user-access-management-d974847.md "You can control and grant access to task list templates, task lists, and tasks in SAP Advanced Financial Closing. By default, users don't have access to these objects.")

