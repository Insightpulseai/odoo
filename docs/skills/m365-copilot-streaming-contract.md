# Microsoft 365 Copilot Streaming Contract — Message Ordering Rules

> Applies when building a **custom engine agent** that streams responses
> back to Microsoft Teams or Microsoft 365 Copilot Chat.
> Scope: `agents/teams-surface/` and any future bot surface.

## Why this matters

Teams and M365 Copilot render agent messages based on **server timestamps,
activity IDs, and the relationship between streaming updates and non-streaming
activities**. If a custom engine agent mixes streaming text, media attachments,
and final messages within the same user turn, messages can appear **out of
sequence** — breaking UX and making the agent look broken.

Source: [Microsoft Learn — Custom engine agents overview, Message ordering
and streaming behavior](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/overview-custom-engine-agent#message-ordering-and-streaming-behavior).

## Rules (all 5 are load-bearing — do not skip)

### 1. One streaming sequence per user turn

Create exactly **one** `StreamingResponse` object per incoming message
activity. Finalize it by calling `endStream()` before sending any other
activity.

```python
# ✓ correct
stream = StreamingResponse(turn_context)
await stream.queue_text_chunk("Working on it…")
# … stream body …
await stream.end_stream()
# ONLY now can another activity go out
```

```python
# ✗ wrong — two streams open at once
stream_a = StreamingResponse(turn_context)
stream_b = StreamingResponse(turn_context)  # ordering becomes nondeterministic
```

### 2. Attach media INSIDE the stream

Use `set_attachments()` on the `StreamingResponse`. Do NOT send attachments
as a separate non-streaming activity — they can appear before or inside
the stream due to timestamp differences.

```python
# ✓ correct
stream.set_attachments([card])   # part of the streamed turn

# ✗ wrong — may render out of order
await turn_context.send_activity(Activity(attachments=[card]))
```

### 3. Don't start a new stream before finalizing the previous one

Multiple streams within the same turn produce unpredictable ordering in
Teams and Copilot. Always `await stream.end_stream()` before opening a new
`StreamingResponse`.

### 4. Serialize outgoing messages

Do not send messages from multiple threads / tasks in parallel. Ensure
every send is `await`ed to maintain strict ordering.

```python
# ✓ correct — awaited serially
await stream.queue_text_chunk(part_a)
await stream.queue_text_chunk(part_b)

# ✗ wrong — parallel sends reorder on server
await asyncio.gather(
    stream.queue_text_chunk(part_a),
    stream.queue_text_chunk(part_b),
)
```

### 5. Don't send streaming updates after `endStream()`

Once the stream is finalized, new updates become **separate activities**
and will likely appear out of order. If a follow-up is needed:

- Start a new stream for a new user turn, OR
- Use `replyToId` on the follow-up activity to keep it threaded to the
  stream's last message

## Implementation template (Python / botbuilder)

```python
async def on_message_activity(self, turn_context: TurnContext) -> None:
    stream = StreamingResponse(turn_context)
    try:
        await stream.queue_informative_update("Thinking…")

        async for chunk in self._orchestrate(turn_context.activity.text):
            if chunk.text:
                await stream.queue_text_chunk(chunk.text)
            if chunk.attachments:
                stream.set_attachments(chunk.attachments)  # rule 2
    except Exception:
        await stream.queue_text_chunk("\n\n_Backend error._")
    finally:
        await stream.end_stream()  # rules 1, 3, 5
```

## Checklist for code review

- [ ] Exactly one `StreamingResponse` per `on_message_activity` call
- [ ] `end_stream()` in a `finally:` block (always runs, even on exception)
- [ ] No `send_activity()` calls for attachments inside the stream window
- [ ] All sends are `await`ed sequentially, no `asyncio.gather` over sends
- [ ] No activities sent after `end_stream()` (if needed, start a new turn)

## Where this applies

- [agents/teams-surface/bot/bot.py](../../agents/teams-surface/bot/bot.py) — `PulserBot.on_message_activity`
- Any future ACA-hosted custom engine agent surface (Pulser, Tax Guru PH, Doc Intelligence)

## Related

- [Custom engine agent overview (MS Learn)](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/overview-custom-engine-agent)
- [M365 Agents SDK (MS Learn)](https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/m365-agents-sdk)
- [Agents Toolkit (MS Learn)](https://learn.microsoft.com/en-us/microsoft-365/developer/overview-m365-agents-toolkit)
