<!-- loioc338b300dd01425bb74c04f0833f417c -->

# How to Manage Users

Upload new users to SAP Advanced Financial Closing and update certain user attributes.



<a name="loioc338b300dd01425bb74c04f0833f417c__prereq_sqn_c1c_ckb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_UserAdmin`

    -   `AFC_ManageUsersApp`


    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   The users you want to upload must be maintained in your identity provider \(IdP\) including the following user attributes:

    -   `logonName`

    -   `givenName`

    -   `familyName`

    -   `email`





## Context

Users who are maintained in the IdP are able to sign in to SAP Advanced Financial Closing without any additional setting. They can access the apps according to the static role templates that are assigned to them.

In addition, you can upload users manually to SAP Advanced Financial Closing in advance so that you can assign user roles to them and enter them as users responsible or processing users, for example. For all user attributes that are maintained in the IdP, you have to do this only once. If certain user attributes aren't maintained in your IdP, you can use the upload function to keep these attributes up to date. In the *Manage Users* app, you can see all users available in SAP Advanced Financial Closing, independently of whether they were uploaded or created through their first sign-in.

You **must maintain** the user attributes `logonName`, `givenName`, `familyName`, and `email` in the IdP. In SAP Advanced Financial Closing, you can only maintain these attributes via the initial user upload or until the users have signed in for the first time. You can't use the upload to update these attributes.

You **can** maintain the following user attributes in the IdP and have to map them to the corresponding user attributes in SAP Advanced Financial Closing. Alternatively, you can maintain these attributes by uploading users manually.

**User Attributes**


<table>
<tr>
<th valign="top">

Identity Provider

</th>
<th valign="top">

SAP Advanced Financial Closing

</th>
</tr>
<tr>
<td valign="top">

`Address`

</td>
<td valign="top">

`address`

</td>
</tr>
<tr>
<td valign="top">

`Phone`

</td>
<td valign="top">

`phone`

</td>
</tr>
<tr>
<td valign="top">

`Mobile`

</td>
<td valign="top">

`mobile`

</td>
</tr>
<tr>
<td valign="top">

`Fax`

</td>
<td valign="top">

`fax`

</td>
</tr>
<tr>
<td valign="top">

`Department`

</td>
<td valign="top">

`department`

</td>
</tr>
<tr>
<td valign="top">

`Function`

</td>
<td valign="top">

`function`

</td>
</tr>
<tr>
<td valign="top">

`Division`

</td>
<td valign="top">

`function` \(if function is empty\)

</td>
</tr>
</table>

> ### Note:  
> The information provided by the IdP always takes precedence. User attributes from the IdP overwrite the information stored in SAP Advanced Financial Closing when the users sign in to the app.

> ### Caution:  
> Make sure that the user attribute `email` isn't empty and is always maintained correctly. The following features can't be used if the email isn't entered correctly because they rely on the email address to find the respective user in the connected financial communication systems:
> 
> -   Task scheduling using this user
> 
> -   Notifications and email to this user



## Procedure

1.  Go to the *Manage Users* app.

2.  In the table toolbar, choose *Download Template* to download the user template file.

3.  Fill the template file with your users according to the format provided.

    > ### Note:  
    > -   The *ID* field is mandatory, and the value entered must match the user ID maintained in the IdP. Note that the field is case-sensitive.
    > 
    > -   For information about which language codes are allowed, refer to [Language Codes Allowed for User Upload](language-codes-allowed-for-user-upload-51c9133.md).
    > 
    > -   Use semicolons as column separators.
    > 
    >     > ### Note:  
    >     > If the application you're using to fill out the template has a setting that indicates that the system-defined separators are being used, deactivate this option and define semicolons as column separators.
    > 
    > -   Save the file with UTF-8 encoding.
    > 
    > -   The fields containing numbers have to be formatted as **text** prior to saving the CSV file.

4.  Back in the *Manage Users* app, choose *Upload Users* in the table toolbar.

5.  Either drag and drop the file you prepared or choose *Add* and select the file.

6.  Confirm by choosing *Upload* in the dialog footer.

7.  Review the results of the upload in the dialog that summarizes the changes.

    > ### Note:  
    > When a user is created, it's set to *Inactive*. However, once the person assigned to this user signs in for the first time, the user is activated. For more information about user statuses, see [User Statuses](user-statuses-f476237.md).




<a name="loioc338b300dd01425bb74c04f0833f417c__result_u45_nyd_rkb"/>

## Results

The users are uploaded with source *CSV Upload*. Once the respective users have signed in for the first time, the source is updated to *Identity Provider*. From then on, the identity provider is the source of the user information.

> ### Note:  
> User information provided by the IdP is updated via the IdP. However, you need to update the user information manually which you've uploaded in your CSV file but which you haven't maintained in the IdP.

> ### Tip:  
> If users have maintained substitutes, you can see their substitutes on the *Substitutes* tab in the user details.
> 
> You can also see the history of substitutes for each user, that is, you can see whom the user assigned as their substitute in the past.

-   **[Language Codes Allowed for User Upload](language-codes-allowed-for-user-upload-51c9133.md "")**  

-   **[User Statuses](user-statuses-f476237.md "Learn which statuses and status changes are possible for users.")**  
Learn which statuses and status changes are possible for users.

**Parent topic:**[User Management](user-management-ae7fa30.md "Understand how you can manage users and their authorizations in SAP Advanced Financial Closing.")

**Next:**[How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md "Define and bundle static roles and assign them to users.")

**Previous:**[How to Delete Users](how-to-delete-users-81d47cf.md "Delete users that are no longer required.")

