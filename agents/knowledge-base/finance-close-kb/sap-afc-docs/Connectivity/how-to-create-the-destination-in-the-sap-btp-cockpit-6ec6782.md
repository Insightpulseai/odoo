<!-- loio6ec67822497649dcaed61baf476fe3aa -->

# How to Create the Destination in the SAP BTP Cockpit

Create a destination for your SAP ERP system in your SAP BTP cockpit.



<a name="loio6ec67822497649dcaed61baf476fe3aa__prereq_vp4_h2b_5qb"/>

## Prerequisites

-   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).

-   To connect to your SAP ERP system, you need to have installed and configured the Cloud Connector. For more information, see [How to Install and Configure the Cloud Connector](how-to-install-and-configure-the-cloud-connector-3d19a8a.md).

-   To connect to your SAP ERP system, you require the SAP ERP connector for SAP Advanced Financial Closing. For more information, see [How to Set Up the SAP ERP Connector](how-to-set-up-the-sap-erp-connector-b139d1e.md).

-   The SAP ERP system administrator needs to have provided you with the following information:

    -   Back-end URL for the communication system

    -   The technical communication user with the authorization objects mentioned in the SAP ERP connector for SAP Advanced Financial Closing documentation. For more information, see [Security Considerations](https://help.sap.com/docs/SAP_ERP_CONNECTOR_FOR_ADVANCED_FINANCIAL_CLOSING/c56f7dab0ed341afad9581be5651184f/c552f0649acd42a7bb8638359ca82897.html).





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

    -   For the proxy type *OnPremise*: <code>http://www.example.com:[port number]<b>/sap/fccx?sap-client</b>=[client]</code>

    -   For the proxy type *Internet*: <code>https://www.example.com:[port number]<b>/sap/fccx?sap-client</b>=[client]</code>


    The highlighted parts are the same for all corresponding SAP ERP systems.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Proxy Type*
    
    </td>
    <td valign="top">
    
    `OnPremise` or `Internet`
    
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
    
    Technical user or other authenticated user
    
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
    



<a name="loio6ec67822497649dcaed61baf476fe3aa__result_ctp_s2b_5qb"/>

## Results

You have now created a destination for your SAP ERP system.

**Parent topic:**[SAP ERP](sap-erp-7b85121.md "Perform the following steps to connect SAP Advanced Financial Closing to your SAP ERP system. Perform the last step only if it applies to your use case.")

**Next:**[How to Install and Configure the Cloud Connector](how-to-install-and-configure-the-cloud-connector-3d19a8a.md "If you want to connect to SAP ERP, you need to install and configure the Cloud Connector as additional software.")

**Previous:**[How to Connect to SAP ERP as a Communication System](how-to-connect-to-sap-erp-as-a-communication-system-e11be48.md "Connect to your SAP ERP system to retrieve information about organizational units, the factory calendar, and so on.")

