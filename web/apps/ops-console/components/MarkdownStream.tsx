'use client'

import { Streamdown } from 'streamdown'

interface MarkdownStreamProps {
  /** Markdown content — may be a partial/streaming string. */
  value: string
  /** Set to true while tokens are still arriving to show the streaming caret. */
  isStreaming?: boolean
}

/**
 * Drop-in Markdown renderer for both static and streaming (AI) content.
 *
 * Usage:
 *   <MarkdownStream value={text} />                   // static
 *   <MarkdownStream value={partial} isStreaming />     // streaming AI output
 *
 * Handles unterminated markdown blocks (bold, code fences, links) without
 * jitter or mis-renders while tokens arrive.
 */
export function MarkdownStream({ value, isStreaming = false }: MarkdownStreamProps) {
  return (
    <Streamdown caret="block" isAnimating={isStreaming}>
      {value}
    </Streamdown>
  )
}
