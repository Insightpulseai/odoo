<!-- loio13dbd046610847ca9726dbd23c8af5b7 -->

# Technical Prerequisites

Before you start to use SAP Advanced Financial Closing, check the requirements and recommendations in this section.

> ### Note:  
> The software and services listed here are not part of the functional scope of SAP Advanced Financial Closing and must be licensed separately.



<a name="loio13dbd046610847ca9726dbd23c8af5b7__section_itr_24d_kjb"/>

## Additional Software



### Financial Communication System

You need to connect SAP Advanced Financial Closing to one of these financial communication systems:

-   SAP S/4HANA Cloud Public Edition

-   SAP S/4HANA Cloud Private Edition

-   SAP S/4HANA

-   SAP ERP


For more information about system-specific requirements, see [Connectivity](../Connectivity/connectivity-200deae.md).



### SAP ERP Connector

To be able to connect to SAP ERP, you require the SAP ERP connector for SAP Advanced Financial Closing.

For more information about the connector, such as how to get the connector and activate the service, see [SAP ERP connector for SAP Advanced Financial Closing](https://help.sap.com/docs/SAP_ERP_CONNECTOR_FOR_ADVANCED_FINANCIAL_CLOSING).



### Cloud Connector

If you want to connect your application to an on-premise system, you must have installed and configured the Cloud Connector. For more information, see [Cloud Connector](https://help.sap.com/viewer/cca91383641e40ffbe03bdc78f00f681/Cloud/en-US/e6c7616abb5710148cfcf3e75d96d596.html).



<a name="loio13dbd046610847ca9726dbd23c8af5b7__section_gzz_1pd_kjb"/>

## Additional Services



### Identity Provider \(IdP\)

You require an identity provider to create business users and user groups. You can use the following options:

-   SAP Cloud Identity Services - Identity Authentication:

    -   You can leverage the capabilities of SAP Cloud Identity Services - Identity Authentication. For more information, see [SAP Cloud Identity Services - Identity Authentication](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/d17a116432d24470930ebea41977a888.html).



-   You can also use your own identity provider. For more information, see [Corporate Identity Providers](https://help.sap.com/docs/IDENTITY_AUTHENTICATION/6d6d63354d1242d185ab4830fc04feb1/19f3eca47db643b6aad448b5dc1075ad.html).

    -   You'll still need SAP Cloud Identity Services - Identity Authentication connected through OIDC \(OpenID Connect\), but you can use your own identity provider as proxy provider behind it.





## Browsers and Browser Settings

This application supports the standard browsers supported by SAP UI5. For more information, see the related chapter in the [SAP UI5 Documentation \(PDF\)](https://help.sap.com/SAPUI5_PDF/SAPUI5.pdf).

-   **[Switch to SAP Cloud Identity Services - Identity Authentication](switch-to-sap-cloud-identity-services-identity-authentication-f3cc8f5.md "SAP Cloud Identity Services
                                                - Identity Authentication is the central
		service for authentication, single sign-on, and user management in SAP cloud
		solutions.")**  
SAP Cloud Identity Services - Identity Authentication is the central service for authentication, single sign-on, and user management in SAP cloud solutions.

