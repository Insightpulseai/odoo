<!-- loiof703a5c6ee0a4fda9f565a67d49d35b7 -->

# How to Assign Users to User Roles

Specify the users to whom the user roles you've created apply.



<a name="loiof703a5c6ee0a4fda9f565a67d49d35b7__prereq_n3m_51c_ckb"/>

## Prerequisites

Your user must have a role collection assigned that includes one of the following role templates:

-   `AFC_UserManagement`

-   `AFC_UserAdmin`


For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

The user roles you've created take effect only once you assign users to them. Users who have no user role assigned don't have access to any data unless they’re maintained as a user responsible or processing user or as a substitute.

> ### Note:  
> A substitute of an owner, a user responsible, or a processing user doesn't inherit role assignments. Accordingly, substitutes may need to be assigned to the same user roles as the owners, users responsible, or processing users they're substituting for.



## Procedure

1.  Go to the *Manage User Role Assignments* app.

2.  Decide how you want to perform the assignment:

    1.  You can perform single assignments. There are two ways to do this:

        -   To assign users to a specific user role, go to the *User Roles* tab and open a user role from the table.

            -   In the *Users* table, choose *Add*.

            -   In the table, select the users you want to assign.

            -   Choose *Add* in the dialog footer.


        -   To assign user roles to a specific user, go to the *Users* tab and open the user details of a user from the table.

            -   In the *User Roles* table, choose *Add*.

            -   In the table, select the user roles you want to assign.

            -   Choose *Add* in the dialog footer.



    2.  You can perform a batch assignment by uploading a CSV file that lists the assignments:

        1.  Go to the *User-to-Role Assignments* tab.

        2.  From the table toolbar, download the template to ensure the file has the correct format for the upload.

            > ### Note:  
            > The upload has to be a CSV file with UTF-8 encoding.

        3.  Fill out the template. Add only one role and one user in each row. You can update several roles and several users with one CSV file.

            > ### Caution:  
            > The user ID is case-sensitive. Use the same spelling as in your identity provider.

            > ### Note:  
            > You need to use the exact role names for the assignment to work.

        4.  Save the template.

        5.  On the *User-to-Role Assignments* tab, choose *Upload Assignments* in the table toolbar.

        6.  Choose *Choose File* and select the file from your device.

        7.  Choose *Upload* in the dialog footer.



3.  To get an overview of the user-to-role assignments, go to the *User-to-Role Assignments* tab.

    1.  You can download this overview using the download options in the table toolbar.





<a name="loiof703a5c6ee0a4fda9f565a67d49d35b7__result_v53_jpt_3mb"/>

## Results

The users you've just updated now have access to the data to which the user role grants access.

