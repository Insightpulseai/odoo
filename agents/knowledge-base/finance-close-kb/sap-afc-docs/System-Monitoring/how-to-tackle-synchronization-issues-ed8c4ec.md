<!-- loioed8c4ec6d9834416903a98e51f0728ec -->

# How to Tackle Synchronization Issues

Check the synchronization status of your communication system and tackle any issues.



<a name="loioed8c4ec6d9834416903a98e51f0728ec__prereq_qkg_2yt_ytb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_MonitorSystemsApp`

    -   `AFC_SystemAdmin`


-   Additionally, your user must have a role collection assigned that includes the role template `Business_Process_Specialist_BL_AccessAll`.


For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

The synchronization check follows the frequency and rules as described under [Synchronization of Communication Systems](../Connectivity/synchronization-of-communication-systems-a86348d.md).

> ### Remember:  
> If the connection check doesn't show any successful result for three hours, the following processes are deactivated until the connection check is successful again:
> 
> -   Synchronization of master data
> 
> -   Scheduling of *Job* tasks



## Procedure

1.  Open the *Monitor Communication Systems* app.

2.  From the table, open the system details of a communication system.

3.  In the *Status* section, check the *Synchronization* tile for more details:


    <table>
    <tr>
    <th valign="top">

    Field
    
    </th>
    <th valign="top">

    Description
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    *Status*
    
    </td>
    <td valign="top">
    
    Shows the status of the synchronization. The status you see was set either after the last synchronization run was attempted or due to connection issues. The following statuses are possible:

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



    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Last Checked On*
    
    </td>
    <td valign="top">
    
    Shows the date and time of the last attempt to perform a synchronization run, independently of whether the run was successful or not.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Last Successful Run*
    
    </td>
    <td valign="top">
    
    Shows the date and time of the last successful run.
    
    </td>
    </tr>
    </table>
    
4.  For more information about passed synchronization runs, choose *Show Logs* on the *Synchronization* tile. This brings you to an overview of the logs created for the passed synchronization runs.

    > ### Tip:  
    > For more information about the synchronization logs provided by SAP Advanced Financial Closing, see [Synchronization Business Logs](synchronization-business-logs-0619d52.md).

    1.  If no issues were detected during the last synchronization, no further action is required.

    2.  If issues were detected that need to be resolved before a new synchronization can start, solve the issues in the corresponding location.


5.  For more details about a specific synchronization run, open the details from the overview. You have two options to do this:

    1.  Click somewhere on the specific entry. This brings you to an overview of **all messages** that were logged during this specific synchronization run.

    2.  Click a specific entry in one of the message category columns. This brings you to an overview of all **messages of this category** that were logged during this specific synchronization run.

        > ### Example:  
        > For the last synchronization run, eight messages of the category *Warning* and 32 messages of the category *Success* were logged. You click on the number *8* shown in the *Warning* column. This opens an overview table listing only the eight warning entries.


6.  If a new synchronization is required, you can start it manually by choosing *Synchronize Now* on the *Synchronization* tile, or you can wait for the next scheduled synchronization to run.

    1.  If this synchronization is successful, no further action is required.

    2.  If the synchronization still fails, repeat the previous steps to find the issues and solve them.

        As soon as the issues are fixed, you can start a new synchronization run.





<a name="loioed8c4ec6d9834416903a98e51f0728ec__result_wtb_wb5_ytb"/>

## Results

You have now checked the synchronization status of your communication system and tackled any issues.

-   **[Synchronization Business Logs](synchronization-business-logs-0619d52.md "Get an overview of synchronization logs and possible solutions.")**  
Get an overview of synchronization logs and possible solutions.

