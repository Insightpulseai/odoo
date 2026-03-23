<!-- loiof3cc8f5f57984faab155b9173802f654 -->

# Switch to SAP Cloud Identity Services - Identity Authentication

SAP Cloud Identity Services - Identity Authentication is the central service for authentication, single sign-on, and user management in SAP cloud solutions.



## Context

Certain future technical innovations, such as possible agentic AI use cases, require a specific infrastructure setup. For such use cases to be available to you, both your SAP Advanced Financial Closing tenant and your identity provider \(IdP\) need to base authentication on SAP Cloud Identity Services - Identity Authentication.

If your current setup involves XSUAA and you want to change to SAP Cloud Identity Services - Identity Authentication for authentication, you can migrate as described below. This process consists of **two discrete migrations**:

-   Migrate your SAP Advanced Financial Closing tenant to SAP Cloud Identity Services - Identity Authentication.

    This migration is **required in any case** if you want your system setup to fulfill the requirements for some future use cases.

-   Migrate your identity provider to SAP Cloud Identity Services - Identity Authentication.

    This migration **may be required**, but only if the initial setup of your identity provider is SAML-based and didn't use the OIDC \(OpenID Connect\) protocol.

    > ### Note:  
    > In the following two cases **no migration of your identity provider** is required:
    > 
    > -   You used the booster in the SAP BTP cockpit to set up SAP Advanced Financial Closing. The booster has completed the setup based on SAP Cloud Identity Services - Identity Authentication using OIDC protocol.
    > -   Even without the booster you implemented your setup with SAP Cloud Identity Services - Identity Authentication from the start and you used OIDC protocol.




<a name="loiof3cc8f5f57984faab155b9173802f654__section_migration_considerations"/>

## Considerations Before Identity Provider Migration

The migration of your identity provider may have some side effects that you need to consider prior to migrating.

> ### Caution:  
> Read and evaluate these considerations thoroughly.



### No Reversal

Once you've migrated your authentication setup to SAP Cloud Identity Services - Identity Authentication, you can't migrate back to your previous setup based on XSUAA.



### Configuration Maintained

When you do the migration you need to ensure that SAP Cloud Identity Services - Identity Authentication uses the same subject name identifier as your current XSUAA-based implementation. If this is not given, new users are created after migration.



### Role Maintenance

Assignments of static roles and role collections in the SAP BTP cockpit are kept during migration if you use the same provider already with OIDC protocol that you used previously as identity provider. If you switch the IdP during migration, you also need to remaintain manually all role and role collection assignments.



### Personalization

User personalization in SAP Advanced Financial Closing, such as saved views, remains intact as long as the IdP isn't switched and the origin key isn't changed during the migration. If the IdP or the origin key changes, users need to remaintain manually any personalization in the system after the migration.

<a name="task_nqy_45z_f3c"/>

<!-- task\_nqy\_45z\_f3c -->

## How to Switch to SAP Cloud Identity Services - Identity Authentication

Request a switch to SAP Cloud Identity Services - Identity Authentication.



## Prerequisites

-   You're an IT expert responsible for the setup of SAP Advanced Financial Closing in your company.

-   You have authorization to edit the settings of your subaccount in the SAP BTP cockpit.

-   If you have an existing SAP BTP subaccount with SAP Cloud Identity Services - Identity Authentication:

    -   If you're using OIDC protocol, then you don't need to do anything.

    -   If you're using Security Assertion Markup Language \(SAML\) protocol, you need to switch to OIDC, as described in the following migration process in [3311563](https://me.sap.com/notes/3311563).


-   If you have a new SAP BTP subaccount, you need to create a trust between SAP Cloud Identity Services - Identity Authentication and SAP BTP.

    For more information, see [Establish Trust and Federation Between SAP Authorization and Trust Management Service and SAP Cloud Identity Services](https://help.sap.com/docs/btp/sap-business-technology-platform/establish-trust-and-federation-between-uaa-and-identity-authentication?version=Cloud).

-   You have **familiarized yourself with and are prepared for the consequences** of this migration as described under [Considerations Before Identity Provider Migration](switch-to-sap-cloud-identity-services-identity-authentication-f3cc8f5.md#loiof3cc8f5f57984faab155b9173802f654__section_migration_considerations) above.

> ### Note:  
> After completing the procedure below of switching from XSUAA to SAP Cloud Identity Services - Identity Authentication, you will have to redo the following configurations because your previous configuration was created for XSUAA:
> 
> -   Identity Authentication application-level configurations \(corporate IdP trust, assertions\).
> 
> -   Mapping of role collections for the given IdP.
> 
> -   Creation of shadow users \(including potential manual mapping of role collections\). You need to do this because all existing mappings/users will be assigned to the old IdP ID \(from XSUAA\).

> ### Note:  
> After you've done the switch to SAP Cloud Identity Services - Identity Authentication, you'll need to add your custom domains to the list of redirect URIs under the OpenID Connect configuration.



## Procedure

**Migration of Identity Provider to SAP Cloud Identity Services - Identity Authentication**

1.  If not done so yet, familiarize yourself with and prepare for the consequences of this migration as described under [Considerations Before Identity Provider Migration](switch-to-sap-cloud-identity-services-identity-authentication-f3cc8f5.md#loiof3cc8f5f57984faab155b9173802f654__section_migration_considerations) above.

    > ### Tip:  
    > Migration happens once per tenant for SAP Advanced Financial Closing. If you're using a test tenant for SAP Advanced Financial Closing, consider migrating this one first to see possible side effects before migrating your production tenant.

2.  In the SAP BTP cockpit, in the subaccount relevant for the tenant to be migrated, go to *Trust Configuration*.

3.  If you don't have an instance for SAP Cloud Identity Services - Identity Authentication as your IdP yet, create one.

    1.  As origin key for this instance, select `sap.custom`.


4.  If you already have an instance for SAP Cloud Identity Services - Identity Authentication as your IdP, check whether the origin key is set as `sap.custom`.

    1.  If the origin key is set as `sap.custom`, you don't need to change anything and can continue with the next step in the procedure described here.

    2.  If the origin key **is not** set as `sap.custom`, you need to change it to `sap.custom`.

        > ### Caution:  
        > If you need to change the origin key, you will need to remaintain all assignments of static roles and role collections. Accordingly, take note of these assignments first.
        > 
        > Additionally, users will need to remaintain manually any personalization in the system, such as personalized views, after the migration is completed.



**Migration of SAP Advanced Financial Closing Tenant to SAP Cloud Identity Services - Identity Authentication**

5.  Once you're all set and you want to start the migration to SAP Cloud Identity Services - Identity Authentication for authentication, create a ticket under the component `FIN-FIO-FCC` requesting the switch.

    For the ticket, use the title `Enable SAP Cloud Identity Services - Identity Authentication`. If you have several tenants SAP Advanced Financial Closing, a test and a production tenant, state clearly for which you're requesting the change.

    **Result:** The switch is made on your behalf for the corresponding tenant. Once migration is complete, you'll be informed about the status.




## Results

You have now switch your authentication method to SAP Cloud Identity Services - Identity Authentication.



## Next Steps

-   Ensure that SAP Cloud Identity Services - Identity Authentication uses the same subject name identifier as your current XSUAA-based implementation. If this is not given, new users are created.
-   If required due to the migration, remaintain user assignments to static roles and role collections, and any personalization.

