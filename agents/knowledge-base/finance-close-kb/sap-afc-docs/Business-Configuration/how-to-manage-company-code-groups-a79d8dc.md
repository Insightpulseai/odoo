<!-- loioa79d8dc4e7d84253a8996338b88efd96 -->

# How to Manage Company Code Groups

Create and manage company code groups.



<a name="loioa79d8dc4e7d84253a8996338b88efd96__prereq_xyl_knd_gxb"/>

## Prerequisites

-   Your user must have a role collection assigned that includes one of the following role templates:

    -   `AFC_CompanyCodeGroupsApp`
    -   `AFC_Config`


    For more information about role templates, see [How to Manage Static Role Templates](../User-Management/how-to-manage-static-role-templates-0cca34d.md) and [Static Roles for SAP Advanced Financial Closing](../User-Management/static-roles-for-sap-advanced-financial-closing-b92a241.md).

-   Get a good understanding of how company code groups work in SAP Advanced Financial Closing. For more information, see [Company Code Groups](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/d673a87cfa484a35a241b3eadc7ba815.html "Understand how company code groups work.") :arrow_upper_right:.



## Context

> ### Remember:  
> In company code groups, you group company codes that can be defined by the same value for a specific grouping characteristic. You create them within **one specific** characteristic.
> 
> Grouping characteristics define by which characteristic you want to group company codes. SAP Advanced Financial Closing offers four grouping characteristics. What each characteristic represents, however, is defined by your company.

The following video gives you a quick overview about how to work with company code groups in SAP Advanced Financial Closing:

> ### Note:  
> For this video, audio is only available in English. However, captions/subtitles may already be available in other languages. Simply click the *CC* button at the bottom right of the video player to see which languages are supported.
> 
> Additionally, using the *Search within video* box, you can run a search on the captions for English and German.



## Procedure

1.  Open the *Configuration* app.

    The next screen lists all the configuration apps you're allowed to access.

2.  Choose *Company Code Groups* from the list.

    This brings you to the *Manage Company Code Groups* app.

3.  Decide for your company what each characteristic represents.

    For example, you can decide that characteristic 1 represents regions.

4.  To create a new company code group, navigate to a grouping characteristic tab and choose *Create* in the toolbar.

5.  On the new screen, provide a name and description for your company code group.

    For example, for a group within the characteristic *Region*, you can enter a region, such as `North`, `East`, `South`, or `West`.

6.  Choose *Create* to confirm.

7.  **Optional:** In the company code group, you can still edit the name and description by choosing *Edit General Information*.

8.  Under *Assigned Company Codes*, choose *Add* in the table toolbar.

9.  Select the company codes you want to assign to this group within the selected characteristic.

10. Choose *Add* to confirm.

11. **Optional:** If you ever need to remove a company code from this group, open the company code group, select the company code in the table, and choose *Delete*.




<a name="loioa79d8dc4e7d84253a8996338b88efd96__result_yxs_ztd_gxb"/>

## Results

You have now created a company code group within a grouping characteristic.



<a name="loioa79d8dc4e7d84253a8996338b88efd96__postreq_gjh_b5d_gxb"/>

## Next Steps

Repeat the steps above to create other company code groups within the same characteristic or for other characteristics.

<a name="task_lkb_hnj_wyb"/>

<!-- task\_lkb\_hnj\_wyb -->

## How to Maintain Several Company Code Group Assignments at the Same Time

Maintain, update, or remove several assignments at the same time.



<a name="task_lkb_hnj_wyb__prereq_mvh_vnj_wyb"/>

## Prerequisites

You have created company code groups as described above.



<a name="task_lkb_hnj_wyb__context_mbq_tnj_wyb"/>

## Context

You can maintain, update, and remove assignments for several company codes at the same time.



<a name="task_lkb_hnj_wyb__steps_xzz_snj_wyb"/>

## Procedure

1.  Go to the *Configuration* app and choose *Company Code Groups* from the table.

2.  Go to the *Assignment Overview* tab.

3.  Find and select the company codes for which you want to change the group assignments.

4.  Choose *Change* in the table toolbar.

5.  For each grouping characteristic, select the corresponding option from the dropdown menus. The following options are available:

    1.  For *<Keep Existing Value\>*: No further action is required.

    2.  For *<Replace Field Value\>*: In the new input field, either type the name of a company code group and select it from the list, or open the value help to get an overview of the values available.

    3.  For *<Clear Field Value\>*: No further action is required, the value will be removed when you confirm the dialog.


6.  To confirm your settings, choose *Change* in the dialog footer.




<a name="task_lkb_hnj_wyb__result_tdy_npj_wyb"/>

## Results

You have now updated the group assignments of several company codes.

**Related Information**  


[Company Code Groups](https://help.sap.com/viewer/b3f5b9cf1ab7498fad5b6f297013d65a/SHIP/en-US/d673a87cfa484a35a241b3eadc7ba815.html "Understand how company code groups work.") :arrow_upper_right:

