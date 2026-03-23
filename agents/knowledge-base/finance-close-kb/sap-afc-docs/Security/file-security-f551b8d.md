<!-- loiof551b8df53714338b0e869110e7ba51e -->

# File Security

Security measures taken with regard to uploaded files.

SAP Advanced Financial Closing runs malware scans when users upload files, such as attachments or template files used to update user details or assignments. If malware is detected during an upload, the upload is rejected and an audit log about this event is written.

SAP Advanced Financial Closing uses the SAP Malware Scanning service for malware scanning. For more information, see [SAP Malware Scanning Service](https://help.sap.com/docs/malware-scanning-servce?version=Cloud) and [What Is SAP Malware Scanning Service?](https://help.sap.com/docs/malware-scanning-servce/sap-malware-scanning-service/what-is-sap-malware-scanning-service?version=Cloud).



## Result Files from External Systems

SAP Advanced Financial Closing integrates with external systems, such as BlackLine, as described under [Integration Capabilities](../Integration-Capabilities/integration-capabilities-8aa10e1.md). When you use an integration with an external system, the external system reports results back to SAP Advanced Financial Closing. The result attachments from these external systems are **referenced** by SAP Advanced Financial Closing, but they are not stored in SAP Advanced Financial Closing. As a result, SAP Advanced Financial Closing **does not run its malware scan** on these attachments.

> ### Caution:  
> The external system always owns the data and should run the malware scan.

If you upload attachments for tasks from external systems directly in SAP Advanced Financial Closing, SAP Advanced Financial Closing runs its usual malware scan.

