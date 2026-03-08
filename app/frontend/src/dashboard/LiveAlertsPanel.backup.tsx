/**
 * BACKUP: Live Alerts panel + button — removed from Dashboard to test layout fix.
 * If removing Live Alerts did NOT fix the slide-left layout, undo by restoring this into Dashboard.tsx.
 *
 * In Dashboard.tsx you need:
 * 1. Import: import { RajuDay } from '../components/RajuDay'
 * 2. Constant: const PANEL_WIDTH = 420
 * 3. State: const [panelOpen, setPanelOpen] = useState(false)
 * 4. In header (next to Logout): the Live Alerts button (see below)
 * 5. After the left column </div>: the Live Alerts panel (see below)
 */

const PANEL_WIDTH = 420

// Live Alerts button (place in header row, before Logout button):
/*
                <button
                  type="button"
                  onClick={() => setPanelOpen((o) => !o)}
                  className="flex items-center gap-2 rounded-xl px-4 py-2.5 text-white text-sm font-bold transition-all duration-200 hover:opacity-95 active:scale-[0.98]"
                  style={{
                    background: panelOpen ? '#64748b' : 'linear-gradient(135deg,#f59e0b,#ea580c)',
                    boxShadow: panelOpen ? 'none' : '0 4px 14px rgba(245, 158, 11, 0.4)',
                  }}
                  aria-label={panelOpen ? 'Close Live Alerts' : 'Open Live Alerts'}
                >
                  <svg width={16} height={16} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                  {panelOpen ? 'Close' : 'Live Alerts'}
                </button>
*/

// Live Alerts panel (place after the left column div, inside the same parent flex div):
/*
          {/* ── RIGHT: Live Alerts panel as overlay; hidden on first load / when closed ── *\/}
          <div
            role="dialog"
            aria-label="Live Alerts"
            aria-hidden={!panelOpen}
            style={{
              position: 'absolute',
              top: 0,
              right: 0,
              bottom: 0,
              width: PANEL_WIDTH,
              transform: panelOpen ? 'translateX(0)' : 'translateX(100%)',
              transition: 'transform 280ms cubic-bezier(0.32, 0.72, 0, 1)',
              visibility: panelOpen ? 'visible' : 'hidden',
              willChange: 'transform',
              flexShrink: 0,
              display: 'flex',
              flexDirection: 'column',
              background: '#fff',
              boxShadow: '-8px 0 32px rgba(0,0,0,0.12)',
              zIndex: 40,
              overflow: 'hidden',
              pointerEvents: panelOpen ? 'auto' : 'none',
            }}
          >
            <div
              style={{
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                borderBottom: '1px solid #e5e7eb',
                background: 'linear-gradient(135deg,#075e54,#0d9488)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <svg width={18} height={18} fill="none" stroke="#fff" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                <span style={{ fontWeight: 800, fontSize: '0.95rem', color: '#fff' }}>Live Alerts</span>
                <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>— My day</span>
              </div>
              <button
                type="button"
                onClick={() => setPanelOpen(false)}
                aria-label="Close"
                className="rounded-lg p-2 text-white/90 hover:bg-white/20 transition-colors"
              >
                <svg width={18} height={18} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            <div style={{ flex: 1, minHeight: 0, overflow: 'hidden' }}>
              <RajuDay welcomeName={welcomeName} onClose={() => setPanelOpen(false)} />
            </div>
          </div>
*/

export { PANEL_WIDTH }
