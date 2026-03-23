<!-- loiod9e09c7bacf542a1902e858a1d091a0d -->

# How to Create a Technical Communication User

Create a technical communication user for your SAP ERP system.



## Context

You need to create a technical communication user with specific authorizations to enable the connection between SAP Advanced Financial Closing and the communication system. The required authorizations can't be granted by assigning the technical communication user to a `SAPALL` profile. Instead, the technical communication user needs to have a specific `PFCG` role assigned as described here.

> ### Caution:  
> The technical communication user needs to have the authorization objects assigned that are listed under [Security Considerations](https://help.sap.com/docs/SAP_ERP_CONNECTOR_FOR_ADVANCED_FINANCIAL_CLOSING/c56f7dab0ed341afad9581be5651184f/c552f0649acd42a7bb8638359ca82897.html).



## Procedure

**Creating the Technical Communication User**

1.  In your communication system, run transaction `SU01` and create a user that will be used for the communication between your back end and SAP Advanced Financial Closing.

2.  Go to the *Logon Data* tab.

    1.  If required for your system setup, provide an alias.

    2.  Under *User Type*, make a selection.

        > ### Recommendation:  
        > It's recommended that you select user type *Dialog* for the purpose of this user.

    3.  Provide a password.

        > ### Remember:  
        > To set the final password, you must first provide an initial password. Then, you log on to the system whereupon you'll be asked to change the password. This will then be the final password.



**Providing the Roles Required for the Technical Communication User**

3.  In your communication system, run transaction `PFCG`.

4.  Enter an ID for the role and choose *Single Role*.

5.  Enter a description and choose *Save*.

6.  In change mode, go to the *Authorizations* tab and choose *Edit*.

7.  Select the role and choose *Edit* \> *Insert Authorization\(s\)* \> *Manual Input*.

8.  Maintain the authorization objects listed under [Security Considerations](https://help.sap.com/docs/SAP_ERP_CONNECTOR_FOR_ADVANCED_FINANCIAL_CLOSING/c56f7dab0ed341afad9581be5651184f/c552f0649acd42a7bb8638359ca82897.html).

9.  When you've added all authorization objects, choose *Generate*.

    > ### Note:  
    > If you later perform any changes to this role, be sure to also choose *User Comparison* on the *User* tab in the role view.

10. Back in the role view, go to the *User* tab and add the technical communication user.

11. Save the role.




<a name="loiod9e09c7bacf542a1902e858a1d091a0d__result_ktt_rxz_4pb"/>

## Results

You have now created a technical communication user that can be used to connect your communication system to SAP Advanced Financial Closing.



<a name="loiod9e09c7bacf542a1902e858a1d091a0d__postreq_n4n_hqz_4pb"/>

## Next Steps

Provide your BTP account administrator for SAP Advanced Financial Closing with the information for the technical communication user.

**Parent topic:**[SAP ERP](sap-erp-7b85121.md "Perform the following steps to connect SAP Advanced Financial Closing to your SAP ERP system. Perform the last step only if it applies to your use case.")

**Next:**[How to Set Up the SAP ERP Connector](how-to-set-up-the-sap-erp-connector-b139d1e.md "If you want to connect to SAP ERP, you require the SAP ERP connector for SAP Advanced Financial Closing as additional software.")

**Previous:**[How to Install and Configure the Cloud Connector](how-to-install-and-configure-the-cloud-connector-3d19a8a.md "If you want to connect to SAP ERP, you need to install and configure the Cloud Connector as additional software.")

