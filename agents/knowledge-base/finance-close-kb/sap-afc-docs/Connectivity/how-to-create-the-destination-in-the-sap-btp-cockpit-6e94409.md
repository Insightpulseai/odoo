<!-- loio6e944094643a43c48e0230081880ddb0 -->

# How to Create the Destination in the SAP BTP Cockpit

Create a destination for your SAP S/4HANA Cloud Public Edition system in your SAP BTP cockpit.



<a name="loio6e944094643a43c48e0230081880ddb0__prereq_bx5_mfb_5qb"/>

## Prerequisites

-   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).

-   The SAP S/4HANA Cloud Public Edition system administrator needs to have completed the set-up instructions as described under [How to Set Up the Integration of Financial Task List Management](how-to-set-up-the-integration-of-financial-task-list-management-24140e9.md).




## Procedure

1.  Open your SAP BTP cockpit.

2.  Create a destination in your SAP BTP cockpit. For more information, see [Managing Destinations](https://help.sap.com/docs/CP_CONNECTIVITY/cca91383641e40ffbe03bdc78f00f681/84e45e071c7646c88027fffc6a7bb787.html).

    Enter the following information in the destination configuration:


    <table>
    <tr>
    <th valign="top">

    Field
    
    </th>
    <th valign="top">

    What to Enter
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    *Name*
    
    </td>
    <td valign="top">
    
    Specify a name for the destination configuration.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Type*
    
    </td>
    <td valign="top">
    
    `HTTP` 
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *URL*
    
    </td>
    <td valign="top">
    
    Enter the back-end URL of the communication system. Make sure to add the SAP client number at the end of the URL. Accordingly, the back-end URL has to have the following format:

    <code>https://www.example.com:[port number]<b>/sap/opu/odata/sap/fccx_communication_services_srv?sap-client=100</b></code>

    The highlighted part is the same for all SAP S/4HANA Cloud Public Edition systems.

    > ### Tip:  
    > You can also find this information in the communication arrangement you created before as described under [How to Set Up the Integration of Financial Task List Management](how-to-set-up-the-integration-of-financial-task-list-management-24140e9.md). Under *Inbound Services*, copy the URL displayed under *Service URL/Service Interface* and paste it into the destination information in the SAP BTP cockpit. Then add the client information *sap-client=100* at the end \(you may need to add a question mark as separator as shown in the example above\).


    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Proxy Type*
    
    </td>
    <td valign="top">
    
    `Internet`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Authentication*
    
    </td>
    <td valign="top">
    
    `BasicAuthentication`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *User*
    
    </td>
    <td valign="top">
    
    Technical communication user that you've received from the SAP S/4HANA Cloud Public Edition system administrator.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Password*
    
    </td>
    <td valign="top">
    
    Password of the selected user
    
    </td>
    </tr>
    </table>
    



<a name="loio6e944094643a43c48e0230081880ddb0__result_jlm_sfb_5qb"/>

## Results

You have now created a destination for your SAP S/4HANA Cloud Public Edition system.

**Parent topic:**[SAP S/4HANA Cloud Public Edition](sap-s-4hana-cloud-public-edition-60448a7.md "Connect to your financial cloud system to retrieve information about organizational units, the factory calendar, and so on.")

**Next:**[How to Add the Launchpad Tile in SAP S/4HANA Cloud Public Edition](how-to-add-the-launchpad-tile-in-sap-s-4hana-cloud-public-edition-857efd5.md "Add a tile for SAP Advanced Financial Closing to your launchpad in SAP S/4HANA Cloud Public Edition.")

**Previous:**[How to Connect to SAP S/4HANA Cloud Public Edition as a Communication System](how-to-connect-to-sap-s-4hana-cloud-public-edition-as-a-communication-system-90aa5f3.md "Connect your financial Cloud system to SAP Advanced Financial Closing.")

