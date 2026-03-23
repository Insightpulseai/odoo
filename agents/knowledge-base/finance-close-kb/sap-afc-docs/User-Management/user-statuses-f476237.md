<!-- loiof47623754bc143f3bb1c084d15f0cc6c -->

# User Statuses

Learn which statuses and status changes are possible for users.

For users in SAP Advanced Financial Closing, several statuses are possible. You can see these statuses and the possible status changes in the following graphic:



![Graphic depicting the different user statuses and the possible status changes: After user creation through a CSV upload
							or through an API for SAP Advanced
                                                  Financial Closing, the user has the status
								Inactive. As soon as the person assigned to the user signs in for the first time, the user
							status is set to Active. The user stays in this status until it's deleted. In the case of a
							deletion, the user status changes to Deleted. However, if the user is used for a new sign-in, the
							user is reactivated and set to Active again.](images/Image_Map_User_Statuses_1055e04.png)

> ### Note:  
> To avoid the reactivation of a deleted user through a new logon via the IdP, you also need to unassign the user from all role collections **relevant for SAP Advanced Financial Closing**. This way, access to all apps for SAP Advanced Financial Closing is revoked. You can delete the user from role collections using the SAP BTP cockpit. For more information, see [Delete Users from Role Collections](https://help.sap.com/docs/BTP/65de2977205c403bbc107264b8eccf4b/4f8a242839a947f9a6f379650480c776.html).

