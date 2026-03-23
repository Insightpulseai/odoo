<!-- loioa880a9768d3e4a6ca8479d9b75656f7e -->

# Data Protection and Privacy

Learn about data protection and privacy in SAP Advanced Financial Closing.

Data protection is associated with numerous legal requirements and privacy concerns. In addition to compliance with general data protection and privacy acts, it is necessary to consider compliance with industry-specific legislation in different countries. SAP provides specific features and functions to support compliance with regard to relevant legal requirements, including data protection, which are documented in these templates along with the assumptions that have been guiding the implementation in the software. By nature of legal requirements the conclusion whether these features are covering customer specific demands as well as the conclusion whether additional measures have to be taken is solely with the customer.

> ### Note:  
> SAP does not provide legal advice in any form. SAP software supports data protection compliance by providing security features and specific data protection-relevant functions, such as simplified blocking and deletion of personal data. In many cases, compliance with applicable data protection and privacy laws will not be covered by a product feature. Definitions and other terms used in this document are not taken from a particular legal source.

> ### Caution:  
> The extent to which data protection is supported by technical means depends on secure system operation. Network security, security note implementation, adequate logging of system changes, and appropriate usage of the system are the basic technical requirements for compliance with data privacy legislation and other legislation.



<a name="loioa880a9768d3e4a6ca8479d9b75656f7e__section_vlk_1wp_qmb"/>

## Which Data Is Processed?

SAP Advanced Financial Closing stores task schedules needed to perform a financial close. This includes that SAP Advanced Financial Closing replicates a limited part of the organizational structure of the affected organization as needed for the scheduling of tasks. In addition, user metadata is processed, for example, roles, authorizations, and last changes to tasks or configurations. At no time does SAP Advanced Financial Closing read or store transactional financial data.

