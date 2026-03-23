<!-- loioa4be7f7ef92d49bcba53be34fcd6f94c -->

# How to Manage General Settings

Maintain settings that apply to all objects in SAP Advanced Financial Closing.



<a name="loioa4be7f7ef92d49bcba53be34fcd6f94c__prereq_y22_qyk_3bc"/>

## Prerequisites

Your user must have a role collection assigned that includes the role template `AFC_GeneralSettings`.

For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

You can manage several general settings that affect the corresponding objects across SAP Advanced Financial Closing, such as archiving settings for task lists.

<a name="task_ttn_bxq_tdc"/>

<!-- task\_ttn\_bxq\_tdc -->

## How to Manage Archiving Times for Task Lists

Maintain archiving settings for production and non-production task lists.



<a name="task_ttn_bxq_tdc__context_p35_fxq_tdc"/>

## Context

In SAP Advanced Financial Closing, generated task lists are archived automatically after a specific **time of inactivity**, independently of their status. The time after which a task list is archived depends on the closing type and on the value set for the *Is Production Task List* indicator. You define this time in the *Manage General Settings* app. The **highest values possible** - which are also the default values delivered by SAP - are defined as follows:




<table>
<tr>
<th valign="top">

Closing Type

</th>
<th valign="top">

Production Task Lists

</th>
<th valign="top">

Non-Production Task Lists

</th>
</tr>
<tr>
<td valign="top">

Month-End Closing

</td>
<td valign="top">

Six months

</td>
<td valign="top">

Three months

</td>
</tr>
<tr>
<td valign="top">

Quarter-End Closing

</td>
<td valign="top">

Nine months

</td>
<td valign="top">

Three months

</td>
</tr>
<tr>
<td valign="top">

Year-End Closing

</td>
<td valign="top">

18 months

</td>
<td valign="top">

Three months

</td>
</tr>
<tr>
<td valign="top">

Special-End Closing

</td>
<td valign="top">

Six months

</td>
<td valign="top">

Three months

</td>
</tr>
</table>

Task lists with status *Obsolete* are archived after one month, independently of the *Is Production Task List* indicator.

Once archived, task lists can be viewed and restored by authorized users. For more information, see [Task List Archiving](../Archiving/task-list-archiving-032bb8e.md).

> ### Note:  
> The archiving settings you make in this app relate to the archiving of task lists in SAP Advanced Financial Closing. They don't cover the archiving settings of objects and data in connected communication systems. For more information about object and data archiving in communication systems, see [Data Archiving in Connected Communication Systems](../Data-Management/data-archiving-in-connected-communication-systems-2829b08.md).



<a name="task_ttn_bxq_tdc__steps_gw1_fxq_tdc"/>

## Procedure

1.  Open the *Manage General Settings* app.

2.  Go to the *General Settings* tab.

3.  In the *Archiving Times by Closing Type* section, choose the *Edit* button.

    > ### Remember:  
    > You define the archiving times based on months of inactivity. This means that you define how long a task list needs to be inactive before it is archived automatically.
    > 
    > To see changes made previously to the settings, you can display the change log within the *Manage General Settings* app.

    1.  Under *Production Task Lists*, define for each closing type the number of months of inactivity before a production task list is archived.

    2.  Under *Non-Production Task Lists*, define for each closing type the number of months of inactivity before a quality task list is archived.


4.  Choose *Save* to confirm your changes.




<a name="task_ttn_bxq_tdc__result_xdy_rhq_ydc"/>

## Results

You have now defined the archiving settings for your task lists. The task lists will now be archived accordingly.

**Related Information**  


[Task List Archiving](../Archiving/task-list-archiving-032bb8e.md "Understand how archiving and restoring in SAP Advanced Financial Closing works.")

[Data Archiving in Connected Communication Systems](../Data-Management/data-archiving-in-connected-communication-systems-2829b08.md "Information about data archiving of objects relating to SAP Advanced Financial Closing.")

<a name="task_jwr_xxq_tdc"/>

<!-- task\_jwr\_xxq\_tdc -->

## How to Manage the Invalidation of Successor Tasks

Decide on how to manage the status and reprocessing of successor tasks.



<a name="task_jwr_xxq_tdc__context_gpm_2yq_tdc"/>

## Context

If you need to manually set the task status *Completed with Errors* for a task that was previously processed successfully, you may want its successor tasks to be invalidated to avoid inconsistencies in your financial close. By activating the invalidation of successor tasks, you can ensure that successor tasks need to be reprocessed as well.

> ### Note:  
> A task is invalidated only if the following holds:
> 
> -   Successor invalidation is activated in the general settings of SAP Advanced Financial Closing.
> -   The task has already reached the status *In Process* or any of its subsequent statuses.
> -   The task is connected to the affected task through process-related dependencies only. If a string of tasks is connected to the affected task through a time-related dependency only, these tasks aren't invalidated.
> 
> For more information about dependency types, see [Dependency Types and Approval Types](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/ed4838015dbd4cf49a4ae5ae74c9207e.html "Learn about the different dependency types and approval types you can define for tasks.") :arrow_upper_right:.

Additionally, you can decide to activate the automated retriggering of invalidated successor tasks **that allow for automated processing**, such as tasks of the types *Job* and *Workflow*. In this case, tasks are retriggered automatically as soon as the task you previously set to *Completed with Errors* manually has been reprocessed successfully.

> ### Note:  
> A task can be retriggered automatically only if the following holds:
> 
> -   All prerequisites, such as the completion and possible approval of predecessor tasks, are fulfilled again.
> -   One of the following start modes is set for the task:
>     -   *Automatically*
>     -   *Automatically When Due*
> 
> -   Before the task was invalidated, it had one of the following statuses:
>     -   *Checked*
>     -   *Completed Without Errors*
>     -   *Completed with Warnings*



<a name="task_jwr_xxq_tdc__steps_rqt_2yq_tdc"/>

## Procedure

1.  Open the *Manage General Settings* app.

2.  Go to the *Successor Invalidation* tab.

3.  Choose the *Edit* button to adjust the settings.

    1.  Under *Production Task Lists*, decide whether you want to activate the following options for production task lists:

        -   *Invalidate Successor Tasks*
        -   *Retrigger Invalidated Tasks Automatically*

    2.  Under *Non-Production Task Lists*, decide whether you want to activate the following options for non-production task lists:

        -   *Invalidate Successor Tasks*
        -   *Retrigger Invalidated Tasks Automatically*


4.  Choose *Save* to confirm your changes.




<a name="task_jwr_xxq_tdc__result_uvf_jzv_ydc"/>

## Results

You have now adjusted the settings on how to handle the invalidation of successor tasks in SAP Advanced Financial Closing.

**Related Information**  


[Task Status and Approval Status](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/b9715e0625734186b3576efaed6e0924.html "Understand the relationship between task status and approval status.") :arrow_upper_right:

