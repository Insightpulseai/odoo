<!-- loio9633df8ab1dd4b80ba6ce9b1ed237133 -->

# How to Create the Destination in the SAP BTP Cockpit

Create a destination in your SAP BTP cockpit for an integration with SAP Accounting Automation by BlackLine.



<a name="loio9633df8ab1dd4b80ba6ce9b1ed237133__prereq_bx5_mfb_5qb"/>

## Prerequisites

-   **SAP Advanced Financial Closing:**
    -   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).

-   **SAP Accounting Automation by BlackLine:**

    -   You have set up BlackLine Studio360.
    -   For the settings in SAP BTP cockpit, you need the following information from your system in BlackLine:
        -   Technical access for the BlackLine system
        -   Client ID
        -   User
        -   Token service URL
        -   System URL
        -   Password


    For more information about BlackLine Studio360, see the following pages:

    -   [BlackLine documentation \(sign-in to BlackLine required\)](https://docs.blackline.com/bundle/blackline/page/blackline-accounting-studio/blackline-accounting-studio.html)
    -   [User assistance content for BlackLine solutions for Finance](https://help.sap.com/docs/SAP_ACCOUNT_SUBSTANTIATION_AND_AUTOMATION_BY_BLACKLINE?locale=en-US&version=LATEST)




## Procedure

1.  Open your SAP BTP cockpit.

2.  Create a destination in your SAP BTP cockpit by choosing *Create* \> *From Scratch*.

    For more information about destinations, see [Managing Destinations](https://help.sap.com/docs/CP_CONNECTIVITY/cca91383641e40ffbe03bdc78f00f681/84e45e071c7646c88027fffc6a7bb787.html).

3.  Under *Destination Details*, enter the following information:

    **Main Properties**


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
    
    *Description* \(Optional\)
    
    </td>
    <td valign="top">
    
    Provide a description for this destination.
    
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
    
    *URL*
    
    </td>
    <td valign="top">
    
    URL of the BlackLine `JobScheduling` API.
    
    </td>
    </tr>
    </table>
    
    **Authentication**


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
    
    *Authentication*
    
    </td>
    <td valign="top">
    
    `OAuth2Password`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Client ID*
    
    </td>
    <td valign="top">
    
    Client ID as defined in your BlackLine system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Use mTLS for token retrieval*
    
    </td>
    <td valign="top">
    
    Do not select this checkbox.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Client Secret*
    
    </td>
    <td valign="top">
    
    Client secret as generated in your BlackLine system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Token Service URL*
    
    </td>
    <td valign="top">
    
    Token service URL of your BlackLine system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *User*
    
    </td>
    <td valign="top">
    
    Technical user for your BlackLine system.

    Please ensure that the user in authorized for API access in your BlackLine system.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Password*
    
    </td>
    <td valign="top">
    
    Password of the selected user.
    
    </td>
    </tr>
    </table>
    
4.  Under *Additional Properties*, choose *Add Property* and provide the following information:


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
    
    *Key*
    
    </td>
    <td valign="top">
    
    `scope`
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Value*
    
    </td>
    <td valign="top">
    
    `bl.workflow instance_[Instance ID]`

    The instance ID is provided by BlackLine.
    
    </td>
    </tr>
    </table>
    



<a name="loio9633df8ab1dd4b80ba6ce9b1ed237133__result_jlm_sfb_5qb"/>

## Results

You have now created a destination for your BlackLine system.

**Parent topic:**[SAP Accounting Automation by BlackLine](sap-accounting-automation-by-blackline-ce92690.md "Perform the following steps to connect SAP Advanced Financial Closing to SAP Accounting Automation by BlackLine.")

**Previous:**[How to Connect to a BlackLine System as a Communication System](how-to-connect-to-a-blackline-system-as-a-communication-system-7b790c6.md "Connect to SAP Accounting Automation by BlackLine to include BlackLine processes in your financial close in SAP Advanced Financial Closing.")

