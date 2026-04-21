/**
 * Stream adapter: OpenAI SSE stream → Anthropic BetaRawMessageStreamEvent.
 *
 * This is the most complex piece — it maintains state to translate OpenAI's
 * flat delta-based streaming into Anthropic's structured block lifecycle:
 *
 *   message_start
 *     → content_block_start (text|thinking|tool_use)
 *       → content_block_delta* (text_delta|thinking_delta|input_json_delta)
 *     → content_block_stop
 *   → message_delta (stop_reason, final usage)
 *   → message_stop
 */

import { ThinkingTagParser } from './thinking-adapter.js'

/**
 * Transform an OpenAI SSE ReadableStream into an AsyncIterable that yields
 * Anthropic-format stream events, compatible with the SDK's
 * Stream<BetaRawMessageStreamEvent>.
 */
export function transformStream(
  body: ReadableStream<Uint8Array>,
  model: string,
): any {
  const iter = new OpenAIToAnthropicStreamIterator(body, model)
  const asyncIterable = {
    [Symbol.asyncIterator]() {
      return iter
    },
    // claude.ts checks `'controller' in e.value` to distinguish stream from
    // error messages — we must have this property.
    controller: new AbortController(),
  }
  return asyncIterable
}

// ---------------------------------------------------------------------------
// Iterator implementation
// ---------------------------------------------------------------------------

class OpenAIToAnthropicStreamIterator {
  private reader: ReadableStreamDefaultReader<Uint8Array>
  private decoder = new TextDecoder()
  private buffer = ''
  private queue: any[] = []
  private done = false
  private finalized = false

  // Anthropic event state
  private messageStarted = false
  private blockIndex = 0
  private currentBlockType: 'text' | 'thinking' | 'tool_use' | null = null
  private inputTokens = 0
  private outputTokens = 0
  private model: string
  private messageId = ''

  // Tool call tracking — OpenAI streams tool_calls by tc.index
  private activeToolCalls = new Map<
    number,
    { id: string; name: string; blockIndex: number }
  >()

  // <think> tag parser for QwQ-style models
  private thinkingParser = new ThinkingTagParser()

  constructor(body: ReadableStream<Uint8Array>, model: string) {
    this.reader = body.getReader()
    this.model = model
    this.messageId = `msg_compat_${Date.now()}`
  }

  async next(): Promise<IteratorResult<any>> {
    // Drain queued events first
    while (this.queue.length === 0 && !this.done) {
      await this.readChunk()
    }
    if (this.queue.length > 0) {
      return { value: this.queue.shift()!, done: false }
    }
    return { value: undefined as any, done: true }
  }

  // Read one chunk from the underlying stream and parse SSE lines
  private async readChunk(): Promise<void> {
    const { value, done } = await this.reader.read()
    if (done) {
      // Stream ended — make sure we emit finalization events
      if (!this.finalized) this.finalize()
      this.done = true
      return
    }

    this.buffer += this.decoder.decode(value, { stream: true })

    // SSE lines are separated by \n; an event ends with \n\n but we process
    // each `data:` line individually since OpenAI sends one JSON per line.
    const lines = this.buffer.split('\n')
    // Keep the last (potentially incomplete) line in the buffer
    this.buffer = lines.pop() || ''

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed || trimmed.startsWith(':')) continue // comment or empty

      if (trimmed.startsWith('data:')) {
        const payload = trimmed.slice(5).trim()
        if (payload === '[DONE]') {
          if (!this.finalized) this.finalize()
          this.done = true
          return
        }
        try {
          this.processChunk(JSON.parse(payload))
        } catch {
          // Malformed JSON — skip
        }
      }
    }
  }

  // -------------------------------------------------------------------------
  // Core: process a single OpenAI chunk
  // -------------------------------------------------------------------------

  private processChunk(chunk: any): void {
    const choice = chunk.choices?.[0]
    if (!choice && chunk.usage) {
      // Some providers send a final usage-only chunk
      this.outputTokens = chunk.usage.completion_tokens ?? this.outputTokens
      this.inputTokens = chunk.usage.prompt_tokens ?? this.inputTokens
      return
    }
    if (!choice) return

    // ---- message_start (once) ----
    if (!this.messageStarted) {
      this.messageStarted = true
      this.inputTokens = chunk.usage?.prompt_tokens ?? 0
      this.messageId = chunk.id || this.messageId
      this.queue.push({
        type: 'message_start',
        message: {
          id: this.messageId,
          type: 'message',
          role: 'assistant',
          content: [],
          model: chunk.model || this.model,
          stop_reason: null,
          stop_sequence: null,
          usage: {
            input_tokens: this.inputTokens,
            output_tokens: 0,
            cache_creation_input_tokens: 0,
            cache_read_input_tokens: 0,
          },
        },
      })
    }

    const delta = choice.delta
    if (!delta) {
      // finish_reason without delta — handle below
      if (choice.finish_reason && !this.finalized) {
        this.finalize(choice.finish_reason)
      }
      return
    }

    // ---- reasoning_content (DeepSeek R1) ----
    if (delta.reasoning_content) {
      this.emitThinking(delta.reasoning_content)
    }

    // ---- content (may contain <think> tags for QwQ) ----
    if (delta.content) {
      const { thinking, text } = this.thinkingParser.extract(delta.content)
      if (thinking) this.emitThinking(thinking)
      if (text) this.emitText(text)
    }

    // ---- tool_calls ----
    if (delta.tool_calls) {
      for (const tc of delta.tool_calls) {
        this.emitToolCall(tc)
      }
    }

    // ---- usage (streaming usage) ----
    if (chunk.usage) {
      this.outputTokens = chunk.usage.completion_tokens ?? this.outputTokens
      this.inputTokens = chunk.usage.prompt_tokens ?? this.inputTokens
    }

    // ---- finish ----
    if (choice.finish_reason && !this.finalized) {
      this.finalize(choice.finish_reason)
    }
  }

  // -------------------------------------------------------------------------
  // Emit helpers
  // -------------------------------------------------------------------------

  private emitThinking(text: string): void {
    if (this.currentBlockType !== 'thinking') {
      this.closeCurrentBlock()
      this.queue.push({
        type: 'content_block_start',
        index: this.blockIndex,
        content_block: { type: 'thinking', thinking: '', signature: '' },
      })
      this.currentBlockType = 'thinking'
    }
    this.queue.push({
      type: 'content_block_delta',
      index: this.blockIndex,
      delta: { type: 'thinking_delta', thinking: text },
    })
  }

  private emitText(text: string): void {
    if (this.currentBlockType !== 'text') {
      this.closeCurrentBlock()
      this.queue.push({
        type: 'content_block_start',
        index: this.blockIndex,
        content_block: { type: 'text', text: '' },
      })
      this.currentBlockType = 'text'
    }
    this.queue.push({
      type: 'content_block_delta',
      index: this.blockIndex,
      delta: { type: 'text_delta', text },
    })
  }

  private emitToolCall(tc: any): void {
    const tcIndex: number = tc.index ?? 0

    // New tool call starts when we see an id or a new name
    if (tc.id || (tc.function?.name && !this.activeToolCalls.has(tcIndex))) {
      this.closeCurrentBlock()
      const id = tc.id || `toolu_compat_${Date.now()}_${tcIndex}`
      const name = tc.function?.name || ''
      this.activeToolCalls.set(tcIndex, {
        id,
        name,
        blockIndex: this.blockIndex,
      })
      this.queue.push({
        type: 'content_block_start',
        index: this.blockIndex,
        content_block: { type: 'tool_use', id, name, input: {} },
      })
      this.currentBlockType = 'tool_use'
    }

    // Accumulate arguments JSON fragments
    if (tc.function?.arguments) {
      const active = this.activeToolCalls.get(tcIndex)
      if (active) {
        this.queue.push({
          type: 'content_block_delta',
          index: active.blockIndex,
          delta: {
            type: 'input_json_delta',
            partial_json: tc.function.arguments,
          },
        })
      }
    }
  }

  // -------------------------------------------------------------------------
  // Block lifecycle
  // -------------------------------------------------------------------------

  private closeCurrentBlock(): void {
    if (this.currentBlockType === null) return

    if (this.currentBlockType === 'thinking') {
      // Anthropic thinking blocks need a signature_delta before close.
      // Third-party models don't produce real signatures — emit a placeholder.
      this.queue.push({
        type: 'content_block_delta',
        index: this.blockIndex,
        delta: { type: 'signature_delta', signature: 'compat-no-sig' },
      })
    }

    this.queue.push({ type: 'content_block_stop', index: this.blockIndex })
    this.blockIndex++
    this.currentBlockType = null
  }

  private closeAllToolCalls(): void {
    for (const [tcIdx, active] of this.activeToolCalls) {
      // Only emit stop if this tool_call block hasn't been closed yet
      // (closeCurrentBlock handles the last one if currentBlockType=tool_use)
      if (active.blockIndex !== this.blockIndex || this.currentBlockType !== 'tool_use') {
        this.queue.push({
          type: 'content_block_stop',
          index: active.blockIndex,
        })
      }
    }
    this.activeToolCalls.clear()
  }

  private finalize(finishReason?: string): void {
    if (this.finalized) return
    this.finalized = true

    // Close all open blocks
    this.closeCurrentBlock()
    this.closeAllToolCalls()

    // Ensure we sent a message_start (edge case: empty response)
    if (!this.messageStarted) {
      this.messageStarted = true
      this.queue.push({
        type: 'message_start',
        message: {
          id: this.messageId,
          type: 'message',
          role: 'assistant',
          content: [],
          model: this.model,
          stop_reason: null,
          stop_sequence: null,
          usage: {
            input_tokens: 0,
            output_tokens: 0,
            cache_creation_input_tokens: 0,
            cache_read_input_tokens: 0,
          },
        },
      })
    }

    // message_delta with final stop_reason and usage
    this.queue.push({
      type: 'message_delta',
      delta: {
        stop_reason: mapFinishReason(finishReason),
        stop_sequence: null,
      },
      usage: { output_tokens: this.outputTokens },
    })

    // message_stop
    this.queue.push({ type: 'message_stop' })
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function mapFinishReason(reason?: string): string {
  switch (reason) {
    case 'stop':
      return 'end_turn'
    case 'tool_calls':
      return 'tool_use'
    case 'length':
      return 'max_tokens'
    case 'content_filter':
      return 'end_turn'
    default:
      return 'end_turn'
  }
}

// ---------------------------------------------------------------------------
// Non-streaming response conversion
// ---------------------------------------------------------------------------

export function transformNonStreamingResponse(data: any): any {
  const choice = data.choices?.[0]
  if (!choice) {
    throw new Error('No choices in OpenAI compat response')
  }

  const msg = choice.message
  const content: any[] = []

  // Text content
  if (msg.content) {
    content.push({ type: 'text', text: msg.content })
  }

  // Tool calls
  if (msg.tool_calls) {
    for (const tc of msg.tool_calls) {
      let input: any = {}
      try {
        input = JSON.parse(tc.function.arguments)
      } catch {
        input = {}
      }
      content.push({
        type: 'tool_use',
        id: tc.id,
        name: tc.function.name,
        input,
      })
    }
  }

  return {
    id: data.id || `msg_compat_${Date.now()}`,
    type: 'message',
    role: 'assistant',
    content,
    model: data.model || 'unknown',
    stop_reason: mapFinishReason(choice.finish_reason),
    stop_sequence: null,
    usage: {
      input_tokens: data.usage?.prompt_tokens ?? 0,
      output_tokens: data.usage?.completion_tokens ?? 0,
      cache_creation_input_tokens: 0,
      cache_read_input_tokens: 0,
    },
  }
}
