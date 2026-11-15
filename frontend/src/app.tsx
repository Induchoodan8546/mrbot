
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

function App() {
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<
    { role: 'user' | 'assistant'; content: string }[]
  >([])
  const [sidebarOpen, setSidebarOpen] = useState(true)

  function sendMessage() {
    if (!message.trim()) return

    setMessages((previous) => [
      ...previous,
      { role: 'user', content: message.trim() },
    ])

    setMessage('')
  }

  return (
    <div className="app-container">

      {/* Sidebar */}
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
          onClick={() => setMessages([])}
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

      {/* Main workspace */}
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
                    <p>{item.content}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <footer className="composer-area">
          <div className="composer">
            <button className="composer-icon" title="Attach file">
              <Paperclip size={19} />
            </button>

            <textarea
              placeholder="Message MRBot..."
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' && !event.shiftKey) {
                  event.preventDefault()
                  sendMessage()
                }
              }}
              rows={1}
            />

            <button
              className="send-button"
              onClick={sendMessage}
              disabled={!message.trim()}
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
