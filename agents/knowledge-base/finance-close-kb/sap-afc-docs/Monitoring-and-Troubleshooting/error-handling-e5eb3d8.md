<!-- loioe5eb3d828cca43fcae562532a43c7bbd -->

# Error Handling

See how to handle issues.



## Context

Depending on what kind of issue you're facing, you need to perform different steps. You can find more details below.



<a name="loioe5eb3d828cca43fcae562532a43c7bbd__steps-unordered_wsz_pk4_ybc"/>

## Procedure

-   Issues with the connection to the communication system:

    The communication issue can have different reasons. Perform the following steps:

    1.  Check that the settings in the *Specify Communication Systems* app are correct.

        1.  Check that the information entered for the communication system is correct.

        2.  Check that the URL information is correct. For systems that have an SAP Fiori launchpad, you can use the *Check UI Settings* function for this. This function is available on the details page for each communication system.

        3.  Now check that the connection to the destination works. You can use the *Check Connection* function for this. This function is available on the overview page and on the details page for each communication system.


    2.  Check that the destination settings in the SAP BTP cockpit are correct. Additionally, check that the system can be reached. You do this by checking the system availability using the corresponding option in the *Actions* column.

    3.  For systems using the Cloud Connector, check that the settings in the Cloud Connector are correct. Additionally, check that the system can be reached from the Cloud Connector. You do this by checking the system availability using the corresponding option in the *Actions* column.

    4.  For SAP ERP systems, check that the settings in the SAP ERP connector for SAP Advanced Financial Closing are correct.

    5.  Check that the synchronization run between SAP Advanced Financial Closing and the communication system was successful. You can find this information in the *Monitor Business Logs* app in SAP Advanced Financial Closing.

    6.  If the settings are correct and the synchronization was successful, but the data isn't displayed in SAP Advanced Financial Closing, for example in the *Manage Closing Task Lists* app, please go to the [SAP Support Portal](https://support.sap.com) and create an incident under the component `FIN-FIO-FCC`.


-   Issues when connecting to your on-premise communication system with the Cloud Connector:

    Please follow the instructions on how to connect to an on-premise communication system under [Connectivity](../Connectivity/connectivity-200deae.md) and the underlying topics.

-   Issues when configuring destinations:

    Please follow the instructions under [Connectivity](../Connectivity/connectivity-200deae.md) and the underlying topics. If you still can't solve the issue, create an incident under the component `FIN-FIO-FCC` in the [SAP Support Portal](https://support.sap.com).

-   Issues when using theme customization features:

    For more information, see [Monitoring and Troubleshooting](https://help.sap.com/docs/btp/ui-theme-designer/monitoring-and-troubleshooting).

-   For all other issues not mentioned here, create an incident under the component `FIN-FIO-FCC` in the [SAP Support Portal](https://support.sap.com).


**Related Information**  


[Communication System Unavailable - No Restore Required](../Connectivity/communication-system-unavailable-no-restore-required-727d2ee.md "Understand how SAP Advanced Financial Closing behaves if a communication system is unavailable.")

[Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md "You use the Monitor Communication Systems app to check the status of your connected communication systems and tackle any issues.")

