import { transformRequest } from './request-adapter.js'
import { transformStream, transformNonStreamingResponse } from './stream-adapter.js'

export function createOpenAICompatClient(options: {
  baseURL: string
  apiKey: string
  model: string
  defaultHeaders?: Record<string, string>
  maxRetries: number
  timeout: number
  [key: string]: any
}): unknown {
  // Normalize URL: strip trailing slash, handle /v1 suffix
  // Users may input: https://api.xxx.com  or  https://api.xxx.com/v1
  // We need: https://api.xxx.com/v1/chat/completions
  let baseURL = options.baseURL.replace(/\/+$/, '')
  const apiKey = options.apiKey
  const model = options.model
  const timeoutMs = options.timeout || 600000

  // Build the full completions endpoint once
  let completionsURL: string
  if (baseURL.endsWith('/v1')) {
    completionsURL = baseURL + '/chat/completions'
  } else if (baseURL.endsWith('/chat/completions')) {
    completionsURL = baseURL
  } else if (baseURL.endsWith('/v1/chat/completions')) {
    completionsURL = baseURL
  } else {
    completionsURL = baseURL + '/v1/chat/completions'
  }

  function messagesCreate(params: any, requestOptions?: any): any {
    const isStreaming = params.stream === true

    const promise = (async () => {
      const openaiParams = transformRequest(params, { model, baseURL, apiKey })

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(apiKey && { Authorization: 'Bearer ' + apiKey }),
      }

      if (requestOptions?.headers) {
        const rh = requestOptions.headers
        if (typeof rh === 'object') {
          for (const [k, v] of Object.entries(rh)) {
            if (typeof v === 'string') headers[k] = v
          }
        }
      }

      const signal = requestOptions?.signal
      const controller = new AbortController()
      let timeoutHandle: ReturnType<typeof setTimeout> | undefined
      if (!signal) {
        timeoutHandle = setTimeout(() => controller.abort(), requestOptions?.timeout ?? timeoutMs)
      }

      try {
        const response = await fetch(completionsURL, {
          method: 'POST',
          headers,
          body: JSON.stringify(openaiParams),
          signal: signal || controller.signal,
        })

        if (!response.ok) {
          let errorBody = ''
          try { errorBody = await response.text() } catch {}
          throw new Error('OpenAI-compatible API error ' + response.status + ': ' + response.statusText + (errorBody ? '\n' + errorBody : ''))
        }

        if (isStreaming) {
          if (!response.body) throw new Error('Streaming response has no body')
          const stream = transformStream(response.body, model)
          return {
            stream,
            requestId: response.headers.get('x-request-id') || null,
            response,
          }
        } else {
          const data = await response.json()
          return { data: transformNonStreamingResponse(data) }
        }
      } finally {
        if (timeoutHandle) clearTimeout(timeoutHandle)
      }
    })()

    if (isStreaming) {
      const p = promise.then(r => (r as any).stream) as any
      p.withResponse = () => promise.then(r => ({
        data: (r as any).stream,
        request_id: (r as any).requestId,
        response: (r as any).response,
      }))
      return p
    } else {
      return promise.then(r => (r as any).data)
    }
  }

  return {
    beta: {
      messages: {
        create: messagesCreate,
      },
    },
    messages: {
      create: messagesCreate,
    },
  }
}
