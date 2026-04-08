<!-- loio7ac9d632b5f9455faca2bfa4e4a240c2 -->

# How to Grant Access by Direct Assignment

Grant access by directly assigning a user to a task list template, task list, or task.



<a name="loio7ac9d632b5f9455faca2bfa4e4a240c2__prereq_sgh_5p2_rrb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes the role template `AFC_Define`.

    For more information about role templates, see [How to Manage Static Role Templates](how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   You must be authorized to perform the following steps through one of the options described under [Task List Creation Scope](task-list-creation-scope-ba4100e.md).

-   You've familiarized yourself with the information under [Direct User Assignment](direct-user-assignment-f96b217.md) to ensure that you're using the right means to grant access.




## Context

You can grant users direct access without assigning them to any user role or authorization group. Accordingly, the access you grant them by direct assignment only applies to the object you assigned them to.



## Procedure

1.  Open the *Manage Closing Task Lists* app and search for the task list template that you want to do an assignment for or that contains a folder or task that you want to do an assignment for.

2.  Navigate to the object for which you want to assign a user or user group by direct assignment.

3.  Select the user or user group in the corresponding field.

    > ### Remember:  
    > Users who are maintained as owners of a task list template or task list or who belong to an assigned owner group have write access to the specific object in the *Manage Closing Task Lists* app.
    > 
    > Users who are maintained as the user responsible for a **folder**, **task list**, or **task**, or who belong to a responsible user group always have write access to the respective object. They don't need to have a user role assigned in addition.
    > 
    > Users who are maintained as the processing user of a **task** or who belong to a processing user group always have access to the respective task. To be able to process the respective task, they don't need to have a user role assigned in addition.

4.  Save your changes.




<a name="loio7ac9d632b5f9455faca2bfa4e4a240c2__result_cyz_gs2_rrb"/>

## Results

You have now granted access by assigning a user or user group directly to an object.

