import sys

path = r"c:\DONARVERSION1\frontend\app\page.tsx"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print(f"Line 601: {lines[600].rstrip()}")
print(f"Line 602: {lines[601].rstrip()}")
print(f"Line 1219: {lines[1218].rstrip()}")
print(f"Line 1220: {lines[1219].rstrip()}")

new_body = '''  const texto = useChatFlow({ autoTts: false });
  const voz   = useChatFlow({ autoTts: true });

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
      <div style={{ display: "flex", gap: 8, padding: "12px 16px", borderTop: "1px solid #e2e8f0" }}>
        {["Masculino","Femenino","Otro"].map(s => (
          <button key={s} onClick={() => chat.seleccionarOpcion(s)}
            style={{ flex: 1, padding: "10px 4px", borderRadius: 8,
                     border: "1px solid #e2e8f0", background: "#f8fafc",
                     cursor: "pointer", fontSize: 13, fontWeight: 600 }}>
            {s}
          </button>
        ))}
      </div>
    );

    if (fase === "resultado") return (
      <div style={{ display: "flex", justifyContent: "center", padding: "12px 16px", borderTop: "1px solid #e2e8f0" }}>
        <button onClick={chat.reiniciar}
          style={{ padding: "10px 24px", borderRadius: 8, border: "none",
                   background: "#0f172a", color: "white", cursor: "pointer",
                   fontSize: 14, fontWeight: 600 }}>
          Nueva evaluación
        </button>
      </div>
    );

    if (BOOL_FASES.includes(fase)) return (
      <div style={{ display: "flex", gap: 8, padding: "12px 16px", borderTop: "1px solid #e2e8f0" }}>
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
                    borderTop: "1px solid #e2e8f0", gap: 6 }}>
        {inputError && <div style={{ fontSize: 12, color: "#dc2626" }}>{inputError}</div>}
        <div style={{ display: "flex", gap: 8 }}>
          <input value={input}
            onChange={e => { setInput(e.target.value); setInputError(""); }}
            onKeyDown={e => { if (e.key === "Enter" && !loading) manejarEnvio(input); }}
            placeholder={chat.placeholder} disabled={loading}
            style={{ flex: 1, padding: "10px 12px", borderRadius: 8,
                     border: inputError ? "1px solid #dc2626" : "1px solid #e2e8f0",
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

  const SIDEBAR_ITEMS = [
    { icon: "🩸", t: "¿Por qué donar?", d: "Tu donación puede salvar hasta 4 vidas." },
    { icon: "📋", t: "Requisitos generales", d: "16-65 años, +50 kg y buen estado de salud." },
    { icon: "⏱️", t: "Duración", d: "El proceso dura entre 45 minutos y 1 hora." },
    { icon: "💧", t: "Antes de donar", d: "Hidratate bien y comé algo liviano." },
    { icon: "🏥", t: "Instituto PBA", d: "La evaluación final la realiza el personal médico." },
  ];

  return (
    <div style={{ display: "flex", gap: 14, height: "calc(100vh - 108px)", alignItems: "stretch" }}>

      {/* Sidebar */}
      {!isMobile && (
        <div style={{ width: 210, flexShrink: 0, display: "flex", flexDirection: "column", gap: 10, overflowY: "auto" }}>
          {SIDEBAR_ITEMS.map((it, i) => (
            <div key={i} style={{ background: "white", borderRadius: 12,
                                  border: "1px solid #e2e8f0", padding: "12px 14px",
                                  display: "flex", gap: 10, alignItems: "flex-start" }}>
              <span style={{ fontSize: 22 }}>{it.icon}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 12, color: "#0f172a", marginBottom: 2 }}>{it.t}</div>
                <div style={{ fontSize: 11, color: "#64748b", lineHeight: 1.5 }}>{it.d}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Panel Texto */}
      <div style={{ flex: voiceActive ? 1 : 2, display: "flex", flexDirection: "column",
                    borderRadius: 12, border: "1px solid #e2e8f0", background: "white",
                    overflow: "hidden", transition: "flex 0.4s ease", minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
                      padding: "14px 16px", borderBottom: "1px solid #e2e8f0", background: "#f8fafc" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>💬</span>
            <span style={{ fontWeight: 700, fontSize: 15 }}>Asistente de texto</span>
          </div>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            {["Datos","Preguntas","Resultado"].map((lbl, i) => (
              <div key={i} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 20, fontWeight: 600,
                                    background: etapaIdx(texto.fase) === i ? "#0f172a" : "#f1f5f9",
                                    color: etapaIdx(texto.fase) === i ? "white" : "#64748b" }}>
                {lbl}
              </div>
            ))}
            <button onClick={texto.reiniciar} title="Reiniciar"
              style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, padding: "0 4px" }}>
              🔄
            </button>
          </div>
        </div>
        <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
          {texto.mensajes.map(m =>
            m.rol === "bot"
              ? <BotBurbuja key={m.id} texto={m.texto} consulta={m.consulta} />
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
      </div>

      {/* Panel Voz */}
      <div onClick={() => !voiceActive && setVoiceActive(true)}
        style={{ flex: voiceActive ? 2 : 1, display: "flex", flexDirection: "column",
                 borderRadius: 12, border: "1px solid #e2e8f0", background: "white",
                 overflow: "hidden", transition: "flex 0.4s ease", minWidth: 0,
                 cursor: voiceActive ? "default" : "pointer" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between",
                      padding: "14px 16px", borderBottom: "1px solid #e2e8f0", background: "#f8fafc" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>🎙️</span>
            <span style={{ fontWeight: 700, fontSize: 15 }}>Asistente de voz</span>
          </div>
          {voiceActive && (
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              {["Datos","Preguntas","Resultado"].map((lbl, i) => (
                <div key={i} style={{ fontSize: 11, padding: "2px 8px", borderRadius: 20, fontWeight: 600,
                                      background: etapaIdx(voz.fase) === i ? "#0f172a" : "#f1f5f9",
                                      color: etapaIdx(voz.fase) === i ? "white" : "#64748b" }}>
                  {lbl}
                </div>
              ))}
              <button onClick={e => { e.stopPropagation(); voz.reiniciar(); }} title="Reiniciar"
                style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, padding: "0 4px" }}>
                🔄
              </button>
              <button onClick={e => { e.stopPropagation(); setVoiceActive(false); }} title="Colapsar"
                style={{ background: "none", border: "none", cursor: "pointer", fontSize: 16, padding: "0 4px" }}>
                ✕
              </button>
            </div>
          )}
        </div>

        {voiceActive ? (
          <>
            <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
              {voz.mensajes.map(m =>
                m.rol === "bot"
                  ? <BotBurbuja key={m.id} texto={m.texto} consulta={m.consulta} />
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
            <div style={{ padding: "12px 16px", borderTop: "1px solid #e2e8f0",
                          display: "flex", flexDirection: "column", gap: 8, alignItems: "center" }}>
              {voz.fase !== "resultado" && (
                <>
                  <button onClick={e => { e.stopPropagation(); voz.iniciarVoz(); }}
                    style={{ width: 64, height: 64, borderRadius: "50%", border: "none",
                             cursor: "pointer",
                             background: voz.escuchando ? "#dc2626" : "#0f172a",
                             color: "white", fontSize: 28,
                             display: "flex", alignItems: "center", justifyContent: "center",
                             boxShadow: voz.escuchando ? "0 0 0 8px #fecaca" : "0 2px 8px rgba(0,0,0,0.2)" }}>
                    🎙️
                  </button>
                  <span style={{ fontSize: 12, color: "#64748b" }}>
                    {voz.escuchando ? "Escuchando... (tocá para detener)" : "Tocá para hablar"}
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
                         border: "none", borderRadius: 6, padding: "4px 10px",
                         cursor: "pointer", fontSize: 12, fontWeight: 600 }}>
                {voz.ttsOn ? "🔊 Voz activada" : "🔇 Voz silenciada"}
              </button>
            </div>
          </>
        ) : (
          <div style={{ flex: 1, display: "flex", flexDirection: "column",
                        alignItems: "center", justifyContent: "center", gap: 12, padding: 24 }}>
            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#f1f5f9",
                          display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>
              🎙️
            </div>
            <div style={{ fontSize: 13, color: "#64748b", textAlign: "center", lineHeight: 1.5 }}>
              Tocá para expandir el asistente de voz
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
'''

# lines[0:601]  = keep lines 1-601
# new_body       = replacement for lines 602-1219
# lines[1219:]  = keep lines 1220+
result = lines[0:601] + [new_body] + lines[1219:]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(result)

print(f"Done. New total lines: {len(result)}")
print(f"New line 602 preview: {result[601][:80].rstrip()}")
