path = r"c:\DONARVERSION1\frontend\app\page.tsx"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print(f"Line 225: {lines[224].rstrip()}")
print(f"Line 290: {lines[289].rstrip()}")
print(f"Line 642: {lines[641].rstrip()}")
print(f"Line 853: {lines[852].rstrip()}")

# ── Change 1: header inner div (lines 225-290, indices 224:290) ─────────────
new_header = '''        <div style={{ padding: isMobile ? "10px 16px" : "0 24px",
          display: "flex", alignItems: "center", justifyContent: "space-between",
          flexDirection: isMobile ? "column" : "row", gap: isMobile ? 8 : 0 }}>

          {/* Brand */}
          <div style={{ fontWeight: 800, fontSize: isMobile ? 14 : 16, letterSpacing: 0.3, flexShrink: 0,
                        padding: isMobile ? 0 : "14px 0" }}>
            🩸 DONAR-APP
          </div>

          {/* Tabs + Herramientas */}
          <nav style={{ display: "flex", gap: 2, flexWrap: "wrap",
            justifyContent: isMobile ? "center" : "flex-end", alignItems: "center" }}>
            {TABS.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)} style={{
                background: "transparent", border: "none", cursor: "pointer",
                padding: isMobile ? "6px 10px" : "0 14px",
                height: isMobile ? "auto" : 52,
                fontSize: isMobile ? 11 : 13, color: tab === t.id ? "white" : "#94a3b8",
                fontWeight: tab === t.id ? 700 : 400,
                borderBottom: tab === t.id ? "2px solid #60a5fa" : "2px solid transparent",
                transition: "all 0.15s",
              }}>
                {t.label}
              </button>
            ))}
            <div style={{ width: 1, height: 24, background: "rgba(255,255,255,0.15)", margin: "0 6px" }} />
            <div style={{ position: "relative" }}>
              <button onClick={() => setToolsOpen(o => !o)}
                style={{ display: "flex", alignItems: "center", gap: 5,
                         background: toolsOpen ? "#334155" : "rgba(255,255,255,0.1)",
                         border: "1px solid rgba(255,255,255,0.2)",
                         borderRadius: 8, cursor: "pointer", padding: "5px 11px",
                         fontSize: 12, color: "#e2e8f0", fontWeight: 600,
                         transition: "all 0.15s" }}>
                ⚙️ Herramientas
                <span style={{ fontSize: 9, opacity: 0.6 }}>{toolsOpen ? "▲" : "▼"}</span>
              </button>
              {toolsOpen && (
                <div style={{ position: "absolute", right: 0, top: "calc(100% + 8px)", zIndex: 200,
                              background: "white", borderRadius: 10, border: "1px solid #e2e8f0",
                              boxShadow: "0 8px 32px rgba(0,0,0,0.18)", width: 340, padding: "8px 0" }}>
                  {[
                    { e: "🎤", t: "Google ASR", d: "Transcripción de voz en tiempo real con la Web Speech API del navegador." },
                    { e: "🟣", t: "Whisper offline", d: "Transcripción local con IA (OpenAI). El audio no sale de tu servidor." },
                    { e: "🔊", t: "TTS", d: "Convierte las respuestas a audio MP3 con gTTS (Google)." },
                    { e: "📊", t: "N-gramas / Perplejidad", d: "Detecta si la consulta está dentro del dominio de donación de sangre." },
                    { e: "🔍", t: "TF-IDF / IR", d: "Recupera documentos del corpus ordenados por relevancia (similitud coseno)." },
                    { e: "📏", t: "WER", d: "Word Error Rate — evalúa la calidad de la transcripción ASR." },
                  ].map((it, i) => (
                    <div key={i} style={{ display: "flex", gap: 10, padding: "10px 16px",
                                         borderBottom: i < 5 ? "1px solid #f1f5f9" : "none",
                                         alignItems: "flex-start" }}>
                      <span style={{ fontSize: 20, flexShrink: 0 }}>{it.e}</span>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 12, color: "#0f172a", marginBottom: 2 }}>{it.t}</div>
                        <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5 }}>{it.d}</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </nav>
        </div>
'''

# ── Change 2: TabConsulta (lines 642-853, indices 641:853) ─────────────────
new_tabconsulta = '''function TabConsulta({ isMobile }: { isMobile: boolean }) {
  const texto = useChatFlow({ autoTts: false });
  const voz   = useChatFlow({ autoTts: true });
  const [activePanel, setActivePanel] = useState<"texto" | "voz">("texto");

  const etapaIdx = (f: FaseChat) => {
    if (["pedir_edad","pedir_sexo","pedir_peso"].includes(f)) return 0;
    if (f === "resultado") return 2;
    return 1;
  };

  const BOOL_FASES = [
    "q_salud","q_medicacion","q_corazon","q_riñones_pulmones",
    "q_neuro_cancer","q_diabetes","q_hepatitis","q_ets_vih",
    "q_chagas","q_procedimientos","q_tatuaje","q_transfusion",
    "q_riesgo_sexual","q_drogas","q_vacunas","q_embarazo",
  ];

  const renderInput = (chat: ReturnType<typeof useChatFlow>) => {
    const { fase, input, setInput, inputError, setInputError, loading, manejarEnvio } = chat;

    if (fase === "pedir_sexo") return (
      <div style={{ display: "flex", gap: 8, padding: "12px 16px", borderTop: "1px solid #cbd5e1" }}>
        {["Masculino","Femenino","Otro"].map(s => (
          <button key={s} onClick={() => chat.seleccionarOpcion(s)}
            style={{ flex: 1, padding: "10px 4px", borderRadius: 8,
                     border: "1px solid #cbd5e1", background: "#f8fafc",
                     cursor: "pointer", fontSize: 13, fontWeight: 600 }}>
            {s}
          </button>
        ))}
      </div>
    );

    if (fase === "resultado") return (
      <div style={{ display: "flex", justifyContent: "center", padding: "12px 16px", borderTop: "1px solid #cbd5e1" }}>
        <button onClick={chat.reiniciar}
          style={{ padding: "10px 24px", borderRadius: 8, border: "none",
                   background: "#0f172a", color: "white", cursor: "pointer",
                   fontSize: 14, fontWeight: 600 }}>
          Nueva evaluación
        </button>
      </div>
    );

    if (BOOL_FASES.includes(fase)) return (
      <div style={{ display: "flex", gap: 8, padding: "12px 16px", borderTop: "1px solid #cbd5e1" }}>
        {["Sí","No"].map(op => (
          <button key={op} onClick={() => manejarEnvio(op)}
            style={{ flex: 1, padding: "10px 4px", borderRadius: 8,
                     border: op === "Sí" ? "1px solid #dc2626" : "1px solid #16a34a",
                     background: op === "Sí" ? "#fff1f2" : "#f0fdf4",
                     cursor: "pointer", fontSize: 14, fontWeight: 700,
                     color: op === "Sí" ? "#dc2626" : "#16a34a" }}>
            {op}
          </button>
        ))}
      </div>
    );

    return (
      <div style={{ display: "flex", flexDirection: "column", padding: "12px 16px",
                    borderTop: "1px solid #cbd5e1", gap: 6 }}>
        {inputError && <div style={{ fontSize: 12, color: "#dc2626" }}>{inputError}</div>}
        <div style={{ display: "flex", gap: 8 }}>
          <input value={input}
            onChange={e => { setInput(e.target.value); setInputError(""); }}
            onKeyDown={e => { if (e.key === "Enter" && !loading) manejarEnvio(input); }}
            placeholder={chat.placeholder} disabled={loading}
            style={{ flex: 1, padding: "10px 12px", borderRadius: 8,
                     border: inputError ? "1px solid #dc2626" : "1px solid #cbd5e1",
                     fontSize: 14, outline: "none" }} />
          <button onClick={() => manejarEnvio(input)} disabled={loading || !input.trim()}
            style={{ padding: "10px 16px", borderRadius: 8, border: "none",
                     background: "#0f172a", color: "white", cursor: "pointer",
                     opacity: loading || !input.trim() ? 0.5 : 1 }}>
            ➤
          </button>
        </div>
      </div>
    );
  };

  const stepBadges = (fase: FaseChat) => (
    <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
      {["Datos","Preguntas","Resultado"].map((lbl, i) => (
        <div key={i} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 20, fontWeight: 600,
                              background: etapaIdx(fase) === i ? "#0f172a" : "#e2e8f0",
                              color: etapaIdx(fase) === i ? "white" : "#64748b" }}>
          {lbl}
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ display: "flex", gap: 16, height: "calc(100vh - 68px)", alignItems: "stretch",
                  maxWidth: 1400, margin: "0 auto" }}>

      {/* Panel Texto */}
      <div
        onClick={() => activePanel !== "texto" && setActivePanel("texto")}
        style={{
          flex: activePanel === "texto" ? 3 : 1,
          display: "flex", flexDirection: "column",
          borderRadius: 14,
          border: activePanel === "texto" ? "2px solid #94a3b8" : "2px solid #e2e8f0",
          background: "white", overflow: "hidden", minWidth: 0,
          boxShadow: activePanel === "texto" ? "0 4px 16px rgba(0,0,0,0.12)" : "none",
          transition: "flex 0.35s ease",
          cursor: activePanel !== "texto" ? "pointer" : "default",
        }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
                      padding: "14px 16px", borderBottom: "2px solid #e2e8f0", background: "#f8fafc",
                      flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>💬</span>
            {activePanel === "texto" && (
              <span style={{ fontWeight: 700, fontSize: 15 }}>Asistente de texto</span>
            )}
          </div>
          {activePanel === "texto" && (
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {stepBadges(texto.fase)}
              <button onClick={e => { e.stopPropagation(); texto.reiniciar(); }} title="Reiniciar"
                style={{ background: "none", border: "none", cursor: "pointer",
                         fontSize: 16, padding: "0 4px", marginLeft: 4 }}>
                🔄
              </button>
            </div>
          )}
        </div>
        {activePanel === "texto" ? (
          <>
            <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
              {texto.mensajes.map(m =>
                m.rol === "bot"
                  ? <BotBurbuja key={m.id} msg={m} onOpcion={op => texto.manejarEnvio(op)} onTTS={() => {}} />
                  : <UsuarioBurbuja key={m.id} texto={m.texto} />
              )}
              {texto.loading && (
                <div style={{ display: "flex", justifyContent: "flex-start", marginTop: 8 }}>
                  <div style={{ background: "#f1f5f9", borderRadius: 12, padding: "10px 14px",
                                fontSize: 13, color: "#64748b" }}>Procesando...</div>
                </div>
              )}
              <div ref={texto.chatEndRef} />
            </div>
            {renderInput(texto)}
          </>
        ) : (
          <div style={{ flex: 1, display: "flex", flexDirection: "column",
                        alignItems: "center", justifyContent: "center", gap: 10, padding: 16,
                        color: "#94a3b8" }}>
            <span style={{ fontSize: 32 }}>💬</span>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>Asistente de texto</div>
              <div style={{ fontSize: 11 }}>Tocá para expandir</div>
            </div>
          </div>
        )}
      </div>

      {/* Panel Voz */}
      <div
        onClick={() => activePanel !== "voz" && setActivePanel("voz")}
        style={{
          flex: activePanel === "voz" ? 3 : 1,
          display: "flex", flexDirection: "column",
          borderRadius: 14,
          border: activePanel === "voz" ? "2px solid #94a3b8" : "2px solid #e2e8f0",
          background: "white", overflow: "hidden", minWidth: 0,
          boxShadow: activePanel === "voz" ? "0 4px 16px rgba(0,0,0,0.12)" : "none",
          transition: "flex 0.35s ease",
          cursor: activePanel !== "voz" ? "pointer" : "default",
        }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
                      padding: "14px 16px", borderBottom: "2px solid #e2e8f0", background: "#f8fafc",
                      flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>🎙️</span>
            {activePanel === "voz" && (
              <span style={{ fontWeight: 700, fontSize: 15 }}>Asistente de voz</span>
            )}
          </div>
          {activePanel === "voz" && (
            <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
              {stepBadges(voz.fase)}
              <button onClick={e => { e.stopPropagation(); voz.reiniciar(); }} title="Reiniciar"
                style={{ background: "none", border: "none", cursor: "pointer",
                         fontSize: 16, padding: "0 4px", marginLeft: 4 }}>
                🔄
              </button>
            </div>
          )}
        </div>
        {activePanel === "voz" ? (
          <>
            <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
              {voz.mensajes.map(m =>
                m.rol === "bot"
                  ? <BotBurbuja key={m.id} msg={m} onOpcion={op => voz.manejarEnvio(op)} onTTS={() => {}} />
                  : <UsuarioBurbuja key={m.id} texto={m.texto} />
              )}
              {voz.loading && (
                <div style={{ display: "flex", justifyContent: "flex-start", marginTop: 8 }}>
                  <div style={{ background: "#f1f5f9", borderRadius: 12, padding: "10px 14px",
                                fontSize: 13, color: "#64748b" }}>Procesando...</div>
                </div>
              )}
              <div ref={voz.chatEndRef} />
            </div>
            <div style={{ padding: "16px", borderTop: "2px solid #e2e8f0",
                          display: "flex", flexDirection: "column", gap: 10, alignItems: "center",
                          flexShrink: 0 }}>
              {voz.fase !== "resultado" && (
                <>
                  <button onClick={e => { e.stopPropagation(); voz.iniciarVoz(); }}
                    style={{ width: 68, height: 68, borderRadius: "50%", border: "none",
                             cursor: "pointer",
                             background: voz.escuchando ? "#dc2626" : "#0f172a",
                             color: "white", fontSize: 28,
                             display: "flex", alignItems: "center", justifyContent: "center",
                             boxShadow: voz.escuchando
                               ? "0 0 0 10px #fecaca, 0 2px 8px rgba(0,0,0,0.2)"
                               : "0 4px 12px rgba(0,0,0,0.25)" }}>
                    🎙️
                  </button>
                  <span style={{ fontSize: 12, color: "#64748b", textAlign: "center" }}>
                    {voz.escuchando ? "Escuchando... tocá para detener" : "Tocá para hablar"}
                  </span>
                </>
              )}
              {voz.fase === "resultado" && (
                <button onClick={e => { e.stopPropagation(); voz.reiniciar(); }}
                  style={{ padding: "10px 24px", borderRadius: 8, border: "none",
                           background: "#0f172a", color: "white", cursor: "pointer",
                           fontSize: 14, fontWeight: 600 }}>
                  Nueva evaluación
                </button>
              )}
              <button onClick={e => { e.stopPropagation(); voz.setTtsOn(!voz.ttsOn); }}
                style={{ background: voz.ttsOn ? "#0f172a" : "#f1f5f9",
                         color: voz.ttsOn ? "white" : "#64748b",
                         border: "1px solid #cbd5e1", borderRadius: 20, padding: "5px 14px",
                         cursor: "pointer", fontSize: 12, fontWeight: 600 }}>
                {voz.ttsOn ? "🔊 Voz activada" : "🔇 Voz silenciada"}
              </button>
            </div>
          </>
        ) : (
          <div style={{ flex: 1, display: "flex", flexDirection: "column",
                        alignItems: "center", justifyContent: "center", gap: 10, padding: 16,
                        color: "#94a3b8" }}>
            <span style={{ fontSize: 32 }}>🎙️</span>
            <div style={{ textAlign: "center" }}>
              <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>Asistente de voz</div>
              <div style={{ fontSize: 11 }}>Tocá para expandir</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
'''

# Apply: keep lines 0:224, new_header, keep lines 290:641, new_tabconsulta, keep lines 853:
result = lines[0:224] + [new_header] + lines[290:641] + [new_tabconsulta] + lines[853:]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(result)

print(f"Done. New total lines: {len(result)}")
print(f"Line 225 preview: {result[224][:80].rstrip()}")
