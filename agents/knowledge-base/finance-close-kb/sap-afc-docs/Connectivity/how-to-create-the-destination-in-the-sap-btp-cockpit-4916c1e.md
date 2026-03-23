<!-- loio4916c1ea4a654ee9baf076f0d4e7cb52 -->

# How to Create the Destination in the SAP BTP Cockpit

Create a destination for your external system in your SAP BTP cockpit.



<a name="loio4916c1ea4a654ee9baf076f0d4e7cb52__prereq_bx5_mfb_5qb"/>

## Prerequisites

-   You have already completed the onboarding process as described under [Onboarding](../Onboarding/onboarding-1987953.md).




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
    
    Enter the back-end URL of the external communication system. The back-end URL has to have the following format:

    <code><b>&lt;URL_OF_EXTERNAL_SYSTEM&gt;</b>/api/job-scheduling/v1</code>

    Replace the highlighted part **<URL\_OF\_EXTERNAL\_SYSTEM\>** \(including the brackets\) with the URL of your communication system.
    
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
    
    Choose the authentication type of your communication system.

    > ### Note:  
    > `NO_AUTH` **is not** supported.


    
    </td>
    </tr>
    </table>
    



<a name="loio4916c1ea4a654ee9baf076f0d4e7cb52__result_jlm_sfb_5qb"/>

## Results

You have now created a destination for your external system.

**Parent topic:**[External Systems](external-systems-9ca3083.md "Connect to your external financial system to retrieve information about organizational units, the factory calendar, and so on.")

**Previous:**[How to Connect to a External System as a Communication System](how-to-connect-to-a-external-system-as-a-communication-system-ea13039.md "Connect to your external system to retrieve information about organizational units, the factory calendar, and so on.")

