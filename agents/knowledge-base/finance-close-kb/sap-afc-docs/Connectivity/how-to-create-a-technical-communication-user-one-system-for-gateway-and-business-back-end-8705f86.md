<!-- loio8705f861937c40ca8afb9dc728f4d5fe -->

# How to Create a Technical Communication User \(One System for Gateway and Business Back End\)

Create a technical communication user for your gateway and business back end.



<a name="loio8705f861937c40ca8afb9dc728f4d5fe__context_qkm_myv_gsb"/>

## Context

You need to create a technical communication user with specific authorizations to enable the connection between SAP Advanced Financial Closing and the communication system. The required authorizations can't be granted by assigning the technical communication user to a `SAPALL` profile. Instead, the technical communication user needs to have a specific `PFCG` role assigned as described here.



## Procedure

**Creating the Technical Communication User**

1.  In your gateway and business back end, run transaction `SU01` and create a user that will be used for the communication between your back end and SAP Advanced Financial Closing.

2.  Go to the *Logon Data* tab.

    1.  If required for your system setup, provide an alias.

    2.  Under *User Type*, make a selection.

        > ### Recommendation:  
        > We recommend that you select the user type *Dialog* for the purpose of this user.

    3.  Provide a password.

        > ### Remember:  
        > To set the final password, you may first need to provide an initial password. Then, you log on to the system whereupon you'll be asked to change the password. This will then be the final password.



**Providing the Roles Required for the Technical Communication User**

3.  Run transaction `PFCG`.

4.  Enter an ID for the role and choose *Single Role*.

5.  Enter a description and choose *Save*.

6.  In change mode, go to the *Menu* tab and choose *Insert*.

7.  Go to *Edit* \> *Insert Authorization Default*.

8.  Under *Default Authorization*, select `SAP Gateway: Service Group Metadata`.

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


9.  Under *Default Authorization*, select `SAP Gateway Business Suite Enablement - Service`.

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
        

10. On the *User* tab, add the technical communication user.

    > ### Recommendation:  
    > We do **not** recommend adding any other or additional profiles to the technical communication user.

11. Save the role.




<a name="loio8705f861937c40ca8afb9dc728f4d5fe__result_qnn_rzv_gsb"/>

## Results

You have now created a technical communication user that can be used to connect your communication system to SAP Advanced Financial Closing.



<a name="loio8705f861937c40ca8afb9dc728f4d5fe__postreq_rj1_szv_gsb"/>

## Next Steps

Provide your BTP account administrator for SAP Advanced Financial Closing with the information for the technical communication user.

