<!-- loiof38da7582fc1431ca231cec92c662c5e -->

# Archiving Message Results in Connected Communication Systems Using `AFC_MSG`

Archive message results relating to SAP Advanced Financial Closing.

You can use archiving object `AFC_MSG` to archive message results in SAP Advanced Financial Closing, such as application logs, job logs, and internal messages.

> ### Note:  
> Data archiving is available for on-premise systems only.

**Tables**

`AFC_MSG` archives data from several tables. To check which tables these are, call up transaction `SARA`, enter the archiving object, and choose *Database Tables*. You can display the relevant tables in the lower part of the screen.



## Prerequisites

The following prerequisite must be fulfilled before a message result relating to SAP Advanced Financial Closing can be archived:

The residence time is fulfilled.

> ### Note:  
> You define the residence time as described under [Performing an Application-Specific Configuration](archiving-spool-results-in-connected-communication-systems-using-afc-objstr-b6e6eb2.md#loiob6e6eb25710a4c97b935a69a9bb35ad6__section_afc_performing_app-specific_config) on this page.



## ILM-Related Information for the Archiving Object

You can use this archiving object with the ILM object of the same name, `AFC_MSG`, as part of SAP Information Lifecycle Management. In transaction `IRMPOL`, you can create policies for residence or retention rules, depending on the available policy category. Here you can also see the available time references and which condition fields exist \(described here below\), and decide which of them shall be used in which order to define your rule structure.

The following condition fields are available:

-   `BUKRS` \(company code\)

The following time references are available:

-   Creation date


For more information, see [SAP Information Lifecycle Management](https://help.sap.com/docs/BS_CA/7ce8e5dc89d7407e8baa9de7b775f31f/7fe188e04fdd462e8ec330bb80efc389.html?locale=en-US).



### Data Destruction

Only message results that originate from task executions that are already **marked for deletion** can be selected for data destruction. Data destruction is based on the retention time you define in your communication system as described under [Data Controller Rule Framework](https://help.sap.com/docs/BS_CA/7ce8e5dc89d7407e8baa9de7b775f31f/4a236b5ed814479495fcfc8cd2fa22cd.html?locale=en-US).

For more information about data destruction, see [Destroying Data in a Live Application System](https://help.sap.com/docs/BS_CA/7ce8e5dc89d7407e8baa9de7b775f31f/90a0446ddd874aaf8b683f77cb3ede8a.html?locale=en-US).

> ### Remember:  
> For more information about how to mark objects for deletion, see [How to Delete Task List Templates and Task Lists](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/2fb877991dcb4baf8379972c96ad4c9a.html "Delete task list templates and task lists.") :arrow_upper_right:.



<a name="loiof38da7582fc1431ca231cec92c662c5e__section_afc_performing_app-specific_config"/>

## Performing an Application-Specific Configuration

Before you can use archiving object `AFC_MSG`, you must first make residence time settings in *Application-Specific Customizing* under *AFC ILM Configuration*:

> ### Note:  
> Alternatively, you can go to transaction `AFC_ILM_MANAGE`.

1.  Create a new entry.
2.  Define the residence key as *Message Residence Days*.
3.  Under *Residence Days*, define the residence time in days, that is, the minimum time that the objects need to remain in the database tables.



## Defining Write Variants

When you schedule the archiving run, you must enter an existing variant or create a new one. You can do so in transaction `SARA`.

A write variant contains the parameters for `AFC_MSG` so that message results can be archived.

SAP delivers the following parameters:

-   *Result Object Type*

    Type of the object that is to be archived.

-   *Business Status*

    Business status of the objects to be archived.




## Displaying Message Results Archived with `AFC_MSG`

Archived objects are archived in the communication system, but they can still be accessed in SAP Advanced Financial Closing in the same way as unarchived objects as long as the files exist in the archive. Once the files are deleted from the archive, they can no longer be accessed in SAP Advanced Financial Closing.

