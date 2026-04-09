<!-- loiofb5fe06295fd493f80e89df3a9c57b7a -->

# How to Enable OData Services in SAP S/4HANA

Enable OData services to be able to connect SAP S/4HANA to SAP Advanced Financial Closing.



## Context

The administrator of your SAP S/4HANA system needs to perform the following steps to enable OData Services and check the virus scan profile to ensure the connection works.



### What Are OData Services Used For?

The OData services are required for the communication and necessary data flow between SAP Advanced Financial Closing and your SAP S/4HANA communication system.

For more information about the data flow and communication between both systems, see [Data Flow from and to SAP Advanced Financial Closing](../Overview/data-flow-from-and-to-sap-advanced-financial-closing-56103b0.md).



## Procedure

**Enabling OData Services**

1.  In the SAP Reference IMG \(transaction `SPRO`\) of your SAP S/4HANA system, navigate to *SAP NetWeaver* \> *SAP Gateway* \> *OData Channel* \> *Administration* \> *General Settings* \> *Activate and Maintain Services*.

    > ### Tip:  
    > Alternatively, you can run transaction `/n/IWFND/MAINT_SERVICE`.

2.  Choose *Add Service*.

3.  In the *Filter* section, make the following entries and press [Enter\]:

    -   *System Alias*: for example, `LOCAL`

    -   *External Service Name*: `FCCX_COMMUNICATION_SERVICES_SRV`

        > ### Tip:  
        > Search for `*FCCX*` to ensure that you find the external service name.


    > ### Note:  
    > The *System Alias* refers to the RFC Destination that points to the system where your service is running.

4.  Select the service and choose *Add Selected Services*.

5.  On the *Add Service* screen, you can change the technical service name. However, it is recommended that you keep the default setting: **`ZFCCX_COMMUNICATION_SERVICES`**.

6.  On the *Activate and Maintain Services* screen, double-click the service to select it and do the following:

    1.  In the *ICF Nodes* window, choose *Call Browser* to test the service. Please note down the URL.

    2.  Back in the *ICF Nodes* window, choose *ICF Node* \> *Configure \(SICF\)*.

    3.  In the table, navigate to *default\_host* \> *\[namespace\]* \> *opu* \> *odata* \> *sap* and open the underlying *fccx\_communication\_services\_srv* node by double-clicking it.

    4.  On the *Create/Change a Service* screen, navigate to the *Logon Data* tab and define the following settings:

        1.  Under *Procedure*, select *Alternative Logon Procedure* from the dropdown.
        2.  In the *Logon Procedure List* table at the bottom of the screen, remove all entries except for *Basic Authentication*.



**Checking Virus Scan Profile**

7.  In the SAP Reference IMG \(transaction `SPRO`\) of your SAP S/4HANA system, navigate to *SAP NetWeaver* \> *SAP Gateway* \> *OData Channel* \> *Administration* \> *General Settings* \> *Define Virus Scan Profiles*.

8.  Under *V2 Virus Scan Options*, check that a virus scan profile is selected and that the *Virus Scan Switched Off* option is **not** selected.

9.  Open transaction `VSCAN` and check whether a virus scan definition is maintained.

    1.  If none is maintained, maintain a definition.

        For more information, see [Setting Up a Virus Scan Provider \(ABAP\)](https://help.sap.com/docs/ABAP_PLATFORM_NEW/3cd5ac93e7ec4690bd804f0d23fed9da/4df582ed472d41c4e10000000a42189c.html).

    2.  If you can't maintain a definition, go to the virus scan profile as described in the previous steps and select the *Virus Scan Switched Off* option.





<a name="loiofb5fe06295fd493f80e89df3a9c57b7a__postreq_x2m_hgz_mlb"/>

## Next Steps

Provide the system administrator of SAP Advanced Financial Closing with the URL you've just copied when you called up the browser.

**Parent topic:**[SAP S/4HANA](sap-s-4hana-15a3a5b.md "Perform the following steps to connect SAP Advanced Financial Closing to your SAP S/4HANA system. Perform the last two steps only if they apply to your use case.")

**Previous:**[How to Install and Configure the Cloud Connector](how-to-install-and-configure-the-cloud-connector-4cf0fb0.md "If you want to connect to SAP S/4HANA, you need to install and configure the Cloud Connector as additional software.")

