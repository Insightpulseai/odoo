:show-content:

.. |VOIP| replace:: :abbr:`VoIP (Voice over Internet Protocol)`

=====
Phone
=====

.. note::
   As of Odoo 19.0, the *VoIP* module has been renamed to *Odoo Phone*.

The Odoo **Phone** app enables businesses to handle calls over the internet by integrating directly
with Odoo apps like **CRM** and **Helpdesk**. The **Phone** app can link calls and messages to
customer interactions, log communication history, and automate call routing based on predefined
rules. Features like call recording and analytics provide insights into call volume and response
times, helping businesses streamline external communication and track team performance.

.. cards::
   .. card:: *Phone* widget
      :target: voip/voip_widget
      :large:

      Get started with the **Phone** widget essentials, including actions that can be taken during a
      call.

   .. card:: Devices and integrations
      :target: voip/devices_integrations
      :large:

      Learn how to access the **Phone** widget from different devices (like phones) and apps (like
      Linphone).

.. seealso::
   `Odoo Tutorials: Phone <https://www.odoo.com/slides/voip-voice-over-ip-315>`_

About VoIP
==========

The **Phone** app uses the following technologies to make and receive calls in Odoo:

- **Voice over Internet Protocol (VoIP)**: Technology that is used to handle calls that are not made
  from a phone line.
- **Session Initiation Protocol (SIP)**: Technology included in |VOIP| that specifically handles the
  setup, management, and termination of calls.
- **Call queue**: A system to route calls (usually in a support team). This allows customers to wait
  for help if no support agents are available.
- **Dial plans**: A system to define how |VOIP| calls are routed, based on set rules.

Configure the Phone app
=======================

To make |VOIP| calls in Odoo, first :ref:`install <general/install>` the **Phone** app.

Once the app is installed, a :icon:`oi-voip` (:guilabel:`Phone`) icon will appear at the top of the
screen. When this icon is clicked, a **Phone** pop-up widget appears on the screen. This is where
users can make and receive calls, send emails, edit user and employee info, and manage activities.
The pop-up widget stays open when navigating other Odoo apps.

Assign user permissions
-----------------------

By default, users can receive their own calls, and managers can receive calls for their team
members. To grant additional |VOIP| permissions to a user, go to :menuselection:`Settings app -->
Users \& Companies --> Users` and search for the user. Open the user's contact card and navigate to
the *Access Rights* tab. Go to the *Productivity* section, and in the |VOIP| field select the
desired access level.

There are three access roles for |VOIP|:

- :guilabel:`No`: cannot access |VOIP| features.
- :guilabel:`Officer`: can view and report on all calls.
- :guilabel:`Administrator`: can view, report, and manage call settings.

.. important::
   | Database administrators are not automatically granted administrator rights for |VOIP|.
   | Make sure to set the correct access level for each |VOIP| user.

To modify these roles or add custom roles, see :ref:`Create and modify groups
<access-rights/groups>`.

Connect to a VoIP provider
--------------------------

Making calls through the **Phone** app also requires a |VOIP| service provider. Odoo supports three
verified providers by default: :doc:`Axivox <voip/axivox>`, :doc:`DIDWW <voip/didww>`, and
:doc:`OnSIP <voip/onsip>`. Click on the cards below to learn how to configure these service
providers in the Odoo database:

.. cards::
   .. card:: Axivox configuration
      :target: voip/axivox
      :large:

      Learn how to set up Axivox in Odoo. This includes adding users to Axivox, setting up call
      queues, and more.

   .. card:: OnSIP configuration
      :target: voip/onsip
      :large:

      Learn how to set up OnSIP in Odoo. This includes entering OnSIP credentials into Odoo and
      handling troubleshooting.

   .. card:: DIDWW configuration
      :target: voip/didww
      :large:

      Learn how to set up DIDWW in Odoo. This includes entering DIDWW credentials into Odoo and
      purchasing new numbers.

Other providers must meet two requirements to connect with Odoo:

#. The |VOIP| host must provide access to a SIP server via a websocket connection.
#. The |VOIP| host must support WebRTC protocol.

.. important::
   If these requirements are met, it should be possible to add the alternate provider to Odoo.
   However, Odoo recommends using a verified provider, and cannot guarantee that every alternate
   provider is compatible with the **Phone** app.

To add credentials for an alternate provider, go to the :menuselection:`Phone app --> Configuration
--> Settings`. Click :guilabel:`New` and enter the provider information (like the websocket's URL).
Enter the domain created by the alternate provider in the :guilabel:`OnSIP Domain` field.

For issues setting up the |VOIP| service provider in Odoo, follow the :ref:`relevant troubleshooting
steps <voip/voip_widget/troubleshooting_voip>`. For any other issues with the |VOIP| service
provider, reach out directly to their support team.

VoIP workflows
==============

Odoo **Phone** is popular with sales teams and support teams, but can be useful for other teams as
well. Click the cards below to learn about |VOIP| workflows in Odoo:

.. cards::
   .. card:: Sales teams and VoIP
      :target: voip/sales_calls
      :large:

      Learn how to use Odoo **Phone** for a sales team workflow. This includes making sales calls,
      handling follow-ups, and sending a sales quotation while on a call.

   .. card:: Support queues and VoIP
      :target: voip/support_calls
      :large:

      Learn how to use Odoo **Phone** for a support team workflow. This includes joining a call
      queue as an agent and handling live phone support tickets.

.. toctree::
   :titlesonly:

   voip/onsip
   voip/axivox
   voip/didww
   voip/voip_widget
   voip/devices_integrations
   voip/sales_calls
   voip/support_calls
