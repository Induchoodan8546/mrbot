
export interface ChatStreamCallbacks {
  onToken: (text: string) => void
  onDone: () => void
  onError: (message: string) => void
}

export async function streamChat(
  conversationId: string,
  message: string,
  callbacks: ChatStreamCallbacks
): Promise<void> {
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
      temperature: 0.7,
    }),
  })

  if (!response.ok) {
    throw new Error(`Chat request failed: ${response.status}`)
  }

  if (!response.body) {
    throw new Error('Streaming response body is unavailable.')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { value, done } = await reader.read()

      if (done) break

      buffer += decoder.decode(value, { stream: true })

      const events = buffer.split(/\r?\n\r?\n/)
      buffer = events.pop() ?? ''

      for (const eventBlock of events) {
        let eventName = ''
        let data = ''

        for (const line of eventBlock.split(/\r?\n/)) {
          if (line.startsWith('event:')) {
            eventName = line.slice(6).trim()
          } else if (line.startsWith('data:')) {
            data += line.slice(5).trim()
          }
        }

        if (!data) continue

        const payload = JSON.parse(data)

        if (eventName === 'token') {
          callbacks.onToken(payload.text)
        } else if (eventName === 'done') {
          callbacks.onDone()
        } else if (eventName === 'error') {
          callbacks.onError(payload.message)
        }
      }
    }

    // Process any remaining event data.
    buffer += decoder.decode()

    if (buffer.trim()) {
      const lines = buffer.split(/\r?\n/)
      const eventName = lines.find(line => line.startsWith('event:'))
        ?.slice(6).trim()
      const dataLine = lines.find(line => line.startsWith('data:'))

      if (dataLine) {
        const payload = JSON.parse(dataLine.slice(5).trim())

        if (eventName === 'token') {
          callbacks.onToken(payload.text)
        } else if (eventName === 'done') {
          callbacks.onDone()
        } else if (eventName === 'error') {
          callbacks.onError(payload.message)
        }
      }
    }
  } finally {
    reader.releaseLock()
  }
}
