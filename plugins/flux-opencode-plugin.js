// flux-opencode-plugin version: v3
// Flux Desktop plugin for OpenCode.
// Bridges OpenCode events to the Flux Desktop app via Unix socket.
import { connect } from "net";

const SOCKET_PATH =
  process.env.FLUX_SOCKET_PATH ||
  "/Users/bytedance/.flux/run/bridge.sock";

function encodeEnvelope(command) {
  return JSON.stringify({ type: "command", command }) + "\n";
}

function sendToSocket(json) {
  return new Promise((resolve) => {
    try {
      const sock = connect({ path: SOCKET_PATH });
      let buf = "";
      sock.on("data", (chunk) => {
        buf += chunk.toString();
        let start = 0;
        for (let i = 0; i < buf.length; i++) {
          if (buf[i] === "\n") {
            const line = buf.slice(start, i);
            start = i + 1;
            if (!line) continue;
            try {
              const env = JSON.parse(line);
              if (env.type === "hello") {
                sock.write(encodeEnvelope(json));
              } else if (env.type === "response") {
                sock.end();
                resolve(true);
              }
            } catch {}
          }
        }
        buf = buf.slice(start);
      });
      sock.on("end", () => resolve(true));
      sock.on("error", () => resolve(false));
      sock.setTimeout(3000, () => { sock.destroy(); resolve(false); });
    } catch { resolve(false); }
  });
}

function sendAndWaitResponse(json, timeoutMs = 300000) {
  return new Promise((resolve) => {
    try {
      const sock = connect({ path: SOCKET_PATH });
      let buf = "";
      sock.on("data", (chunk) => {
        buf += chunk.toString();
        let start = 0;
        for (let i = 0; i < buf.length; i++) {
          if (buf[i] === "\n") {
            const line = buf.slice(start, i);
            start = i + 1;
            if (!line) continue;
            try {
              const env = JSON.parse(line);
              if (env.type === "hello") {
                sock.write(encodeEnvelope(json));
              } else if (env.type === "response") {
                sock.end();
                resolve(env.response);
              }
            } catch {}
          }
        }
        buf = buf.slice(start);
      });
      sock.on("end", () => resolve(null));
      sock.on("error", () => resolve(null));
      sock.setTimeout(timeoutMs, () => { sock.destroy(); resolve(null); });
    } catch { resolve(null); }
  });
}

let detectedTty = null;
try {
  const { execSync } = require("child_process");
  let walkPid = process.pid;
  for (let i = 0; i < 8; i++) {
    const info = execSync("ps -o tty=,ppid= -p " + walkPid, { timeout: 1000 }).toString().trim();
    const parts = info.split(/\s+/);
    const tty = parts[0], ppid = parseInt(parts[1]);
    if (tty && tty !== "??" && tty !== "?") { detectedTty = "/dev/" + tty; break; }
    if (!ppid || ppid <= 1) break;
    walkPid = ppid;
  }
} catch {}

const ENV_KEYS = [
  "TERM_PROGRAM", "ITERM_SESSION_ID", "TERM_SESSION_ID",
  "TMUX", "TMUX_PANE", "KITTY_WINDOW_ID",
];

function recognizedTerminalApp(command) {
  const low = command.toLowerCase();
  if (low.includes("/opencode.app/") || low.includes("/opencode desktop.app/")) return "OpenCode";
  if (low.includes("/claude.app/")) return "Claude";
  if (low.includes("/codex.app/") || low.includes("/codex desktop.app/")) return "Codex";
  if (low.includes("/cmux.app/contents/macos/cmux")) return "cmux";
  if (low.includes("/ghostty.app/contents/macos/ghostty") || low.endsWith("/ghostty")) return "Ghostty";
  if (low.includes("/terminal.app/contents/macos/terminal")) return "Terminal";
  if (low.includes("/iterm.app/contents/macos/iterm2")) return "iTerm";
  if (low.includes("/wezterm.app/contents/macos/wezterm-gui") || low.endsWith("/wezterm-gui")) return "WezTerm";
  if (low.includes("/warp.app/") || low.endsWith("/warp")) return "Warp";
  if (low.includes("/alacritty.app/") || low.endsWith("/alacritty")) return "Alacritty";
  if (low.includes("/kitty.app/") || low.endsWith("/kitty")) return "kitty";
  if (low.includes("/cursor.app/")) return "Cursor";
  if (low.includes("/windsurf.app/")) return "Windsurf";
  if (low.includes("/trae cn - alpha.app/")) return "Trae CN - Alpha";
  if (low.includes("/trae cn.app/")) return "Trae CN";
  if (low.includes("/trae.app/")) return "Trae";
  if (low.includes("/visual studio code - insiders.app/")) return "VS Code Insiders";
  if (low.includes("/visual studio code.app/") || low.includes("/code helper")) return "VS Code";
  if ((low.includes("/intellij idea") && low.includes(".app/")) || low.includes("/idea.app/")) return "IntelliJ IDEA";
  if (low.includes("/webstorm") && low.includes(".app/")) return "WebStorm";
  if (low.includes("/pycharm") && low.includes(".app/")) return "PyCharm";
  if (low.includes("/goland") && low.includes(".app/")) return "GoLand";
  if (low.includes("/clion") && low.includes(".app/")) return "CLion";
  if (low.includes("/rubymine") && low.includes(".app/")) return "RubyMine";
  if (low.includes("/phpstorm") && low.includes(".app/")) return "PhpStorm";
  if (low.includes("/rider") && low.includes(".app/")) return "Rider";
  if (low.includes("/rustrover") && low.includes(".app/")) return "RustRover";
  return undefined;
}

function detectTerminalAppFromProcessTree() {
  try {
    const { execSync } = require("child_process");
    const raw = execSync("/bin/ps -Ao pid=,ppid=,command=", { timeout: 500, stdio: ["pipe", "pipe", "pipe"] }).toString();
    const procs = new Map();
    for (const line of raw.split("\n")) {
      const m = line.trim().match(/^(\d+)\s+(\d+)\s+(.+)$/);
      if (m) procs.set(m[1], { ppid: m[2], command: m[3] });
    }
    let pid = String(process.ppid);
    const seen = new Set();
    while (pid && pid !== "0" && pid !== "1" && !seen.has(pid)) {
      seen.add(pid);
      const p = procs.get(pid);
      if (!p) break;
      const app = recognizedTerminalApp(p.command);
      if (app) return app;
      pid = p.ppid;
    }
  } catch {}
  return undefined;
}

const TERM_PROGRAM_CANONICAL = {
  apple_terminal: "Terminal",
  "iterm.app": "iTerm",
  warpterminal: "Warp",
};

function detectTerminalApp() {
  const env = process.env;
  if (env.CMUX_SURFACE_ID) return "cmux";
  if (env.VSCODE_IPC_HOOK_CLI || env.VSCODE_PID || env.VSCODE_CWD) {
    return detectTerminalAppFromProcessTree() || "VS Code";
  }
  if (env.TERMINAL_EMULATOR === "JetBrains-JediTerm") {
    return detectTerminalAppFromProcessTree() || "IntelliJ IDEA";
  }
  const term = env.TERM_PROGRAM;
  if (term === "vscode") return detectTerminalAppFromProcessTree() || "VS Code";
  if (term) return TERM_PROGRAM_CANONICAL[term.toLowerCase()] || term;
  return detectTerminalAppFromProcessTree() || "OpenCode";
}

function terminalFields() {
  const env = process.env;
  const app = detectTerminalApp();
  const result = { pid: process.pid };
  if (app) {
    result.terminal_app = app;
    const low = app.toLowerCase();
    if (low === "iterm" && env.ITERM_SESSION_ID) {
      result.terminal_session_id = env.ITERM_SESSION_ID;
    } else if (low === "ghostty" && env.TERM_SESSION_ID) {
      result.terminal_session_id = env.TERM_SESSION_ID;
    } else if (low === "cmux" && env.CMUX_SURFACE_ID) {
      result.terminal_session_id = env.CMUX_SURFACE_ID;
    } else if (low === "kitty" && env.KITTY_WINDOW_ID) {
      result.terminal_session_id = env.KITTY_WINDOW_ID;
    }
  }
  if (detectedTty) result.terminal_tty = detectedTty;
  return result;
}

function makePayload(hookEventName, sessionID, cwd, extra = {}) {
  return {
    type: "processHook",
    source: "opencode",
    payload: {
      hook_event_name: hookEventName,
      session_id: "opencode-" + sessionID,
      cwd: cwd || ".",
      ...terminalFields(),
      ...extra,
    },
  };
}

function extractSubagentFields(p) {
    return {
        ...(p.agent_id && { agent_id: p.agent_id }),
    };
}

const LIFECYCLE_EVENTS = new Set(["SessionStart", "SessionEnd"]);

export default async ({ client, serverUrl }) => {
  const serverPort = serverUrl ? parseInt(serverUrl.port) || 4096 : 4096;
  const internalFetch = client?._client?.getConfig?.()?.fetch || null;
  const msgRoles = new Map();
  const assistantMessageParts = new Map();
  const userMessageParts = new Map();
  const sessionCwd = new Map();
  const sessions = new Map();
  const pendingRequestSessions = new Set();
  const childSessions = new Set();

  function getSession(sid) {
    if (!sessions.has(sid)) sessions.set(sid, { lastAssistantText: "", title: "" });
    return sessions.get(sid);
  }

  function clearSessionMessageState(sessionID) {
    for (const [messageID, meta] of msgRoles) {
      if (meta.sessionID !== sessionID) continue;
      msgRoles.delete(messageID);
      assistantMessageParts.delete(messageID);
      userMessageParts.delete(messageID);
    }
  }

  function upsertMessagePart(store, messageID, partID, text) {
    let parts = store.get(messageID);
    if (!parts) {
      parts = new Map();
      store.set(messageID, parts);
    }
    if (text) {
      parts.set(partID, text);
    } else {
      parts.delete(partID);
    }
    if (parts.size === 0) {
      store.delete(messageID);
      return "";
    }
    return Array.from(parts.values())
      .map((value) => String(value || "").trim())
      .filter(Boolean)
      .join("\n");
  }

  async function postPermissionReply(requestId, directive) {
    if (!requestId) return;
    const permanent = directive?.type === "allow" && directive?.permanent === true;
    const reply = directive?.type === "allow"
      ? (permanent ? "always" : "once")
      : "reject";
    const message = directive?.type === "deny" ? directive?.reason : undefined;
    const url = "http://localhost:" + serverPort + "/permission/" + requestId + "/reply";
    const body = JSON.stringify({ reply, message });
    const opts = { method: "POST", headers: { "Content-Type": "application/json" }, body };
    try {
      if (internalFetch) {
        await internalFetch(new Request(url, opts));
        return;
      }
    } catch {}
    try { await fetch(url, opts); } catch {}
  }

  async function postQuestionReply(requestId, directive) {
    if (!requestId || directive?.type !== "answer") return;
    let answers;
    if (Array.isArray(directive.answers)) {
      answers = directive.answers.map((a) => Array.isArray(a) ? a : [String(a || "")]);
    } else if (typeof directive.text === "string") {
      answers = [[directive.text]];
    } else {
      return;
    }
    const url = "http://localhost:" + serverPort + "/question/" + requestId + "/reply";
    const body = JSON.stringify({ answers });
    const opts = { method: "POST", headers: { "Content-Type": "application/json" }, body };
    try {
      if (internalFetch) {
        await internalFetch(new Request(url, opts));
        return;
      }
    } catch {}
    try { await fetch(url, opts); } catch {}
  }

  function mapEvent(ev) {
    const t = ev.type;
    const p = ev.properties || {};
    const subagentFields = extractSubagentFields(p);

    if (t === "message.part.updated" && p.part && p.part.type === "tool" && p.part.tool === "task") {
      const metadata = p.part.state?.metadata;
      if (metadata?.sessionId) {
        childSessions.add(metadata.sessionId);
      }
    }

    if (t === "session.created" && p.info && p.info.parentID) {
      childSessions.add(p.info.id);
    }

    if (p.sessionID && childSessions.has(p.sessionID)) {
      return null;
    }

    if (t === "session.created" && p.info) {
      if (childSessions.has(p.info.id)) {
        return null;
      }

      const cwd = p.info.directory || "";
      sessionCwd.set(p.info.id, cwd);
      const extra = { ...subagentFields };
      const title = p.info.title || p.info.name || '';
      if (title) {
        extra.session_title = title;
        getSession(p.info.id).title = title;
      }
      return makePayload("SessionStart", p.info.id, cwd, extra);
    }

    if (t === "session.deleted" && p.info) {
      if (childSessions.has(p.info.id)) {
        childSessions.delete(p.info.id);
        return null;
      }
      sessions.delete(p.info.id);
      const cwd = sessionCwd.get(p.info.id);
      sessionCwd.delete(p.info.id);
      clearSessionMessageState(p.info.id);
      return makePayload("SessionEnd", p.info.id, cwd, { ...subagentFields });
    }

    if (t === "session.updated" && p.info) {
      if (childSessions.has(p.info.id)) {
        return null;
      }
      if (p.info.directory) sessionCwd.set(p.info.id, p.info.directory);
      const title = p.info.title || p.info.name;
      if (title) getSession(p.info.id).title = title;

      if (p.info.time?.archived) {
        sessions.delete(p.info.id);
        const cwd = sessionCwd.get(p.info.id);
        sessionCwd.delete(p.info.id);
        clearSessionMessageState(p.info.id);
        return makePayload("SessionEnd", p.info.id, cwd, { ...subagentFields });
      }
      return null;
    }

    if (t === "session.status" && p.sessionID) {
      if (childSessions.has(p.sessionID)) {
        return null;
      }
      if (p.status?.type === "idle") {
        const s = getSession(p.sessionID);
        const extra = {
          last_assistant_message: s.lastAssistantText || undefined,
          ...subagentFields
        };
        if (s.title) extra.session_title = s.title;
        return makePayload("Stop", p.sessionID, sessionCwd.get(p.sessionID), extra);
      }
      return null;
    }

    if (t === "message.updated" && p.info?.id && p.info?.sessionID) {
      if (childSessions.has(p.info.sessionID)) {
        return null;
      }
      msgRoles.set(p.info.id, { role: p.info.role, sessionID: p.info.sessionID });
      if (msgRoles.size > 200) {
        const oldestMessageID = msgRoles.keys().next().value;
        msgRoles.delete(oldestMessageID);
        assistantMessageParts.delete(oldestMessageID);
        userMessageParts.delete(oldestMessageID);
      }
      return null;
    }

    if (t === "message.part.updated" && p.part?.type === "text" && p.part?.messageID) {
      const meta = msgRoles.get(p.part.messageID);
      if (!meta) return null;
      if (childSessions.has(meta.sessionID)) {
        return null;
      }
      const text = p.part.text || "";
      if (meta.role === "user" && text) {
        if (p.part.synthetic === true || p.part.ignored === true) return null;
        const prompt = upsertMessagePart(
          userMessageParts,
          p.part.messageID,
          p.part.id || (p.part.messageID + ":text"),
          text,
        );
        if (!prompt) return null;
        return makePayload("UserPromptSubmit", meta.sessionID, sessionCwd.get(meta.sessionID), { prompt, ...subagentFields });
      }
      if (meta.role === "assistant" && text) {
        const assistantText = upsertMessagePart(
          assistantMessageParts,
          p.part.messageID,
          p.part.id || (p.part.messageID + ":text"),
          text,
        );
        if (!assistantText) return null;
        getSession(meta.sessionID).lastAssistantText = assistantText;

        const extra = { assistant_message_preview: assistantText, ...subagentFields };
        const title = getSession(meta.sessionID).title;
        if (title) extra.session_title = title;

        return makePayload("AssistantMessageUpdate", meta.sessionID, sessionCwd.get(meta.sessionID), extra);
      }
      return null;
    }

    if (t === "message.part.updated" && p.part?.type === "tool" && p.part?.sessionID) {
      if (childSessions.has(p.part.sessionID)) {
        return null;
      }
      const st = p.part.state?.status;
      const cwd = sessionCwd.get(p.part.sessionID);
      const toolName = (p.part.tool || "").charAt(0).toUpperCase() + (p.part.tool || "").slice(1);
      if (st === "running" || st === "pending") {
        return makePayload("PreToolUse", p.part.sessionID, cwd, {
          tool_name: toolName,
          tool_input: typeof p.part.state?.input === "string"
            ? p.part.state.input
            : JSON.stringify(p.part.state?.input || {}).slice(0, 200),
          ...subagentFields
        });
      }
      if (st === "completed" || st === "error") {
        return makePayload("PostToolUse", p.part.sessionID, cwd, {
          tool_name: toolName,
          ...subagentFields
        });
      }
      return null;
    }

    if (t === "permission.asked" && p.id && p.sessionID) {
      if (childSessions.has(p.sessionID)) {
        return null;
      }
      const toolName = (p.permission || "").charAt(0).toUpperCase() + (p.permission || "").slice(1);
      const patterns = p.patterns || [];
      const toolInput = { patterns, metadata: p.metadata };
      if (p.permission === "bash" && patterns.length > 0) {
        toolInput.command = patterns.join(" && ");
      }
      if ((p.permission === "edit" || p.permission === "write") && patterns.length > 0) {
        toolInput.file_path = patterns[0];
      }
      return makePayload("PermissionRequest", p.sessionID, sessionCwd.get(p.sessionID), {
        tool_name: toolName,
        tool_input: JSON.stringify(toolInput).slice(0, 200),
        permission_id: p.id,
        permission_title: "Allow " + toolName,
        permission_description: patterns.length > 0
          ? ("OpenCode wants to run " + toolName + ": " + patterns[0])
          : ("OpenCode wants to run " + toolName),
        _opencode_request_id: p.id,
        ...subagentFields
      });
    }

    if (t === "permission.replied" && p.sessionID) {
      if (childSessions.has(p.sessionID)) {
        return null;
      }
      return makePayload("PostToolUse", p.sessionID, sessionCwd.get(p.sessionID), { ...subagentFields });
    }

    if (t === "question.asked" && p.id && p.sessionID) {
      const rawQuestions = Array.isArray(p.questions) ? p.questions : [];
      const structured = rawQuestions.map((q) => ({
        question: q.question || "",
        header: q.header || "",
        options: (q.options || []).map((opt) => ({
          label: opt.label,
          description: opt.description,
        })),
        multiple: !!q.multiple,
      }));
      const flatText = rawQuestions.map((q) => q.question).filter(Boolean).join("; ")
        || "OpenCode has a question";
      return makePayload("QuestionAsked", p.sessionID, sessionCwd.get(p.sessionID), {
        question_id: p.id,
        question_text: flatText,
        tool_input: { questions: structured },
        _opencode_request_id: p.id,
        ...subagentFields
      });
    }

    if ((t === "question.replied" || t === "question.rejected") && p.sessionID) {
      return makePayload("PostToolUse", p.sessionID, sessionCwd.get(p.sessionID), { ...subagentFields });
    }

    return null;
  }

  return {
    "event": async ({ event }) => {
      try {
        const mapped = mapEvent(event);
        if (!mapped) return;

        const hookName = mapped.payload.hook_event_name;
        const sid = mapped.payload.session_id;

        if (
          pendingRequestSessions.has(sid) &&
          !LIFECYCLE_EVENTS.has(hookName) &&
          hookName !== "PermissionRequest" &&
          hookName !== "QuestionAsked" &&
          hookName !== "PostToolUse"
        ) {
          return;
        }

        if (hookName === "PermissionRequest") {
          const requestId = mapped.payload._opencode_request_id;
          pendingRequestSessions.add(sid);
          sendAndWaitResponse(mapped)
            .then(async (response) => {
              const directive = response?.directive;
              if (directive) await postPermissionReply(requestId, directive);
            })
            .finally(() => { pendingRequestSessions.delete(sid); })
            .catch(() => {});
          return;
        }

        if (hookName === "QuestionAsked") {
          const requestId = mapped.payload._opencode_request_id;
          pendingRequestSessions.add(sid);
          sendAndWaitResponse(mapped)
            .then(async (response) => {
              const directive = response?.directive;
              if (directive) await postQuestionReply(requestId, directive);
            })
            .finally(() => { pendingRequestSessions.delete(sid); })
            .catch(() => {});
          return;
        }

        await sendToSocket(mapped);
      } catch {}
    },

    "shell.env": async (input, output) => {
      output.env.FLUX_ACTIVE = "1";
      for (const v of ENV_KEYS) {
        if (process.env[v]) output.env["_FLUX_" + v] = process.env[v];
      }
    },
  };
};
