<!-- loio1fdf114d6f3541c6bbbb04af32151130 -->

# How to Upgrade from an SAP ERP System to SAP S/4HANA

If you have already used SAP Advanced Financial Closing in connection with your SAP ERP system, you can upgrade from SAP ERP to SAP S/4HANA as your financial communication system and retrieve information about organizational units, the factory calendar, and so on.



<a name="loio1fdf114d6f3541c6bbbb04af32151130__prereq_efw_syq_4lb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_SpecifySystemsApp`


    For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You need to have installed and configured the Cloud Connector. For more information, see [How to Install and Configure the Cloud Connector](how-to-install-and-configure-the-cloud-connector-4cf0fb0.md).

-   The SAP S/4HANA system administrator needs to have enabled OData services in SAP S/4HANA, see [How to Enable OData Services in SAP S/4HANA](how-to-enable-odata-services-in-sap-s-4hana-fb5fe06.md).

-   The SAP S/4HANA system administrator needs to have provided you with the technical communication user that was created as described under [How to Create a Technical Communication User](how-to-create-a-technical-communication-user-c4a9b51.md), and the corresponding password.

-   The SAP S/4HANA system administrator needs to have provided you with the back-end URL for the communication system.




## Procedure

1.  Update the destination in your SAP BTP cockpit: Under *URL* in the destination configuration, enter the back-end URL of the communication system that you've received from the SAP S/4HANA system administrator.

2.  In SAP Advanced Financial Closing, go to the *Specify Communication Systems* app.

3.  Update the *UI Domain*:

    Enter the domain of the SAP Fiori launchpad gateway of your target communication system via which users can access the app UI.

    To get this domain, open the SAP Fiori launchpad of your communication system, copy only the domain, and paste it in the *UI Domain* field.

    > ### Example:  
    > Given the complete URL is as follows:
    > 
    > `https://mylaunchpad.mycompany.corp/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-language=en&sap-client=230#Shell-home/`
    > 
    > Then the UI domain is as follows: `https://mylaunchpad.mycompany.corp`

4.  Update the *UI Endpoint* \(mandatory for communication systems that have an SAP Fiori launchpad\):

    > ### Example:  
    > Given the complete URL is as follows:
    > 
    > `https://mylaunchpad.mycompany.corp/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-language=en&sap-client=230#Shell-home/`
    > 
    > Then the UI endpoint is as follows:`/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html`

    > ### Note:  
    > The default entry is `/sap/bc/ui2/flp`.
    > 
    > You can overwrite this entry. However, consider the following formatting rules:
    > 
    > -   Entry has to start with /
    > 
    > -   Entry can't end with /

5.  **Optional:** Update the *UI Parameters*:

    Enter the UI parameters that are to be applied for the connection with the communication system.

    > ### Example:  
    > Given the complete URL is as follows:
    > 
    > `https://mylaunchpad.mycompany.corp/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-client=230#Shell-home/`
    > 
    > Then the UI parameter is as follows: `sap-client=230`

6.  Save.

    > ### Tip:  
    > For systems that have an SAP Fiori launchpad , you can check whether the UI domain, UI endpoint, and possibly UI parameters are correct and lead to the correct URL. Choose *Check UI Settings*. If the settings are correct, you're directed to the SAP Fiori launchpad of your communication system.


**Parent topic:**[SAP S/4HANA](sap-s-4hana-15a3a5b.md "Perform the following steps to connect SAP Advanced Financial Closing to your SAP S/4HANA system. Perform the last two steps only if they apply to your use case.")

**Next:**[How to Connect to SAP S/4HANA as a Communication System](how-to-connect-to-sap-s-4hana-as-a-communication-system-34ec755.md "Connect to SAP S/4HANA as your financial communication system to retrieve information about organizational units, the factory calendar, and so on.")

**Previous:**[How to Configure Local Settings in Communication Systems](how-to-configure-local-settings-in-communication-systems-a3b374a.md "Configure your local settings for better use with SAP Advanced Financial Closing.")

