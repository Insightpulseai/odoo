<!-- copy0619d5229e4d4af0adec147a83355654 -->

# Synchronization Business Logs

Get an overview of synchronization logs and possible solutions.



During the synchronization of the connected communication system with SAP Advanced Financial Closing, different types of message are written and provided in the synchronization logs. The following table provides more information and possible solutions for these messages:

> ### Remember:  
> Business logs are automatically deleted after 30 days.

> ### Note:  
> In the following table, the curly brackets with numbers represent placeholders. In synchronization logs in SAP Advanced Financial Closing, these placeholders are replaced with specific information, such as IDs or names.

****


<table>
<tr>
<th valign="top">

Severity

</th>
<th valign="top">

Text

</th>
<th valign="top">

Recommendation/Solution

</th>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Communication system "\{0\}": Task list model "\{1\}" \("\{2\}"\) contains a cyclic dependency. The following task in folder "\{3\}" is affected: "\{4\}" \("\{5\}"\). This task list model can't be assigned to a task list template.

</td>
<td valign="top">

Change the task and folder definition in the connected communication system. For more information, see [How to Define Task Models](https://help.sap.com/viewer/a32675ceb29149fd9be78a66704da190/SHIP/en-US/0500ad4d75b2417499b503b04048e0f7.html "Define a task model from which you can later create tasks.") :arrow_upper_right:.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Communication system "\{0\}": Program "\{1\}" for task parameter header variant "\{2\}" couldn't be found. Check that the program and a business transaction type for this program exist and that they're used by the task.

</td>
<td valign="top">

Check your definition and maintenance of the task list model content in your communication system. For more information, see [How to Register Programs for Parameter Mapping](https://help.sap.com/viewer/a32675ceb29149fd9be78a66704da190/SHIP/en-US/85b71e19c90f40c59526a80aa70fa2ac.html "Register an ABAP program for parameter mapping.") :arrow_upper_right:.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Request for communication system “\{0\}” exceeded the time limit. Check your ABAP logs.

</td>
<td valign="top">

Check the ABAP logs.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Connectivity service user isn't authorized for connected communication system “\{0\}”. Check if the necessary authorizations have been granted.

</td>
<td valign="top">

Check whether the necessary authorizations have been granted in the ABAP system.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

An error occurred in the connected communication system “\{0\}”. Check your ABAP logs.

</td>
<td valign="top">

Check the ABAP logs.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

The task parameter structure couldn't be converted correctly for the master data synchronization. Please check the task parameter definitions and mappings in your communication system “\{0\}”.

</td>
<td valign="top">

Check the ABAP logs and the corresponding exposed OData endpoint of the ABAP system.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Communication system “\{0\}” doesn't fulfill the technical prerequisites. Check the documentation about technical prerequisites and connectivity.

</td>
<td valign="top">

For more information, see the following pages:

-   [Technical Prerequisites](../Technical-Prerequisites/technical-prerequisites-13dbd04.md)
-   [Connectivity](../Connectivity/connectivity-200deae.md)



</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Unable to read business configuration data from communication system "\{0\}" with destination "\{1\}".

</td>
<td valign="top">

Check your destination configuration in the SAP BTP cockpit. Additionally, check the exposed OData endpoint of your communication system.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Unable to read master data from communication system "\{0\}" with destination "\{1\}".

</td>
<td valign="top">

Check your destination configuration in the SAP BTP cockpit. Additionally, check the exposed OData endpoint of your communication system.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Destination configuration with name "\{0\}" was not found.

</td>
<td valign="top">

Check your destination configuration in the SAP BTP cockpit.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Unable to read gateway features from communication system "\{0\}" with destination "\{1\}".

</td>
<td valign="top">

Check your destination configuration in the SAP BTP cockpit. Additionally, check the exposed OData endpoint of your communication system.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Connection to destination failed. Check destination configuration with name "\{0\}" for communication system "\{1\}" in your SAP BTP Cockpit.

</td>
<td valign="top">

Check your destination configuration in the SAP BTP cockpit.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Synchronization for communication system "\{0\}" failed. The following insertion error occurred for entity "\{1\}": Message: "\{2\}"; Affected field: "\{3\}".

</td>
<td valign="top">

Check further details in the error message or contact your system administrator.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Synchronization for communication system "\{0\}" failed. The update of entity "\{1\}" for record "\{2\}" was not successful.

</td>
<td valign="top">

Check further details in the error message or contact your system administrator.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Synchronization failed due to an empty report metadata response from configured communication system "\{0\}". Check the destination configuration with name "\{1\}" and the connected ABAP system.

</td>
<td valign="top">

Check the destination configuration and the connected ABAP system, and provide the required report metadata. Additionally, check the configuration and system setup and the implementation of SAP Notes and service packs of the system or technical component.

</td>
</tr>
<tr>
<td valign="top">

Error

</td>
<td valign="top">

Synchronization failed due to an empty task parameter registration response from configured communication system "\{0\}". Check the destination configuration with name "\{1\}" and the connected ABAP system.

</td>
<td valign="top">

Check the destination configuration and the connected ABAP system, and maintain the required task parameter registration. Additionally, check the configuration and system setup and the implementation of SAP Notes and service packs of the system or technical component.

</td>
</tr>
<tr>
<td valign="top">

Warning

</td>
<td valign="top">

Synchronization of report metadata and program registration for communication system "\{0\}" needed to restart. This may indicate missing resources in the ABAP system. For safety reasons, a full synchronization was performed.

</td>
<td valign="top">

Contact your system administrator and check the ABAP communication system resources. One reason can be an overloaded system that is not responding fast enough or is unable to save entries in a given time. A possible solution is to increase the system resources \(for example, dialog processes\).

</td>
</tr>
<tr>
<td valign="top">

Warning

</td>
<td valign="top">

Country ISO code "\{0\}" can't be mapped for communication system "\{1\}". Custom country code "ZZZ" is used instead.

</td>
<td valign="top">

This can happen in the following cases:

-   The country/region code used in the communication system is not ISO-code-compliant.
-   Custom countries/regions are defined in the ABAP tables in the communication system.



</td>
</tr>
<tr>
<td valign="top">

Warning

</td>
<td valign="top">

Some ABAP reports couldn't be found for communication system "\{0\}". Please have a look at the documentation under "Synchronization Business Logs" and check your communication system for reports with the following codes: "\{1\}".

</td>
<td valign="top">

Check your communication system for reports with the codes provided in the warning message in SAP Advanced Financial Closing. This warning is issued in several cases such as the following:

-   The reports no longer exist in the communication system.
-   The communication user's authorizations haven't been configured correctly.
-   An upgrade failed resulting in incorrect references.
-   The system is overloaded.



</td>
</tr>
<tr>
<td valign="top">

Information

</td>
<td valign="top">

Synchronization of business configuration was skipped because the content for communication system “\{0\}” was unchanged.

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Information

</td>
<td valign="top">

Synchronization of master data was skipped because the content for communication system “\{0\}” was unchanged.

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Synchronization of business configuration finished with “\{0\}” inserts for entity “\{1\}” for communication system “\{2\}”.

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Synchronization of business configuration finished with "\{0\}" updates for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Synchronization of business configuration texts finished with "\{0\}" inserts for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Synchronization of business configuration texts finished with "\{0\}" updates for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Synchronization of business configuration finished. "\{0\}" entries are orphaned and no longer imported for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Master data synchronization finished with "\{0\}" inserts for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Master data synchronization finished with "\{0\}" updates for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Master data text synchronization finished with "\{0\}" inserts for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Master data text synchronization finished with "\{0\}" updates for entity "\{1\}" for communication system "\{2\}".

</td>
<td valign="top">

No action required

</td>
</tr>
<tr>
<td valign="top">

Success

</td>
<td valign="top">

Synchronization of master data finished. “\{0\}” entries are orphaned and no longer imported for entity “\{1\}” for communication system “\{2\}”.

</td>
<td valign="top">

No action required

</td>
</tr>
</table>

