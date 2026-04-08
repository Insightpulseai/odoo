<!-- loiod3b1cbe50ca246f8b2c03e92b42a6b5b -->

# How to Create Technical Communication Users \(Separate Gateway and Business Back Ends\)

Create technical communication users for your separate gateway and business back ends.



<a name="loiod3b1cbe50ca246f8b2c03e92b42a6b5b__context_dsc_2vv_gsb"/>

## Context

If you use separate systems for the gateway back end and the business back end, you need to create two technical communication users - one for each system - with specific authorizations to enable the connection between SAP Advanced Financial Closing and the communication system. The required authorizations can't be granted by assigning the technical communication user to a `SAPALL` profile. Instead, the technical communication user needs to have a specific `PFCG` role assigned as described here.

> ### Caution:  
> If you use separate systems for the gateway back end and the business back end, the users created for both systems **must be dialog users**. These users require authorization object `S_RFCACL`. Depending on your release, this object is provided with the default authorization *SAP Gateway Business Suite Enablement - Service*.



<a name="loiod3b1cbe50ca246f8b2c03e92b42a6b5b__steps_eq4_2vv_gsb"/>

## Procedure

**Creating the Technical Communication User for a Business Back End**

1.  In your business back end, run transaction `SU01` and create a user that will be used for the communication between your business back end and SAP Advanced Financial Closing.

2.  Go to the *Logon Data* tab.

    1.  You may need to provide an alias depending your system.

    2.  Under *User Type*, select *Dialog*.

    3.  Provide a password.

        > ### Remember:  
        > To set the final password, you may first need to provide an initial password. Then, you log on to the system whereupon you'll be asked to change the password. This will then be the final password.



**Providing the Roles Required for the Technical Communication User**

3.  Run transaction `PFCG`.

4.  Enter an ID for the role and choose *Single Role*.

5.  Enter a description and choose *Save*.

6.  In change mode, go to the *Menu* tab and choose *Insert*.

7.  Go to *Edit* \> *Insert Authorization Default*.

8.  Under *Default Authorization*, select `SAP Gateway Business Suite Enablement - Service`.

    The following information is filled automatically:


    <table>
    <tr>
    <th valign="top">

    Program ID
    
    </th>
    <th valign="top">

    Object Type
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    `R3TR`
    
    </td>
    <td valign="top">
    
    `IWSV`
    
    </td>
    </tr>
    </table>
    
    1.  Under *TADIR Service*, use the value help to search for `FCCX_COMMUNICATION_SERVICES_SRV 0001`, and apply this service.

    2.  Choose *Copy*.

    3.  For this last authorization, the *OP Variant* needs to have been selected on the *Applications* tab if this is supported by your release:


        <table>
        <tr>
        <th valign="top">

        Active
        
        </th>
        <th valign="top">

        Type
        
        </th>
        <th valign="top">

        Name
        
        </th>
        <th valign="top">

        Variant
        
        </th>
        <th valign="top">

        Description
        
        </th>
        </tr>
        <tr>
        <td valign="top">
        
        `Selected`
        
        </td>
        <td valign="top">
        
        SAP Gateway Business Suite Enablement - Service
        
        </td>
        <td valign="top">
        
        `FCCX_COMMUNICATION_SERVICES_SRV 0001`
        
        </td>
        <td valign="top">
        
        `FCCX_COMMUNICATION_SERVICES_SRVO`
        
        </td>
        <td valign="top">
        
        `OP Variant`
        
        </td>
        </tr>
        </table>
        
    4.  The following authorization objects need to be maintained:


        <table>
        <tr>
        <th valign="top">

        Authorization Object
        
        </th>
        <th valign="top">

        Field Name \(Heading\)
        
        </th>
        <th valign="top">

        Value
        
        </th>
        </tr>
        <tr>
        <td valign="top" rowspan="2">
        
        `S_BTCH_NA1`
        
        </td>
        <td valign="top">
        
        `PROGRAM`
        
        </td>
        <td valign="top">
        
        `FCCX_APJ_PROCESSOR`
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `BTCUNAME`: *Background User Name for Authorization Check*
        
        </td>
        <td valign="top">
        
        Enter one of the following:

        -   `*`: Using the asterisk, you ensure that you don't have to list all relevant users explicitly.

        -   List all relevant business users explicitly.



        
        </td>
        </tr>
        <tr>
        <td valign="top" rowspan="2">
        
        `S_BTCH_JOB`
        
        </td>
        <td valign="top">
        
        `JOBACTION`
        
        </td>
        <td valign="top">
        
        -   `DELE`: Delete Background Jobs

        -   `RELE`: Release Jobs



        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `JOBGROUP`
        
        </td>
        <td valign="top">
        
        `*` \(asterisk\)
        
        </td>
        </tr>
        <tr>
        <td valign="top" rowspan="3">
        
        `S_APPL_LOG`
        
        </td>
        <td valign="top">
        
        `ACTVT`
        
        </td>
        <td valign="top">
        
        Automatically prefilled: `03`
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `ALG_OBJECT`
        
        </td>
        <td valign="top">
        
        `*` \(asterisk\)
        
        </td>
        </tr>
        <tr>
        <td valign="top">
        
        `ALG_SUBOBJ`
        
        </td>
        <td valign="top">
        
        `*` \(asterisk\)
        
        </td>
        </tr>
        </table>
        

9.  On the *User* tab, add the technical communication user.

    > ### Caution:  
    > If you use separate systems for the gateway back end and the business back end, the users created for both systems **must be dialog users**. These users require authorization object `S_RFCACL`. Depending on your release, this object is provided with the default authorization *SAP Gateway Business Suite Enablement - Service*.

    > ### Recommendation:  
    > We do **not** recommend adding any alternative or additional profiles to the technical communication user.

10. Save the role.


**Creating the Technical Communication User for a Gateway Back End**

11. In your gateway back end, run transaction `SU01` and create a user that will be used for the communication between your gateway back end and SAP Advanced Financial Closing.

12. Go to the *Logon Data* tab.

    1.  If required for your system setup, provide an alias.

    2.  Under *User Type*, select *Dialog*.

    3.  Provide the same password as that used for the technical communication user in your business back end.

        > ### Remember:  
        > To set the final password, you may first need to provide an initial password. Then, you log on to the system whereupon you'll be asked to change the password. This will then be the final password.



**Providing the Roles Required for the Technical Communication User**

13. Run transaction `PFCG`.

14. Enter an ID for the role and choose *Single Role*.

15. Enter a description and choose *Save*.

16. In change mode, go to the *Menu* tab. If you use separate systems for the gateway back end and the business back end, choose *Insert*.

17. Go to *Edit* \> *Insert Authorization Default*.

18. Under *Default Authorization*, select `SAP Gateway: Service Group Metadata`.

    The following information is filled automatically:


    <table>
    <tr>
    <th valign="top">

    Program ID
    
    </th>
    <th valign="top">

    Object Type
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    `R3TR`
    
    </td>
    <td valign="top">
    
    `IWSG`
    
    </td>
    </tr>
    </table>
    
    1.  Under *TADIR Service*, use the value help to search for the technical service name that was used during service activation as described under [How to Enable OData Services in SAP S/4HANA](how-to-enable-odata-services-in-sap-s-4hana-fb5fe06.md). For example, the default **`[ZFCCX_COMMUNICATION_SERVICES_SRV]*`**.


19. On the *User* tab, add the technical communication user.

    > ### Caution:  
    > If you use separate systems for the gateway back end and the business back end, the users created for both systems **must be dialog users**. These users require authorization object `S_RFCACL`. Depending on your release, this object is provided with the default authorization *SAP Gateway Business Suite Enablement - Service*.

    > ### Tip:  
    > We do not recommend adding any alternative or additional profiles to the technical communication user.

20. Save the role.




<a name="loiod3b1cbe50ca246f8b2c03e92b42a6b5b__result_qh4_xvv_gsb"/>

## Results

You have now created technical communication users that can be used to connect your communication system to SAP Advanced Financial Closing.



<a name="loiod3b1cbe50ca246f8b2c03e92b42a6b5b__postreq_ygx_xvv_gsb"/>

## Next Steps

Provide your BTP account administrator for SAP Advanced Financial Closing with the information for the technical communication users.

