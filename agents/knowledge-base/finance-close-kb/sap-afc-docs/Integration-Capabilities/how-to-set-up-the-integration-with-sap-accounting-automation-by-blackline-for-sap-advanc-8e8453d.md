<!-- loio8e8453d99f9a40ceaeaa66fd0501b833 -->

# How to Set Up the Integration with SAP Accounting Automation by BlackLine for SAP Advanced Financial Closing

Set up an integration with SAP Accounting Automation by BlackLine to use SAP Advanced Financial Closing to trigger BlackLine processes.



<a name="loio8e8453d99f9a40ceaeaa66fd0501b833__prereq_esn_w1g_cfc"/>

## Prerequisites

-   You're already using SAP Accounting Automation by BlackLine for some of your closing activities.
-   For the steps to be performed with regards to or in your BlackLine system, you need to have the required authorization.
-   For the steps to be performed in SAP Advanced Financial Closing, the following authorizations are required:
    -   Your user must have a role collection assigned that includes one of the following role templates:

        -   `AFC_SystemAdmin`

        -   `AFC_SpecifySystemsApp`


        For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).





## Context

Some of your closing activities may be performed with SAP Accounting Automation by BlackLine. You can set up an integration between SAP Accounting Automation by BlackLine and SAP Advanced Financial Closing to use SAP Advanced Financial Closing to trigger these closing activities. After processing, the status of the BlackLine processes is then reported back to SAP Advanced Financial Closing. This way, you can fully integrate processes in BlackLine into your financial close and use SAP Advanced Financial Closing to trigger them automatically and receive results, and apply an approval process.

> ### Caution:  
> Result attachments from external systems are **referenced** by SAP Advanced Financial Closing, but they are not stored in SAP Advanced Financial Closing. The external system owns the data and must ensure file security.



## Procedure

**Setting up a communication system in SAP Advanced Financial Closing**

1.  Set up a communication system for SAP Accounting Automation by BlackLine as described under [SAP Accounting Automation by BlackLine](../Connectivity/sap-accounting-automation-by-blackline-ce92690.md) in the *Connectivity* section of this guide.


**Creating Processes in BlackLine**

2.  If not done yet, create processes in your BlackLine system that you want to include into your financial close managed in SAP Advanced Financial Closing. For information on how to do this, refer to the corresponding documentation about BlackLine.




<a name="loio8e8453d99f9a40ceaeaa66fd0501b833__result_r2l_qxr_zcc"/>

## Results

You have now finished the preparation to use an integration between SAP Advanced Financial Closing and SAP Accounting Automation by BlackLine.

