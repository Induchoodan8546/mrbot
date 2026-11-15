
import { useState } from 'react'
import {
  Bot,
  Plus,
  MessageSquare,
  Settings,
  PanelLeftClose,
  Send,
  Paperclip,
  Sparkles,
  User,
  ChevronDown,
} from 'lucide-react'
import { streamChat } from './services/chatservice'

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
}

function App() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function sendMessage() {
    const userMessage = message.trim()

    if (!userMessage || isGenerating) return

    setMessage('')
    setError(null)
    setIsGenerating(true)

    setMessages(previous => [
      ...previous,
      { role: 'user', content: userMessage },
      { role: 'assistant', content: '' },
    ])

    try {
      let activeConversationId = conversationId

      // Create a conversation for the first message.
      if (!activeConversationId) {
        const response = await fetch('/api/v1/conversations', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({}),
        })

        if (!response.ok) {
          throw new Error(`Could not create conversation (${response.status})`)
        }

        const conversation: { id: string } = await response.json()
        activeConversationId = conversation.id
        setConversationId(activeConversationId)
      }

      await streamChat(activeConversationId, userMessage, {
        onToken: (token) => {
          setMessages(previous => {
            const updated = [...previous]
            const lastMessage = updated[updated.length - 1]

            if (lastMessage?.role === 'assistant') {
              updated[updated.length - 1] = {
                ...lastMessage,
                content: lastMessage.content + token,
              }
            }

            return updated
          })
        },

        onDone: () => {
          // Streaming completed successfully.
        },

        onError: (message) => {
          setError(message || 'The AI could not generate a response.')
        },
      })
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Something went wrong.'

      setError(errorMessage)

      setMessages(previous => {
        const updated = [...previous]
        const lastMessage = updated[updated.length - 1]

        if (lastMessage?.role === 'assistant' && !lastMessage.content) {
          updated.pop()
        }

        return updated
      })
    } finally {
      setIsGenerating(false)
    }
  }

  function startNewChat() {
    if (isGenerating) return

    setMessages([])
    setConversationId(null)
    setMessage('')
    setError(null)
  }

  return (
    <div className="app-container">
      <aside className={`sidebar ${sidebarOpen ? '' : 'sidebar-hidden'}`}>
        <div className="sidebar-header">
          <div className="brand">
            <div className="brand-icon">
              <Bot size={23} />
            </div>
            <span>MR<span className="brand-accent">Bot</span></span>
          </div>

          <button
            className="icon-button"
            onClick={() => setSidebarOpen(false)}
            title="Close sidebar"
          >
            <PanelLeftClose size={19} />
          </button>
        </div>

        <button
          className="new-chat-button"
          onClick={startNewChat}
          disabled={isGenerating}
        >
          <Plus size={18} />
          <span>New chat</span>
        </button>

        <div className="sidebar-section">
          <p className="section-label">WORKSPACE</p>

          <button className="sidebar-item active">
            <MessageSquare size={17} />
            <span>Chat</span>
          </button>
        </div>

        <div className="sidebar-section history-section">
          <p className="section-label">RECENT CONVERSATIONS</p>
          <p className="empty-history">Your conversations will appear here.</p>
        </div>

        <div className="sidebar-bottom">
          <button className="sidebar-item">
            <Settings size={18} />
            <span>Settings</span>
          </button>

          <div className="profile">
            <div className="profile-avatar">M</div>
            <div className="profile-info">
              <span>MRBot User</span>
              <small>Local workspace</small>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            {!sidebarOpen && (
              <button
                className="icon-button"
                onClick={() => setSidebarOpen(true)}
                title="Open sidebar"
              >
                <PanelLeftClose size={19} />
              </button>
            )}

            <span className="workspace-title">Chat</span>
            <ChevronDown size={15} className="muted-icon" />
          </div>

          <div className="connection-status">
            <span className="status-dot" />
            Local AI
          </div>
        </header>

        <section className="chat-area">
          {messages.length === 0 ? (
            <div className="welcome-screen">
              <div className="welcome-icon">
                <Sparkles size={27} />
              </div>

              <h1>What can I help you with?</h1>

              <p>
                Your local AI assistant, powered by MRBot.
                <br />
                Ask anything to get started.
              </p>

              <div className="suggestions">
                <button onClick={() => setMessage('Explain how neural networks work.')}>
                  <span>Learn something</span>
                  <small>Explain a complex topic</small>
                </button>

                <button onClick={() => setMessage('Help me write a Python program.')}>
                  <span>Write some code</span>
                  <small>Build and debug applications</small>
                </button>

                <button onClick={() => setMessage('Help me brainstorm a project idea.')}>
                  <span>Brainstorm ideas</span>
                  <small>Explore new possibilities</small>
                </button>
              </div>
            </div>
          ) : (
            <div className="messages-container">
              {messages.map((item, index) => (
                <div
                  className={`message-row ${item.role}`}
                  key={index}
                >
                  <div className="message-avatar">
                    {item.role === 'assistant' ? (
                      <Bot size={19} />
                    ) : (
                      <User size={19} />
                    )}
                  </div>

                  <div className="message-content">
                    <span className="message-author">
                      {item.role === 'assistant' ? 'MRBot' : 'You'}
                    </span>

                    <p>
                      {item.content ||
                        (item.role === 'assistant' && isGenerating
                          ? 'Thinking...'
                          : '')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {error && (
          <div className="error-message" role="alert">
            {error}
          </div>
        )}

        <footer className="composer-area">
          <div className="composer">
            <button className="composer-icon" title="Attach file" disabled>
              <Paperclip size={19} />
            </button>

            <textarea
              placeholder="Message MRBot..."
              value={message}
              disabled={isGenerating}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  void sendMessage()
                }
              }}
              rows={1}
            />

            <button
              className="send-button"
              onClick={() => void sendMessage()}
              disabled={!message.trim() || isGenerating}
              title="Send message"
            >
              <Send size={18} />
            </button>
          </div>

          <p className="composer-note">
            MRBot can make mistakes. Verify important information.
          </p>
        </footer>
      </main>
    </div>
  )
}

export default App
