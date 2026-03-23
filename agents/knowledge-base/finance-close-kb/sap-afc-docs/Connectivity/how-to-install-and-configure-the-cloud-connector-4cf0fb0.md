<!-- loio4cf0fb0cded846719506ef4ade1e4e2f -->

# How to Install and Configure the Cloud Connector

If you want to connect to SAP S/4HANA, you need to install and configure the Cloud Connector as **additional software**.



## Context

The Cloud Connector serves as a link between SAP BTP applications and on-premise systems.



<a name="loio4cf0fb0cded846719506ef4ade1e4e2f__steps_kvd_3xr_1pb"/>

## Procedure

1.  Install the Cloud Connector following the relevant procedure for your operating system as described under [Cloud Connector Installation](https://help.sap.com/docs/CP_CONNECTIVITY/cca91383641e40ffbe03bdc78f00f681/57ae3d62f63440f7952e57bfcef948d3.html?&locale=en-US).

2.  Perform the initial configuration steps described under [Initial Configuration](https://help.sap.com/viewer/cca91383641e40ffbe03bdc78f00f681/Cloud/en-US/db9170a7d97610148537d5a84bf79ba2.html).

    > ### Note:  
    > You can't use port 443 as virtual host for your destination.

3.  Connect your subaccounts to the Cloud Connector as described under [Managing Subaccounts](https://help.sap.com/docs/CP_CONNECTIVITY/cca91383641e40ffbe03bdc78f00f681/f16df12fab9f4fe1b8a4122f0fd54b6e.html?&locale=en-US).

    If needed, you can find information about how to use more than one system with the Cloud Connector under [Set Up an HTTP Destination](https://help.sap.com/docs/connectivity/sap-btp-connectivity-cf/create-http-destinations).

    > ### Remember:  
    > You can't use port 443 as virtual host for your destination.




<a name="loio4cf0fb0cded846719506ef4ade1e4e2f__result_egy_vtr_1pb"/>

## Results

You have now installed and configured the Cloud Connector.

**Parent topic:**[SAP S/4HANA](sap-s-4hana-15a3a5b.md "Perform the following steps to connect SAP Advanced Financial Closing to your SAP S/4HANA system. Perform the last two steps only if they apply to your use case.")

**Next:**[How to Enable OData Services in SAP S/4HANA](how-to-enable-odata-services-in-sap-s-4hana-fb5fe06.md "Enable OData services to be able to connect SAP S/4HANA to SAP Advanced Financial Closing.")

**Previous:**[How to Create a Technical Communication User](how-to-create-a-technical-communication-user-c4a9b51.md "Create a technical communication user for your SAP S/4HANA system.")

