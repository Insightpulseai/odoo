======================
AI voice transcription
======================

.. |AI| replace:: :abbr:`AI (Artificial Intelligence)`

Odoo |AI| can transcribe spoken audio into text and generate summaries from that transcript. This
feature supports both meeting recordings and real-time dictation, making it easier to capture notes,
decisions, and action items without manual typing.

Voice transcription converts spoken audio into a written transcript. Once a transcript is available,
Odoo |AI| can generate a summary that highlights key information, such as:

- key discussion points
- decisions
- action items
- next steps

Transcription and summarization can be used for meetings, calls, quick dictations, and internal
notes.

.. note::
   Voice transcripts can be created in the *Description* and *Notes* fields of most records, as well
   as in **Knowledge** articles.

   .. image:: voice/power-box.png
      :alt: The powerbox in the description tab of a task in the Projects app.

Voice transcription works by temporarily recording audio during the session, replaying it for
transcription, and generating a written transcript and summary. Once the transcription process is
complete, the audio recording is automatically discarded. The recorded audio is not stored,
replayable, or accessible from the database.

Transcribe a meeting
====================

To create a voice transcript, type `/` to open the :ref:`powerbox
<essentials/html_editor/commands>`. Select :guilabel:`Voice Transcript` from the drop-down list.
This creates a new text block. Click :icon:`fa-bars` :guilabel:`Notes` to add notes and details
regarding the meeting. This is where information, such as a meeting agenda and attendees, can be
added. Click :icon:`fa-microphone` :guilabel:`Transcript` to switch to a live view of the transcript
being created in real-time.

When the meeting is ready to begin, click :icon:`fa-circle` :guilabel:`Start Recording`.

.. important::
   Clicking :icon:`fa-circle` :guilabel:`Start Recording` may cause a pop-up in the browser,
   requesting access to a microphone. If permission is not given, the recording stops, and an error
   message appears. To combat this error, refresh the page and allow Odoo access to the microphone.

When the meeting has ended, click :icon:`fa-stop` :guilabel:`Stop Recording`. The recorded audio is
then processed to generate a transcript and an |AI| summary. Once processing is complete, the audio
recording is automatically discarded, leaving only the transcript and summary available.

.. image:: voice/ai-summary.png
   :alt: The AI summary of a meeting transctipt.

The |AI| summary can be manually edited to provide additional insight, such as identifying meeting
attendees by name, or specifying key points. The meeting notes can then be converted into an email
recap, or shared directly via email by clicking the :guilabel:`Share by email` button.
