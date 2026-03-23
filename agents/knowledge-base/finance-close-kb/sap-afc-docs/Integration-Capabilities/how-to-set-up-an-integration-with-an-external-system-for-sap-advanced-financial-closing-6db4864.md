<!-- loio6db4864a10d5462389172902c0b441e5 -->

# How to Set Up an Integration with an External System for SAP Advanced Financial Closing

Set up an integration with an external system to use SAP Advanced Financial Closing to trigger closing activities in that external system.



<a name="loio6db4864a10d5462389172902c0b441e5__prereq_esn_w1g_cfc"/>

## Prerequisites

-   You're already using the corresponding external system for some of your closing activities.
-   For the steps to be performed with regards to or in your external system, you need to have the required authorization.
-   For the steps to be performed in SAP Advanced Financial Closing, the following authorizations are required:
    -   Your user must have a role collection assigned that includes one of the following role templates:

        -   `AFC_SystemAdmin`

        -   `AFC_SpecifySystemsApp`


        For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).





## Context

Some of your closing activities may be performed in an external system, not using the built-in functions of SAP Advanced Financial Closing. You can set up an integration between your external system and SAP Advanced Financial Closing to use SAP Advanced Financial Closing to trigger these closing activities. After processing, the status of the closing activities in the external system is then reported back to SAP Advanced Financial Closing. This way, you can fully integrate closing activities into your financial close and use SAP Advanced Financial Closing to trigger them automatically and receive results, and apply an approval process.

> ### Caution:  
> Result attachments from external systems are **referenced** by SAP Advanced Financial Closing, but they are not stored in SAP Advanced Financial Closing. The external system owns the data and must ensure file security.



## Procedure

**Implementing the Scheduling Provider Interface**

> ### Note:  
> You have two options to implement the scheduling provider interface, either based on an SDK or from scratch.

1.  Implement the scheduling provider interface using the SDK for out-of-the-box implementation:

    1.  Use the open source software development kit \(SDK\) for SAP Cloud Application Programming Model `Node.js` and SAP Cloud Application Programming Model `Java`. This SDK has been provided to facilitate the implementation of the scheduling provider interface for SAP Advanced Financial Closing.

        Find the required information and the SDK on GitHub under [SAP Advanced Financial Closing SDK for CDS](https://github.com/cap-js-community/sap-afc-sdk).

        > ### Tip:  
        > Find more information about SAP Cloud Application Programming Model under [SAP Cloud Application Programming Model](https://cap.cloud.sap/docs/).


2.  Implement the scheduling provider interface from scratch using a technology stack of your choosing:

    1.  Use the intuitive OpenAPI specification provided to implement the scheduling provider interface in your external system.

        Find the specifications and all the required information under [SAP Advanced Financial Closing Scheduling Provider Interface](https://api.sap.com/api/SSPIV1/overview) in the SAP Business Accelerator Hub.

        Developing an app based on these specifications will expose a Public Rest API which allows for the integration with SAP Advanced Financial Closing.



**Creating Closing Activities in the External System**

3.  If not done yet, create jobs in your external system that you want to include into your financial close managed in SAP Advanced Financial Closing. For information on how to do this, follow the corresponding processes for the external system.


**Setting up a communication system in SAP Advanced Financial Closing**

4.  Set up a communication system for your external system as described under [External Systems](../Connectivity/external-systems-9ca3083.md) in the *Connectivity* section of this guide.




<a name="loio6db4864a10d5462389172902c0b441e5__result_r2l_qxr_zcc"/>

## Results

You have now finished the preparation to use an integration between SAP Advanced Financial Closing and you external system.

