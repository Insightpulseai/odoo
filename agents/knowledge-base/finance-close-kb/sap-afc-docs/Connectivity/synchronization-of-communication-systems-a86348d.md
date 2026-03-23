<!-- loioa86348d6459a4c929ec1f389e38827ad -->

# Synchronization of Communication Systems

Get an overview of the synchronization and validation of data.



<a name="loioa86348d6459a4c929ec1f389e38827ad__section_j5c_zsw_b5b"/>

## Context

As soon as you connect a communication system to SAP Advanced Financial Closing, regular synchronization ensures that the data in SAP Advanced Financial Closing is always up to date. During the synchronization, the data is also validated so that no inconsistent data is synchronized. These two aspects are addressed here.



<a name="loioa86348d6459a4c929ec1f389e38827ad__section_mgl_1tw_b5b"/>

## Synchronization

Synchronization between the communication system and SAP Advanced Financial Closing involves two sets of data: business configuration data and master data. It always covers both sets of data. Accordingly, if an error in one set causes synchronization to fail, synchronization fails for both data sets.

![Animated GIF depicting synchronization between SAP Advanced Financial Closing and the communication system: On the one hand, you have the communication system with its business configuration data and master data. On the other hand, you have SAP Advanced Financial Closing with business configuration data and master data that has already been received from the communication system. These two sets of data are synchronized during synchronization. During this process, business logs are created for both data sets. The logs consist of success, warning, and error messages. If error messages are created in the business logs during synchronization, they cause synchronization to fail for both data sets.](images/GIF_System_Synchronization_in_AFC_7caefb4.gif)



### Data Scope for Synchronization

The following data in the connected system is synchronized with SAP Advanced Financial Closing:


<table>
<tr>
<th valign="top" align="center">

Business Configuration

</th>
<th valign="top" align="center">

Master Data

</th>
</tr>
<tr>
<td valign="top">

Task model types

</td>
<td valign="top">

Accounting principles

</td>
</tr>
<tr>
<td valign="top">

Task list models

> ### Note:  
> Task list model changes in the communication system are applied to task list models only, **not** to task list templates or task lists that the model has been assigned to.



</td>
<td valign="top">

Factory calendars

> ### Note:  
> Synchronization considers only factory calendars from two years before until four years after the current year. Previously synchronized factory calendars aren't deleted from existing task lists, but they might no longer be available for new assignment.
> 
> For example, let's assume you ran your first synchronization in 2020. If you then check the synchronization results for 2023, you'll see that the synchronization covers the years 2021 until 2027. The factory calendars for 2020, however, are no longer synchronized and you might therefore no longer be able to assign them to your task lists.



</td>
</tr>
<tr>
<td valign="top">

Folder models

</td>
<td valign="top">

Fiscal year variants

</td>
</tr>
<tr>
<td valign="top">

Task models

</td>
<td valign="top">

Ledgers \(only if assigned to company codes\)

</td>
</tr>
<tr>
<td valign="top">

Task dependencies

</td>
<td valign="top">

Organizational units \(only if they aren't templates\)

</td>
</tr>
<tr>
<td valign="top">

Assignment of tasks to country/region

</td>
<td valign="top">

Parameters

</td>
</tr>
<tr>
<td valign="top">

Assignments of tasks to folder

</td>
<td valign="top">

Task parameters

</td>
</tr>
</table>

> ### Note:  
> Only consistent data is synchronized. If data is deleted in your communication system, it will be set to *orphaned* in SAP Advanced Financial Closing with the next synchronization. This means that the orphaned data can't be used for new task list templates or task lists and their referenced objects.
> 
> If necessary, check the business logs for more information as described under [Logging](../Monitoring-and-Troubleshooting/logging-57375b8.md).
> 
> If data in the communication system is maintained in a language that is not supported by SAP Advanced Financial Closing, English is used instead. For more information about the languages supported by the user interface of SAP Advanced Financial Closing, see [Language Scope](../Overview/language-scope-4f635b9.md).



### Synchronization Statuses

The synchronization run can result in the following statuses:

-   *Completed*

    This status is set if the synchronization was completed without errors or warnings.

-   *In Process*

    This status is set if the synchronization is currently ongoing.

-   *Completed with Warnings*

    This status is set if the synchronization was completed, but warnings exist. Warnings are available in the synchronization logs.

-   *Error*

    This status is set if the synchronization failed.

-   *Paused*

    This status is set if a connection issue persists.

-   *Open*

    This status is set only if there has not yet been an attempt to run a synchronization. This is usually the case for new systems that were connected.


For more information about the synchronization logs provided by SAP Advanced Financial Closing, see [Synchronization Business Logs](synchronization-business-logs-c4a31b9.md).



<a name="loioa86348d6459a4c929ec1f389e38827ad__section_ekz_klc_sxb"/>

## Daily and Immediate Synchronization

To synchronize data \(for example, if you have changes in your communication system\), you have two options:

1.  **Daily synchronization:**

    SAP Advanced Financial Closing checks automatically for changes in the connected communication system once every day, except if synchronization has been paused due to connection issues. For more information, see [Monitor Communication Systems](../System-Monitoring/monitor-communication-systems-a215069.md).

    > ### Recommendation:  
    > Ensure that you always have the latest support package \(SP\) installed on your communication system. If this is not the case, synchronization may only take place every seven days instead of daily.

2.  **Immediate synchronization:**

    Trigger immediate synchronization using the *Synchronize Now* option in the *Monitor Communication Systems* app. If you don't use this option, the communication system will still be synchronized during **daily synchronization**.

    > ### Tip:  
    > You can use the *Monitor System Status* button to navigate directly to the *Monitor Communication Systems* app.


> ### Note:  
> Synchronization always uses the active state of the communication system entry in SAP Advanced Financial Closing. This means that any unsaved changes aren't considered and synchronization is performed based on the state last saved.



<a name="loioa86348d6459a4c929ec1f389e38827ad__section_elr_nlc_sxb"/>

## Validation

The data that is synchronized is always validated to avoid any inconsistencies in SAP Advanced Financial Closing. The data is validated with regard to the following aspects:

-   Structure

-   Data consistency

-   Data references

    > ### Example:  
    > To synchronize an entity from the *Task Parameter Definition* table, the entity *Parameter Type Value* has to be available if it's referenced in the *Task Parameter Definition* table.


The synchronization results can be accessed in the *Monitor Business Logs* app. They're grouped into the following severity categories:

> ### Note:  
> In the case of failing synchronizations, check the business logs before opening a ticket. The logs may already reveal the source of the issue.
> 
> Business logs are automatically deleted after 30 days.

**Business Log Messages**


<table>
<tr>
<th valign="top">

Severity Category

</th>
<th valign="top">

Description

</th>
<th valign="top">

Example

</th>
</tr>
<tr>
<td valign="top" rowspan="2">

*Success*

</td>
<td valign="top">

Data was synchronized successfully.

You also find information about the number of entities that were updated or added.

</td>
<td valign="top">

-   A new entity maintained in the communication system was synchronized.

-   An entity that was updated in the communication system was synchronized.




</td>
</tr>
<tr>
<td valign="top">

Entities that were synchronized before no longer exist in the communication system. They're mentioned as orphaned entities.

> ### Note:  
> Orphaned entities can still be used in existing task list templates and task lists that already reference them. However, they can't be added to any task list template or task list as of the moment they were marked as orphaned.



</td>
<td valign="top">

 

</td>
</tr>
<tr>
<td valign="top">

*Warning*

</td>
<td valign="top">

An issue was found with the affected entities.

Synchronization of the remaining data continues.

</td>
<td valign="top">

-   *Task Country Assignment* table:

    Incomplete table rows on ABAP side

-   A mandatory field or a key field is empty.

-   Entered value doesn't have the correct format, for example, a number is entered in a text field.

-   It is not possible to map the semantic code from ABAP.




</td>
</tr>
<tr>
<td valign="top">

*Error*

</td>
<td valign="top">

An issue was found with the affected entities.

Synchronization of the remaining data **cannot** continue and synchronization consequently fails.

</td>
<td valign="top">

 

</td>
</tr>
</table>

> ### Tip:  
> For more information plus possible recommendations and solutions, see [Synchronization Business Logs](synchronization-business-logs-c4a31b9.md).

-   **[Synchronization Business Logs](synchronization-business-logs-c4a31b9.md "Get an overview of synchronization logs and possible solutions.")**  
Get an overview of synchronization logs and possible solutions.

