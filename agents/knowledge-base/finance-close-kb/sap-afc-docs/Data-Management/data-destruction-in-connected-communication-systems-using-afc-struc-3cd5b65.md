<!-- loio3cd5b65e2d9d4262a270d9e01abb1e73 -->

# Data Destruction in Connected Communication Systems Using `AFC_STRUC`

Data destruction of task executions relating to SAP Advanced Financial Closing.

You can use the data destruction object `AFC_STRUC` for destroying data in the connected communication system that relates to SAP Advanced Financial Closing. This data destruction object is assigned to the ILM object of the same name: `AFC_STRUC`.



<a name="loio3cd5b65e2d9d4262a270d9e01abb1e73__section_shn_5nc_wcb"/>

## Prerequisites

The following prerequisites need to be fulfilled before a data relating to SAP Advanced Financial Closing can be destroyed:

-   Data is marked for deletion

    > ### Remember:  
    > For more information about how to mark objects for deletion, see [How to Delete Task List Templates and Task Lists](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/2fb877991dcb4baf8379972c96ad4c9a.html "Delete task list templates and task lists.") :arrow_upper_right:.

-   Your communication system needs to fulfill the requirements for archiving and ILM and data destruction as specified under [System-Dependent Feature Availability](../Connectivity/system-dependent-feature-availability-0465d8f.md).



<a name="loio3cd5b65e2d9d4262a270d9e01abb1e73__section_ehz_5rk_bcc"/>

## More Information



### SAP S/4HANA Cloud Public Edition

For more information, see:

-   [ILM Audit Areas](https://help.sap.com/docs/SAP_S4HANA_CLOUD/a630d57fc5004c6383e7a81efee7a8bb/3789a4256f1248219cf6c84e49e1e046.html)
-   [ILM Policies](https://help.sap.com/docs/SAP_S4HANA_CLOUD/a630d57fc5004c6383e7a81efee7a8bb/14a1b8ef5ee84741a499e12589206cbb.html)



### SAP S/4HANA and SAP S/4HANA Cloud Private Edition

For more information, see:

-   [Processing Audit Areas](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/19e0786c9fc347b1bc7d0c0ae03e70d4.html)
-   [Editing ILM Policies](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/f4e6642b7f5542d8a7b7c7a037cba46f.html)
-   [Editing Retention Rules](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/aa983758d2724969aa82eda43f79cd6b.html)



### SAP Business Suite

For more information, see:

-   [Processing Audit Areas](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/19e0786c9fc347b1bc7d0c0ae03e70d4.html)
-   [Editing ILM Policies](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/f4e6642b7f5542d8a7b7c7a037cba46f.html)
-   [Editing Retention Rules](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/aa983758d2724969aa82eda43f79cd6b.html)



<a name="loio3cd5b65e2d9d4262a270d9e01abb1e73__section_vhn_5nc_wcb"/>

## ILM-Based Information for the Data Destruction Object

> ### Note:  
> For more information about information lifecycle management, see:
> 
> -   For SAP S/4HANA Cloud Public Edition: [Information Lifecycle Management](https://help.sap.com/docs/SAP_S4HANA_CLOUD/a630d57fc5004c6383e7a81efee7a8bb/3c9d33dde6154f71863f994262a584fd.html)
> -   For SAP S/4HANA and SAP S/4HANA Cloud Private Edition: [SAP Information Lifecycle Management](https://help.sap.com/docs/SAP_S4HANA_ON-PREMISE/35d6f7d8cbd04dbf997ca36785c7a795/7fe188e04fdd462e8ec330bb80efc389.html)
> -   For SAP Business Suite: [SAP Information Lifecycle Management](https://help.sap.com/docs/BS_CA/7ce8e5dc89d7407e8baa9de7b775f31f/7fe188e04fdd462e8ec330bb80efc389.html)

You create policies and rules for the related ILM object of this data destruction object.

The following fields for the ILM object are defined in the ILM policy and are visible when creating or processing the *ILM Policies*:

-   Available *Time References*

    -   `CREATION_DATE` \(creation date of the task execution\)


-   Available *Condition Fields*

    -   `BUKRS`\(company code\)



