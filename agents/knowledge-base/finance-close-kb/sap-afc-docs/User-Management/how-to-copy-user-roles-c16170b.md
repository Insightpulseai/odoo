<!-- loioc16170b31fd5467ba96a764c71e89433 -->

# How to Copy User Roles

Copy scoped user roles.



<a name="loioc16170b31fd5467ba96a764c71e89433__prereq_zdr_xnq_x5b"/>

## Prerequisites

Your user must have a role collection assigned that includes one of the following role templates:

-   `AFC_Config`

-   `AFC_UserRoles`

-   `AFC_UserRolesSingleApp`


For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

You can copy a scoped user role to reuse its settings for another role. The following changes are applied in the copied role:

-   User assignments aren't taken over to the copied role.

-   Administrative data for the copied role is filled with the data of the user creating the copied role.

-   The status of the copied role is set to *Pending Changes*.


The user role name with the added suffix *\- Copy* and the description of the original role are taken over as proposal to the copied role. Both entries can be changed in the copy dialog directly.

The following graphic shows what happens during the copying step:

![Graphic depicting two columns, representing the original user role on the left and the copied role on the right: The user role on the left has the following attributes attached: name, main information (scope restriction, status, and administrative data), then general information (type and description), and finally authorizations, authorization group assignments (if available), and organizational unit assignments (if available). The users assigned to the role are also mentioned. In the copied role on the right, the following changes are highlighted: users assigned to the role aren't taken over to the copied role, the role name gets the suffix "- Copy", the status is set to "Pending Changes", and the administrative data is filled with the data of the user creating the copied role.](images/Image_Copy_Scoped_User_Role_6ac16ad.png)

You can edit the information of the copied role the same way as for other user roles.



## Procedure

1.  Open the *Configuration* app and choose *User Roles*.

2.  Go to the *Scoped User Roles* tab.

3.  Search for the user role you want to copy and select it in the table.

4.  Choose *Copy* in the table toolbar.

    > ### Note:  
    > You can also choose *Copy* in the header in the role details.

5.  In the new dialog, provide a name and description for the copied role.

    > ### Note:  
    > The fields are filled with the following default values:
    > 
    > 
    > <table>
    > <tr>
    > <th valign="top">
    > 
    > Field
    > 
    > </th>
    > <th valign="top">
    > 
    > Default Value
    > 
    > </th>
    > </tr>
    > <tr>
    > <td valign="top">
    > 
    > *Name*
    > 
    > </td>
    > <td valign="top">
    > 
    > Name of the original user role with the suffix *\- Copy* added
    > 
    > </td>
    > </tr>
    > <tr>
    > <td valign="top">
    > 
    > *Description*
    > 
    > </td>
    > <td valign="top">
    > 
    > Description of the original user role
    > 
    > </td>
    > </tr>
    > </table>

6.  Choose *Copy* in the dialog footer.

    **Result:** The copied role is created and the role details are opened right away.

7.  You can make changes to the copied role as described in the corresponding section:

    -   [Task List Creation Scope](task-list-creation-scope-ba4100e.md)

    -   [Task Processing Scope](task-processing-scope-b4f8ec6.md)


8.  When you're finished, choose *Activate* in the details header.




<a name="loioc16170b31fd5467ba96a764c71e89433__result_gwj_r3s_x5b"/>

## Results

You have now copied a scoped user role.



<a name="loioc16170b31fd5467ba96a764c71e89433__postreq_bm4_s3s_x5b"/>

## Next Steps

To make use of the new user role, assign users to it as described under [How to Assign Users to User Roles](how-to-assign-users-to-user-roles-f703a5c.md).

