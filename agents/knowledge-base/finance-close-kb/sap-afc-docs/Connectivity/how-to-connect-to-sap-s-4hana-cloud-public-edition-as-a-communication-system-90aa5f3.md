<!-- loio90aa5f3dd1124a54b8bd33ba5b5868bd -->

# How to Connect to SAP S/4HANA Cloud Public Edition as a Communication System

Connect your financial Cloud system to SAP Advanced Financial Closing.



<a name="loio90aa5f3dd1124a54b8bd33ba5b5868bd__prereq_lrk_shn_sjb"/>

## Prerequisites

-   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_SystemAdmin`

    -   `AFC_SpecifySystemsApp`


    For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   The SAP S/4HANA Cloud Public Edition system administrator needs to have completed the set-up instructions. For more information, see [Setting Up Financial Task List Management Integration \(4HG\)](https://support.sap.com/content/dam/SAAP/Sol_Pack/S4C/Library/Setup/4HG_Set-Up_EN_XX.pdf).


-   The destination in the SAP BTP cockpit has already been created as described under [How to Create the Destination in the SAP BTP Cockpit](how-to-create-the-destination-in-the-sap-btp-cockpit-6e94409.md).


> ### Tip:  
> Instead of connecting a communication system manually to SAP Advanced Financial Closing as described below, you can also use the *Set Up SAP Advanced Financial Closing* booster in the SAP BTP cockpit. This is the preferred way to connect a system of type SAP S/4HANA Cloud Public Edition. Keep in mind that notification settings as described below aren't covered by the booster.
> 
> For more information about the booster, see [Automated Setup for Production Tenant](../Automated-Setup/automated-setup-for-production-tenant-08b5486.md#loio08b54863254c43fda04b0726814e5506).



<a name="loio90aa5f3dd1124a54b8bd33ba5b5868bd__steps_bwt_shn_sjb"/>

## Procedure

1.  In SAP Advanced Financial Closing, go to the *Specify Communication Systems* app.

2.  Choose *Create* \> *Create ABAP System* in the table toolbar.

3.  Enter the following information:


    <table>
    <tr>
    <th valign="top">

    Field
    
    </th>
    <th valign="top">

    Description
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    *Name*
    
    </td>
    <td valign="top">
    
    Enter a name for the communication system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Name of Destination Configuration*
    
    </td>
    <td valign="top">
    
    Enter the name of the destination configuration that was configured in the SAP BTP cockpit.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *UI Domain*
    
    </td>
    <td valign="top">
    
    Enter the domain of the SAP Fiori launchpad gateway of your target communication system via which users can access the app UI.

    To get this domain, open the SAP Fiori launchpad of your communication system, copy only the domain, and paste it in the *UI Domain* field.

    > ### Example:  
    > Given the complete URL is as follows:
    > 
    > `https://mylaunchpad.mycompany.corp/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-language=en&sap-client=230#Shell-home/`
    > 
    > Then the UI domain is as follows: `https://mylaunchpad.mycompany.corp`

    The UI domain is therefore the first part of the URL of the communication system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *UI Endpoint* \(mandatory for communication systems that have an SAP Fiori launchpad\)
    
    </td>
    <td valign="top">
    
    Enter the UI endpoint for the SAP Fiori launchpad of your communication system.

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

    The UI endpoint is later added to the URL of the communication system after the UI domain.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *UI Parameters* \(optional\)
    
    </td>
    <td valign="top">
    
    Enter the UI parameters that are to be applied for the connection with the communication system.

    > ### Example:  
    > Given the complete URL is as follows:
    > 
    > `https://mylaunchpad.mycompany.corp/sap/bc/ui5_ui5/ui2/ushell/shells/abap/FioriLaunchpad.html?sap-client=230#Shell-home/`
    > 
    > Then the UI parameter is as follows: `sap-client=230`

    Enter only the parameters in the format shown in the example without any additional characters. If you want to add more than one parameter, add an ampersand \(&\) between them.

    The UI parameters are later added to the URL of the communication system after the UI endpoint.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Is Production System*
    
    </td>
    <td valign="top">
    
    Decide whether the communication system you want to connect to is a test system or a production system. `Yes` indicates that the communication system contains production data, which thereby makes all related task lists potentially relevant to auditing and data retention.

    The default value is `Yes`.

    > ### Note:  
    > Define a communication system as a production system to prevent the untimely deletion of related task lists. Mark communication systems as test systems only if they do not contain audit- or retention-relevant data. However, use this setting to allow enhanced testing capabilities for your non-production systems.
    > 
    > Ensure that you set this indicator correctly, since the information will be displayed in the task list header information in the *Manage Closing Task Lists* app.
    > 
    > We do not recommend changing the *Is Production System* indicator for a system after it has already been in use. Existing task lists will not be reclassified.


    
    </td>
    </tr>
    </table>
    
    > ### Tip:  
    > For systems that have an SAP Fiori launchpad, you can check whether the UI domain, UI endpoint, and possibly UI parameters are correct and lead to the correct URL. Go to the *Monitor Communication Systems* app and choose *Check UI Settings* for the corresponding system. If the settings are correct, you're directed to the SAP Fiori launchpad of your communication system.

    > ### Tip:  
    > You can check whether the connection with the communication system works as expected. Choose *Check Connection*. This will check whether the back-end connection works and whether the system communicates as expected.

4.  Save.

    > ### Tip:  
    > You can check whether the connection you set up works:
    > 
    > 1.  After the first synchronization, go to the *Manage Closing Task Lists* app.
    > 
    >     > ### Note:  
    >     > For access to this app, your user must have a role collection assigned that includes the role template `AFC_Define`.
    > 
    > 2.  Create a template.
    > 
    > 3.  After you've provided the mandatory information and created the template, choose *Closing Structure*.
    > 
    > 4.  Under *Communication System*, enter the corresponding system.
    > 
    > 5.  Open the value help for the *Ledger* or *Factory Calendar ID* field.
    > 
    >     **Results**:
    > 
    >     -   If entries are displayed, the connection works. Exit the value help and choose *Cancel* to cancel template creation.
    > 
    >     -   If no entries are displayed, the connection doesn't work properly. Perform the steps described for issues with the connection to the communication system under [Error Handling](../Monitoring-and-Troubleshooting/error-handling-e5eb3d8.md).

5.  Under *Notifications*, you can set up notifications about system errors. Follow the steps described under [How to Set Up Notifications About Communication System Errors](../System-Monitoring/how-to-set-up-notifications-about-communication-system-errors-835b2a2.md).

6.  Under *Migration*, you can maintain the migration system name. This is only relevant if you're migrating your data from SAP Advanced Financial Closing as part of SAP S/4HANA Cloud Public Edition.

    For more information about the migration, refer to the [Migration Guide (Process Deprecated)](https://help.sap.com/viewer/c67f40b6823f4b33ad8abe58303db75b/SHIP/en-US/025204e29f8b43b282099d44470de1fc.html "Get an overview of what this migration guide covers.") :arrow_upper_right:.




<a name="loio90aa5f3dd1124a54b8bd33ba5b5868bd__result_er4_5c5_plb"/>

## Results

During daily synchronization between the communication system and SAP Advanced Financial Closing, your business configuration data and master data are synchronized. For more information about the synchronization and validation of data, see [Synchronization of Communication Systems](synchronization-of-communication-systems-a86348d.md).



<a name="loio90aa5f3dd1124a54b8bd33ba5b5868bd__postreq_xh1_4bq_jpb"/>

## Next Steps

You have two options for the initial data synchronization with the communication system:

1.  **Daily synchronization:**

    SAP Advanced Financial Closing checks automatically for changes in the connected communication system once every day, except if synchronization has been paused due to connection issues. For more information, see [Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md).

    > ### Recommendation:  
    > Ensure that you always have the latest support package \(SP\) installed on your communication system. If this is not the case, synchronization may only take place every seven days instead of daily.

2.  **Immediate synchronization:**

    Trigger immediate synchronization using the *Synchronize Now* option in the *Monitor Communication Systems* app. If you don't use this option, the communication system will still be synchronized during **daily synchronization**.

    > ### Tip:  
    > You can use the *Monitor System Status* button to navigate directly to the *Monitor Communication Systems* app.


> ### Note:  
> Synchronization always uses the active state of the communication system entry in SAP Advanced Financial Closing. This means that any unsaved changes aren't considered and synchronization is performed based on the state last saved.

**Parent topic:**[SAP S/4HANA Cloud Public Edition](sap-s-4hana-cloud-public-edition-60448a7.md "Connect to your financial cloud system to retrieve information about organizational units, the factory calendar, and so on.")

**Next:**[How to Create the Destination in the SAP BTP Cockpit](how-to-create-the-destination-in-the-sap-btp-cockpit-6e94409.md "Create a destination for your SAP S/4HANA Cloud Public Edition system in your SAP BTP cockpit.")

