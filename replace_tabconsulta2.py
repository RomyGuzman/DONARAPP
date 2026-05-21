path = r"c:\DONARVERSION1\frontend\app\page.tsx"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print(f"Line 635: {lines[634].rstrip()}")
print(f"Line 886: {lines[885].rstrip()}")
print(f"Line 887: {lines[886].rstrip()}")

new_tabconsulta = '''function TabConsulta({ isMobile }: { isMobile: boolean }) {
  const texto = useChatFlow({ autoTts: false });
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

  const panelStyle = {
    flex: 1, display: "flex", flexDirection: "column" as const,
    borderRadius: 14, border: "2px solid #94a3b8", background: "white",
    overflow: "hidden", minWidth: 0,
    boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
  };

  const headerStyle = {
    display: "flex", alignItems: "center", justifyContent: "space-between",
    padding: "14px 16px", borderBottom: "2px solid #e2e8f0", background: "#f8fafc",
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
    <div style={{ display: "flex", gap: 16, height: "calc(100vh - 68px)", alignItems: "stretch" }}>

      {/* Panel Texto */}
      <div style={panelStyle}>
        <div style={headerStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>💬</span>
            <span style={{ fontWeight: 700, fontSize: 15 }}>Asistente de texto</span>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            {stepBadges(texto.fase)}
            <button onClick={texto.reiniciar} title="Reiniciar"
              style={{ background: "none", border: "none", cursor: "pointer",
                       fontSize: 16, padding: "0 4px", marginLeft: 4 }}>
              🔄
            </button>
          </div>
        </div>
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
      </div>

      {/* Panel Voz */}
      <div style={panelStyle}>
        <div style={headerStyle}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ fontSize: 20 }}>🎙️</span>
            <span style={{ fontWeight: 700, fontSize: 15 }}>Asistente de voz</span>
          </div>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            {stepBadges(voz.fase)}
            <button onClick={voz.reiniciar} title="Reiniciar"
              style={{ background: "none", border: "none", cursor: "pointer",
                       fontSize: 16, padding: "0 4px", marginLeft: 4 }}>
              🔄
            </button>
          </div>
        </div>
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
                      display: "flex", flexDirection: "column", gap: 10, alignItems: "center" }}>
          {voz.fase !== "resultado" && (
            <>
              <button onClick={voz.iniciarVoz}
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
            <button onClick={voz.reiniciar}
              style={{ padding: "10px 24px", borderRadius: 8, border: "none",
                       background: "#0f172a", color: "white", cursor: "pointer",
                       fontSize: 14, fontWeight: 600 }}>
              Nueva evaluación
            </button>
          )}
          <button onClick={() => voz.setTtsOn(!voz.ttsOn)}
            style={{ background: voz.ttsOn ? "#0f172a" : "#f1f5f9",
                     color: voz.ttsOn ? "white" : "#64748b",
                     border: "1px solid #cbd5e1", borderRadius: 20, padding: "5px 14px",
                     cursor: "pointer", fontSize: 12, fontWeight: 600 }}>
            {voz.ttsOn ? "🔊 Voz activada" : "🔇 Voz silenciada"}
          </button>
        </div>
      </div>
    </div>
  );
}
'''

# Keep lines 1-634 (indices 0:634), replace 635-886 (indices 634:886), keep 887+ (indices 886:)
result = lines[0:634] + [new_tabconsulta] + lines[886:]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(result)

print(f"Done. New total lines: {len(result)}")
