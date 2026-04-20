/**
 * Thinking model adapter for third-party models.
 *
 * Handles:
 * - DeepSeek R1: `reasoning_content` field in SSE delta (handled in stream-adapter)
 * - QwQ / other models: `<think>...</think>` tags embedded in content
 * - Normal models: pass through unchanged
 */

/** Per-stream state for <think> tag parsing */
export class ThinkingTagParser {
  private inThinkTag = false
  private pendingBuffer = ''

  /**
   * Process a text chunk, separating thinking content from normal text.
   * Handles partial `<think>` / `</think>` tags across chunk boundaries.
   */
  extract(text: string): { thinking: string; text: string } {
    let thinking = ''
    let normalText = ''
    let i = 0

    while (i < text.length) {
      if (!this.inThinkTag) {
        const openIdx = text.indexOf('<think>', i)
        if (openIdx === -1) {
          // Check for partial tag at end
          const remaining = text.slice(i)
          const partialMatch = this.findPartialOpenTag(remaining)
          if (partialMatch > 0) {
            normalText += remaining.slice(0, -partialMatch)
            this.pendingBuffer = remaining.slice(-partialMatch)
          } else {
            normalText += remaining
          }
          break
        }
        normalText += text.slice(i, openIdx)
        this.inThinkTag = true
        i = openIdx + 7 // '<think>'.length
      } else {
        const closeIdx = text.indexOf('</think>', i)
        if (closeIdx === -1) {
          thinking += text.slice(i)
          break
        }
        thinking += text.slice(i, closeIdx)
        this.inThinkTag = false
        i = closeIdx + 8 // '</think>'.length
      }
    }

    // Flush any pending buffer from previous chunk
    if (this.pendingBuffer && !this.pendingBuffer.startsWith('<think>'.slice(0, this.pendingBuffer.length))) {
      normalText = this.pendingBuffer + normalText
      this.pendingBuffer = ''
    }

    return { thinking, text: normalText }
  }

  private findPartialOpenTag(text: string): number {
    const tag = '<think>'
    for (let len = Math.min(text.length, tag.length - 1); len > 0; len--) {
      if (text.endsWith(tag.slice(0, len))) {
        return len
      }
    }
    return 0
  }

  reset(): void {
    this.inThinkTag = false
    this.pendingBuffer = ''
  }
}
