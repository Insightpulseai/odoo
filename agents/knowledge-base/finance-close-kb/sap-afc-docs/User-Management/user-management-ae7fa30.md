<!-- loioae7fa30ce51d43e3a89f607b3dc6a930 -->

# User Management

Understand how you can manage users and their authorizations in SAP Advanced Financial Closing.

This section describes how to configure user management for your application. As a prerequisite, you have created business users and user groups in your identity provider \(IdP\). SAP ID service is configured as the default IdP, but you can also add your instance of SAP Cloud Identity Services - Identity Authentication or a different IdP.

If you use the Identity Authentication service, you can find more information in the SAP BTP documentation under [Manually Establish Trust and Federation Between UAA and Identity Authentication](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/7c6aa87459764b179aeccadccd4f91f3.html).

If you use a different IdP, you can find more information under[Establish Trust and Federation with UAA Using Any SAML Identity Provider](https://help.sap.com/viewer/65de2977205c403bbc107264b8eccf4b/Cloud/en-US/2ce3938c66d94479848bff3090999027.html).

Users provisioned by the configured IdP are allowed to start the applications that are part of SAP Advanced Financial Closing. User information is automatically synchronized on application start.

Users must have static roles assigned to be able to see the respective SAP Fiori apps in their SAP Fiori launchpad.

The following documents explain how to manage static roles and assign them to users using the SAP BTP cockpit, and how to create users and manage user access in SAP Advanced Financial Closing:

1.  [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md "Define and bundle static roles and assign them to users.")  
Define and bundle static roles and assign them to users.
2.  [How to Manage Users](how-to-manage-users-c338b30.md "Upload new users to SAP Advanced
                                                  Financial Closing and update certain
		user attributes.")  
Upload new users to SAP Advanced Financial Closing and update certain user attributes.
3.  [How to Delete Users](how-to-delete-users-81d47cf.md "Delete users that are no longer required.")  
Delete users that are no longer required.
4.  [User Access Management](user-access-management-d974847.md "You can control and grant access to task list templates, task lists, and tasks in
			SAP Advanced
                                                  Financial Closing. By default,
		users don't have access to these objects.")  
You can control and grant access to task list templates, task lists, and tasks in SAP Advanced Financial Closing. By default, users don't have access to these objects.
5.  [Authorizations Required in the Communication System](authorizations-required-in-the-communication-system-97120d2.md "Find more information about authorizations users need to have in the communication
		system.")  
Find more information about authorizations users need to have in the communication system.

