<!-- loio98629e172db747eb87df028d56764253 -->

# How to Set Up the SAP Task Center Integration Using Different Subaccounts

You have one subaccount in which SAP Advanced Financial Closing is set up and another subaccount where SAP Task Center is set up.



<a name="loio98629e172db747eb87df028d56764253__prereq_k2s_vfc_gzb"/>

## Prerequisites

-   You've created an API instance and service key for API integration scenarios for SAP Advanced Financial Closing as described under [How to Create an API Instance and Service Key for API Integration Scenarios](how-to-create-an-api-instance-and-service-key-for-api-integration-scenarios-4058064.md).

    Make sure that you have the following service key values, which you'll need to set up the destination:

    -   *endpoints* \> *task-center*
    -   *uaa* \> *clientid*
    -   *uaa* \> *clientsecret*
    -   *uaa* \> *url*

    For more information, see [Connect SAP Advanced Financial Closing and SAP Task Center](https://help.sap.com/docs/task-center/sap-task-center/connect-afc-and-sap-task-center).

-   You have access to your Identity Authentication service.

-   You've configured your SAP Build Work Zone.


<a name="task_dbv_rgc_gzb"/>

<!-- task\_dbv\_rgc\_gzb -->

## Add Fully-Qualified Domain Name



<a name="task_dbv_rgc_gzb__steps_fpw_sgc_gzb"/>

## Procedure

1.  On the SAP Advanced Financial Closing subaccount, add the fully-qualified domain name of the SAP Task Center subaccount as a trusted domain.

    1.  Make sure that you copy the fully-qualified domain name of the SAP Task Center subaccount from the SAP Build Work Zone home page where the Task Center tile is located and not from the *Site Manager - Site Directory* page.

    2.  Choose *Security* \> *Settings* and paste the name in the *Domain* field on the *Trusted Domains* tab.


2.  On the SAP Advanced Financial Closing subaccount, adjust the security headers.

    1.  Open the developer tools when opening a task, and search for the error message ***Refuse to frame ... because an ancestor violates the following Content Security Policy directive: 'frame-ancestors 'self' ...'***.

    2.  Copy the value ***frame-ancestors 'self' ....***.

    3.  In SAP Build Work Zone, choose *Settings* \> *Security Headers*.

    4.  Select the *content-security-policy* security header.

    5.  Add the frame-ancestors from the error message and, after that, the fully-qualified domain name of SAP Task Center subaccount.


    See [Using Security Headers](https://help.sap.com/docs/Launchpad_Service/8c8e1958338140699bd4811b37b82ece/da266508e0594a36a619b3eeeea849e9.html).

3.  In your custom identity provider, choose *Applications & Resources* \> *Tenant Settings*.

    1.  Add the fully-qualified domain name of the SAP Task Center subaccount as a trusted domain.

        See [Configure Trusted Domains for Multi-environment Subaccounts](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/c5e997235f724ec686dc5dc101a1ccfb.html). If you're using a custom identity provider, follow the instructions of that provider.



<a name="task_rf4_ygc_gzb"/>

<!-- task\_rf4\_ygc\_gzb -->

## Establish Trust with Identity Authentication



<a name="task_rf4_ygc_gzb__context_nws_cgn_tyb"/>

## Context

> ### Note:  
> For the trust configuration, particularly when using an existing one, please note that only the SAML protocol is supported.
> 
> **OpenID Connect is not supported.**
> 
> Although the SAP Task Center supports OpenID Connect, for the user propagation between Cloud Foundry Applications, SAML must also be used in the subaccount where SAP Task Center is located.



<a name="task_rf4_ygc_gzb__steps_o33_3hc_gzb"/>

## Procedure

1.  In the SAP BTP cockpit, choose *Security* \> *Trust Configuration*.

2.  Choose *New Trust Configuration*.

    1.  To download the metadata file from your Identity Authentication, see steps 1–4 of [Tenant SAML 2.0 Configuration](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/e81a19b0067f4646982d7200a8dab3ca.html).

    2.  Enter any name.

    3.  Save your changes.


3.  To download the metadata, choose *SAML Metadata*.

    For more information, see [Establish Trust with Any SAML 2.0 Identity Provider in a Subaccount](https://help.sap.com/docs/CP_AUTHORIZ_TRUST_MNG/ae8e8427ecdf407790d96dad93b5f723/2ce3938c66d94479848bff3090999027.html).


<a name="task_zfb_phc_gzb"/>

<!-- task\_zfb\_phc\_gzb -->

## Adapt Subaccount to Subject Name Identifier



<a name="task_zfb_phc_gzb__steps_wp4_qhc_gzb"/>

## Procedure

1.  Access the Identity Authentication service, and choose *Applications & Resources* \> *Applications*.

2.  Create an application by choosing *Create*.

    1.  Enter any display name.

    2.  Select the *SAP BTP Solution* type.

    3.  Save your changes.


3.  In the new application, access *Protocol* and ensure that the protocol is set to SAML.

4.  In the new application, access *SAML 2.0 Configuration*.

    1.  Upload the SAML metadata file for Identity Authentication \(that you downloaded in the last step of the procedure above\) using the *Browse* button next to the *Metadata File* entry field.

    2.  Save your changes.


5.  In the new application, access *Subject Name Identifier*.

    1.  Under *Basic Configuration*, select one of the supported values for the basic attribute: *Global User ID*, *User ID*, *Email*, *Display Name*, or *Login Name*.

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


6.  In the new application, access *Assertion Attributes*.

    1.  Choose *Add* and select the *Groups* user attribute.

    2.  For the *Groups* entry, change the *Assertion Attribute* entry to use an uppercase G.

    3.  Save your changes.





<a name="task_zfb_phc_gzb__result_rfb_2yb_55b"/>

## Results

You have established the trust relationship with the Identity Authentication and are able to use the SAP Task Center showing the tasks of a process. If your instances of SAP Advanced Financial Closing and SAP Task Center are in different subaccounts, you must forward the identity of the user from one subaccount to the other. See the next section *Set Up Principal Propagation Between Subaccounts*.

The next step for the integration is [Connect SAP Build Process Automation and SAP Task Center](https://help.sap.com/docs/TASK_CENTER/08cbda59b4954e93abb2ec85f1db399d/e1e1dce7e52249f78370e5b05d3bce88.html).

**Related Information**  


[Global User ID in Integration Scenarios](https://help.sap.com/docs/SAP_CLOUD_IDENTITY/b95c3d5bab324a3a8409eee5267a5b75/a04611df60404a248a7a8089c85b9761.html?version=Cloud)

[Usage of User UUID](https://help.sap.com/docs/SAP_CLOUD_IDENTITY/b95c3d5bab324a3a8409eee5267a5b75/5dcc5a62e1004aa69bc4639646ddd8a8.html?version=Cloud)

<a name="task_uq2_yhc_gzb"/>

<!-- task\_uq2\_yhc\_gzb -->

## Set Up Principal Propagation Between Subaccounts

If your instances of SAP Advanced Financial Closing and SAP Task Center are in different subaccounts, you must forward the identity of the user from the SAP Task Center subaccount to the SAP Advanced Financial Closing subaccount. You then have access to the MyInbox view of the task that's shown in the SAP Task Center UI.



<a name="task_uq2_yhc_gzb__steps_mqf_rlh_wyb"/>

## Procedure

1.  Execute the *Assemble IdP Metadata for Subaccount 1* and *Establish Trust between Subaccount 1 and Subaccount 2* steps of [User Propagation Between Cloud Foundry Applications](https://help.sap.com/docs/CP_CONNECTIVITY/cca91383641e40ffbe03bdc78f00f681/8ebf60c82a8e4cfc904f441c0c0acd6b.html?locale=en-US), where subaccount 1 is for SAP Task Center and subaccount 2 is for SAP Advanced Financial Closing.

2.  To assign users permissions so they can perform actions in task, choose one of the following options.

    -   Assign role collections to users and user groups, see [Assigning Role Collections to Users or User Groups](https://help.sap.com/docs/btp/sap-business-technology-platform/assigning-role-collections-to-users-or-user-groups).

        > ### Note:  
        > Make sure that the user name value matches the subject name identifier configured in the identity provider. For example, if the subject name identifier is email, then the user name must be the user's email address, see also [Create Users](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/a3bc7e863ac54c23ab856863b681c9f8.html) and [Configure the Subject Name Identifier Sent to the Application](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/1d020e3a3ba34c43a71fde70bfa6419a.html).

    -   Assign role collections to business users, see [Mapping Role Collections in the Subaccount](https://help.sap.com/docs/btp/sap-business-technology-platform/mapping-role-collections-in-subaccount).

        > ### Note:  
        > Make sure that you also map the role collections to the trust configuration from step one.



<a name="task_gwx_f3c_gzb"/>

<!-- task\_gwx\_f3c\_gzb -->

## Resolve Users Recipients

As recipients of approvals or forms, SAP Advanced Financial Closing supports global user IDs, user IDs, login names, and email addresses. The default setting is user UUIDs.



<a name="task_gwx_f3c_gzb__prereq_y1b_tls_vvb"/>

## Prerequisites

-   If your instances of SAP Advanced Financial Closing and SAP Task Center are in different subaccounts, you must create a destination named `Identity_Authentication_Connectivity_IDS` manually in your SAP Advanced Financial Closing subaccount. See [Identity Directory Connectivity](https://help.sap.com/docs/TASK_CENTER/08cbda59b4954e93abb2ec85f1db399d/3dcfba91f69942b29bd924f75bf51c10.html?version=Cloud).

-   The system administrator used for the `Identity_Authentication_Connectivity_IDS` destination must have authorization to read and export users \(*Read Users*\). See [Add System as Administrator \(step 5\)](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/bbbdbdd3899942ce874f3aae9ba9e21d.html?version=Cloud#loiocefb742a36754b18bbe5c3503ac6d87c).




<a name="task_gwx_f3c_gzb__steps_hvj_xkh_wyb"/>

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




<a name="task_gwx_f3c_gzb__postreq_pjy_33x_pzb"/>

## Next Steps

After you've performed the steps described on this page, continue with the next steps described in the [SAP Task Center documentation](https://help.sap.com/docs/task-center/sap-task-center/connect-afc-and-sap-task-center).

