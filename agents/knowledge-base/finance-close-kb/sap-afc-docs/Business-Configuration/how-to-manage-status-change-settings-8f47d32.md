<!-- loio8f47d3218f1943c9a0a325e7f6b9d1a5 -->

# How to Manage Status Change Settings

Maintain settings that define whether comments are required for specific task status changes in SAP Advanced Financial Closing.



## Prerequisites

Your user must have a role collection assigned that includes the role template `AFC_StatusChangeConstraintApp`.

For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).



## Context

You can manage settings that define whether or not a comment is required for a task status change. You can do this by defining **general rules** and **specific rules**.



### General Rules

You can create general rules for task types and target statuses by selecting the *All* value for the corresponding field.

If you create a rule with the *All* value selected for both task type and target status, the settings you make in that rule applies to all manual status changes for all task types.



### Specific Rules

You can create specific rules for task types and target statuses by selecting a specific value for the corresponding field.



### Rule Hierarchy

If by logic two rules - a general and a specific one - were to apply to a specific manual status change, the specific rule takes priority over the general rule.

> ### Example:  
> You've created a general rule for all task types that comments are optional for all manual status changes. Additionally, you've created a specific rule that for all task types a comment is mandatory for a manual change to the status *Completed with Errors*.
> 
> A user changes the status of a task of type *SAP Fiori Application* to *Completed with Errors*. The specific rule takes priority over the general rule, which is why a comment is mandatory in this case.



### Default Fallback

If there is a status change that isn't covered by any rule, the default setting applies. The default setting in this case is that a comment is mandatory upon status change.



## Procedure

1.  Open the *Configuration* app.

    The next screen lists all the configuration apps you're allowed to access.

2.  Choose *Status Change Settings* from the list.

    This brings you to the *Manage Status Change Settings* app where you can create rules by task types for each target status.

3.  In the table toolbar, choose *Create* to create a new rule based on a task type.

4.  Under *Task Type*, select the task type for which this rule applies.

    > ### Tip:  
    > You can also select the *All* option, meaning that the same rule will apply for all task types.
    > 
    > Keep in mind, however, that you can maintain one entry with the *All* option and additionally an entry with a specific task type. In this case, the *All* rule will apply to all task types with the defined status change for which no more specific rule exists. If a rule exists for a specific task type for the same target status, that specific rule will apply to a change to the specific target status.

5.  Under *Target Status*, select the target status for which you want to define settings.

    This rule applies to manual status changes only.

    > ### Tip:  
    > You can also select the *All* option, meaning that the same rule will apply for all status changes for this task type.
    > 
    > Keep in mind, however, that you can maintain one entry with the *All* option and additionally an entry with a specific target status for the same task type. In this case, the *All* rule will apply to all status changes for which no specific rule exists for this task type. If a rule exists for the selected task type for a specific target status, that rule will apply to a change to the specific target status.

6.  Under *Comments in Production Systems* and *Comments in Non-Production Systems*, define a status change setting for both cases.

    The following values are possible:


    <table>
    <tr>
    <th valign="top">

    Value
    
    </th>
    <th valign="top">

    Description
    
    </th>
    </tr>
    <tr>
    <td valign="top">
    
    *Mandatory*
    
    </td>
    <td valign="top">
    
    A comment is **required** upon a change to the respective task status.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Optional*
    
    </td>
    <td valign="top">
    
    A comment **may be provided**, but is not required upon a change to the respective task status.
    
    </td>
    </tr>
    <tr>
    <td valign="top">
    
    *Hidden*
    
    </td>
    <td valign="top">
    
    The option to provide a reason, comment, or attachment respectively is hidden in the *Change Status* dialog.
    
    </td>
    </tr>
    </table>
    
7.  To confirm, choose *Create* in the table toolbar.




## Results

You have now maintained settings for status changes based on task type, target status, and system type.

