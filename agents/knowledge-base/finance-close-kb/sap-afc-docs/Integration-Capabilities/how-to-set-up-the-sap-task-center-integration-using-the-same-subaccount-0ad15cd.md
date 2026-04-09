<!-- loio0ad15cd8216b47499b9facfaf91368c1 -->

# How to Set Up the SAP Task Center Integration Using the Same Subaccount

You have one subaccount in which SAP Advanced Financial Closing and SAP Task Center are set up.



<a name="loio0ad15cd8216b47499b9facfaf91368c1__prereq_knf_l1c_gzb"/>

## Prerequisites

-   You've created an API instance and service key for API integration scenarios for SAP Advanced Financial Closing as described under [How to Create an API Instance and Service Key for API Integration Scenarios](how-to-create-an-api-instance-and-service-key-for-api-integration-scenarios-4058064.md).

    Make sure that you have the following service key values, which you'll need to set up the destination:

    -   *endpoints* \> *task-center*
    -   *uaa* \> *clientid*
    -   *uaa* \> *clientsecret*
    -   *uaa* \> *url*

    For more information, see [Connect SAP Advanced Financial Closing and SAP Task Center](https://help.sap.com/docs/task-center/sap-task-center/connect-afc-and-sap-task-center).

-   You have access to your identity authentication service.

-   You've configured your SAP Build Work Zone.


<a name="task_rsx_ydc_gzb"/>

<!-- task\_rsx\_ydc\_gzb -->

## Establish Trust with Identity Authentication



<a name="task_rsx_ydc_gzb__steps_vv1_12c_gzb"/>

## Procedure

1.  In the SAP BTP cockpit, choose *Security* \> *Trust Configuration*.

2.  Choose *Establish Trust*. See [Tenant OpenID Connect Configurations](https://help.sap.com/docs/identity-authentication/identity-authentication/tenant-openid-connect-configurations).

    1.  Choose a tenant.

    2.  Choose a domain.

    3.  Configure the parameters.

    4.  Save your changes.

    5.  Make sure that the trust configuration is available for user logon.


    Alternatively, you can use SAML 2.0. For more information, see [Tenant SAML 2.0 Configuration](https://help.sap.com/docs/identity-authentication/identity-authentication/tenant-saml-2-0-configuration).

3.  To assign users permissions so they can perform actions in the task, choose one of the following options.

    -   Assign role collections to users and user groups. For more information, see [Assigning Role Collections to Users or User Groups](https://help.sap.com/docs/btp/sap-business-technology-platform/assigning-role-collections-to-users-or-user-groups).

    -   Assign role collections to business users. For more information, see [Mapping Role Collections in the Subaccount](https://help.sap.com/docs/btp/sap-business-technology-platform/mapping-role-collections-in-subaccount).

        > ### Note:  
        > Make sure that the user name value matches the subject name identifier configured in the identity provider. For example, if the subject name identifier is *email*, then the user name must be the user's email address. For more information, see also [Create Users](https://help.sap.com/docs/btp/sap-business-technology-platform/create-users) and [Configure the Subject Name Identifier Sent to the Application](https://help.sap.com/docs/identity-authentication/identity-authentication/configure-subject-name-identifier-sent-to-application).



<a name="task_llf_j2c_gzb"/>

<!-- task\_llf\_j2c\_gzb -->

## Adapt Subaccount to Subject Name Identifier



<a name="task_llf_j2c_gzb__steps_j35_k2c_gzb"/>

## Procedure

1.  Access the Identity Authentication service, and choose *Applications & Resources* \> *Applications*.

2.  Search for an application named `XSUAA_<subaccount_name>`.

3.  In the new application, access *Protocol* and ensure that the protocol is set to *OpenID Connect*.

4.  In the new application, access *Subject Name Identifier*.

    1.  Under *Basic Configuration*, select one of the values supported for the basic attribute: *Global User ID*, *User ID*, *Email*, *Display Name*, or *Login Name*.

        **Supported Values**


        <table>
        <tr>
        <th valign="top">

        Parameter
        
        </th>
        <th valign="top">

        Value
        
        </th>
        </tr>
        <tr>
        <td valign="top">
        
        `User ID`
        
        </td>
        <td valign="top">
        
        `userId`
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `E-Mail`
        
        </td>
        <td valign="top">
        
        `email`
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `Display Name`
        
        </td>
        <td valign="top">
        
        `displayName`
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `Login Name`
        
        </td>
        <td valign="top">
        
        `loginName`
        
        </td>
        </tr>
        </table>
        
        For more information, see [Configure the Subject Name Identifier Sent to the Application](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/1d020e3a3ba34c43a71fde70bfa6419a.html?version=Cloud).

    2.  Save your changes.


5.  In the new application, access *Assertion Attributes*.

    1.  Choose *Add* and select the *Groups* user attribute.

    2.  For the *Groups* entry, change the *Assertion Attribute* entry to use an uppercase G.

    3.  Save your changes.



<a name="task_lzj_ffc_gzb"/>

<!-- task\_lzj\_ffc\_gzb -->

## Resolve Users Recipients

As recipients of approvals or forms, SAP Advanced Financial Closing supports global user IDs, user IDs, login names, and email addresses. The default setting is user UUIDs.



<a name="task_lzj_ffc_gzb__prereq_y1b_tls_vvb"/>

## Prerequisites

The system administrator used for the `Identity_Authentication_Connectivity_IDS` destination must have authorization to read and export users \(*Read Users*\). See [Add System as Administrator \(step 5\)](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/bbbdbdd3899942ce874f3aae9ba9e21d.html?version=Cloud#loiocefb742a36754b18bbe5c3503ac6d87c).



<a name="task_lzj_ffc_gzb__steps_ppl_gfc_gzb"/>

## Procedure

1.  In the SAP Advanced Financial Closing subaccount, access the `Identity_Authentication_Connectivity_IDS` destination.

2.  Add the additional `wfs.subjectNameIdentifier` property as described in [Create HTTP Destinations](https://help.sap.com/docs/CP_CONNECTIVITY/cca91383641e40ffbe03bdc78f00f681/783fa1c418a244d0abb5f153e69ca4ce.html).

    > ### Note:  
    > If you're using the global user ID as the subject name identifier, this property is not needed.

3.  As the value, specify the subject name identifier configured in your identity authentication.

    **Supported Values**


    <table>
    <tr>
    <th valign="top">

    Parameter
    
    </th>
    <th valign="top">

    Value
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    `User ID`
    
    </td>
    <td valign="top">
    
    `userId`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    `E-Mail`
    
    </td>
    <td valign="top">
    
    `email`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    `Display Name`
    
    </td>
    <td valign="top">
    
    `displayName`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    `Login Name`
    
    </td>
    <td valign="top">
    
    `loginName`
    
    </td>
    </tr>
    </table>
    
    For more information, see [Configure the Subject Name Identifier Sent to the Application](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/1d020e3a3ba34c43a71fde70bfa6419a.html?version=Cloud).




<a name="task_lzj_ffc_gzb__postreq_hcg_khx_pzb"/>

## Next Steps

After you've performed the steps described on this page, continue with the next steps described in the [SAP Task Center documentation](https://help.sap.com/docs/task-center/sap-task-center/connect-afc-and-sap-task-center).

