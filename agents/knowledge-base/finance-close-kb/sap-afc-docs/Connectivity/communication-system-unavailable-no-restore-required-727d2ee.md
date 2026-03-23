<!-- loio727d2ee07e364da796a4273ff2f73bb5 -->

# Communication System Unavailable - No Restore Required

Understand how SAP Advanced Financial Closing behaves if a communication system is unavailable.



<a name="loio727d2ee07e364da796a4273ff2f73bb5__section_knm_d3t_qxb"/>

## Context

Since SAP Advanced Financial Closing processes data from connected communication systems, system performance is not only influenced by maintenance windows of SAP Advanced Financial Closing, but also by maintenance windows of the connected systems. The behavior of SAP Advanced Financial Closing is set up to avoid inconsistencies resulting from system unavailability. The sections below describe the effect that maintenance modes of connected communication systems have on activities and functions in SAP Advanced Financial Closing.

The following graphic gives an overview of system behavior:

![Graphic depicting system behavior in the case of unavailability and restored availability of the communication system: If the communication system is unavailable, SAP Advanced Financial Closing can't navigate to apps in the system, schedule jobs in the system, nor synchronize data with the system. If the communication system is available again, SAP Advanced Financial Closing can again navigate to apps in the system, schedule jobs in the system, and synchronize data with the system. At the same time, the communication system sends any task statuses to SAP Advanced Financial Closing that haven't been sent before due to the system being unavailable.](images/Diagram_AFC_Behaviour_If_System_Unavailable_45f6562.png)

> ### Tip:  
> You can monitor the connection status of your communication system using the *Monitor Communication Systems* app. For more information, see [Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md).



<a name="loio727d2ee07e364da796a4273ff2f73bb5__section_exg_43t_qxb"/>

## Navigation to Apps in Connected Systems

From the *Process Closing Tasks* app, you can in general navigate to apps in connected communication systems to process tasks. However, if the corresponding communication system is unavailable, this navigation doesn't work. In this case, you receive the default system message that the affected communication system issues.



<a name="loio727d2ee07e364da796a4273ff2f73bb5__section_ikw_1jt_qxb"/>

## Job Processing

Tasks of type *Job* may already have been started when the communication system becomes unavailable. In this case, either the jobs finish during a cool-down time of the communication system before it reaches maintenance mode or the jobs fail. In both cases, the task status will be communicated to SAP Advanced Financial Closing once the communication system is available again.



### Scheduling

SAP Advanced Financial Closing can schedule jobs to run in connected communication systems. However, if the corresponding communication system is unavailable, the system can no longer schedule new tasks. The affected tasks remain in the scheduling queue and are processed once the connected system is available again. Manual scheduling, however, isn't possible if the connected system isn't available, and it has to be retried in SAP Advanced Financial Closing when the communication system is available again.



<a name="loio727d2ee07e364da796a4273ff2f73bb5__section_rnq_xkt_qxb"/>

## Synchronization

SAP Advanced Financial Closing runs regular synchronizations with the connected communication systems. However, if a communication system is unavailable, these synchronizations don't work. They'll be retried after a certain time. For more information about the handling of synchronization runs, see [Synchronization of Communication Systems](synchronization-of-communication-systems-a86348d.md) and [Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md).

**Related Information**  


[Synchronization of Communication Systems](synchronization-of-communication-systems-a86348d.md "Get an overview of the synchronization and validation of data.")

[Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md "You use the Monitor Communication Systems app to check the status of your connected communication systems and tackle any issues.")

