import json
import os
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path

import requests

from tools.registry import all_tools, get as get_tool
from brain.routing.personas import PERSONA_DIR, load_persona
from scripts.prompt_builder import build_system_prompt
from scripts.router import detect_task
from scripts import history


BRIDGE_URL = "http://127.0.0.1:8788"

VERSION = "v0.2.0 (2026.8.18)"

# ---- responsive sizing (re-measured live, see measure()) ----
TERM_W = 96
WIDTH = 96
LEFT_W = 24
RIGHT_W = 65


def _console_width():
    if os.name != "nt":
        return None

    try:
        import ctypes
        import struct

        kernel32 = ctypes.windll.kernel32

        for handle_id in (-11, -12, -10):
            handle = kernel32.GetStdHandle(handle_id)

            if not handle or handle == -1:
                continue

            buf = ctypes.create_string_buffer(22)

            if kernel32.GetConsoleScreenBufferInfo(handle, buf):
                left, _top, right, _bottom = struct.unpack_from("<HHHH", buf.raw, 10)
                width = right - left + 1

                if width > 0:
                    return width

    except Exception:
        pass

    return None


def measure():
    global TERM_W, WIDTH, LEFT_W, RIGHT_W, COL_B, COL_C

    detected = _console_width()

    if detected:
        TERM_W = detected
    else:
        TERM_W = shutil.get_terminal_size((96, 24)).columns

    TERM_W = max(40, min(TERM_W, 400))
    WIDTH = TERM_W
    LEFT_W = max(22, min(30, WIDTH // 5))
    RIGHT_W = WIDTH - 4 - LEFT_W - 3
    COL_B = (WIDTH - 4 - LEFT_W - 2) // 2
    COL_C = WIDTH - 4 - LEFT_W - 2 - COL_B


measure()

# ---- palette (Hermes reference palette) ----
GOLD = "\033[38;2;176;138;36m"
TEXT = "\033[38;2;208;208;208m"
DIM = "\033[38;2;120;128;140m"
FAINT = "\033[38;2;104;112;128m"
BOLD = "\033[1m"
RESET = "\033[0m"

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

EMBLEM = r"""
        ╭───────╮
      ╭─┤  ◉ ◉  ├─╮
      │ ╰───┬───╯ │
      ╰─────┼─────╯
            ◉"""

def collect_personas():
    out = []

    for path in sorted(PERSONA_DIR.glob("*.md")):
        name = path.stem
        tag = ""

        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()

            if line:
                tag = (
                    line
                    .removeprefix("You are Nova's ")
                    .removesuffix(".")
                    .strip()
                )

                if tag == "You are Nova":
                    tag = "General Assistant"

                break

        out.append((name, tag))

    return out


PERSONA_KEYWORDS = {
    "debugger": ["debug", "bug", "trace", "crash", "exception", "traceback", "segfault", "stack trace"],
    "api-crafter": ["api", "endpoint", "rest", "openapi", "webhook", "curl", "json schema"],
    "test": ["test", "pytest", "unit test", "tdd", "regression", "spec"],
    "security": ["security", "vulnerability", "exploit", "cve", "attack", "harden", "xss", "injection"],
    "docs": ["document", "readme", "docstring", "documentation", "comment", "guide"],
    "data": ["data", "dataset", "csv", "pandas", "sql", "database", "analysis"],
    "refactor": ["refactor", "rewrite", "restructure", "clean up", "simplify"],
    "architect": ["architecture", "system design", "microservices", "scale", "diagram", "design"],
    "optimizer": ["optimize", "performance", "perf", "bottleneck", "latency", "slow"],
    "reviewer": ["review", "code review", "pull request"],
    "migrator": ["migrate", "migration", "upgrade", "porting", "version bump"],
    "cleaner": ["clean", "delete unused", "dead code", "tidy", "organize"],
    "mentor": ["teach", "learn", "explain to me", "guide", "beginner", "tutorial"],
    "ops": ["deploy", "docker", "kubernetes", "ci", "devops", "server", "infra"],
    "ui-ux": ["ui", "ux", "interface", "user experience", "prototype"],
    "terminal-ui": ["cli", "terminal", "command line", "tui", "shell"],
    "design-system": ["design system", "component library", "design tokens"],
    "brand": ["brand", "logo", "identity", "marketing"],
    "speed": ["quick", "fast", "brief", "short answer", "calculate"],
    "vision": ["image", "photo", "picture", "visual", "screenshot"],
    "reasoning": ["why", "explain", "analyze", "research", "compare", "strategy"],
    "nvidia-gpu": ["gpu", "cuda", "cudnn", "triton", "nvidia", "vram", "tensor core", "warp", "kernel"],
    "frontend": ["frontend", "react", "next", "tailwind", "css", "component", "html", "vue", "page", "login", "styled"],
    "backend": ["backend", "server", "auth", "middleware", "session", "oauth", "handler"],
    "database": ["sql", "query", "index", "schema", "postgres", "mysql", "normalize", "database"],
    "writer": ["email", "report", "essay", "blog post", "prose", "article", "newsletter", "cover letter"],
    "ml": ["machine learning", "fine-tune", "fine tune", "evaluate", "model training", "pytorch", "ml"],
    "translator": ["translate", "translation", "french", "spanish", "japanese", "chinese", "localize"],
    "accessibility": ["accessibility", "a11y", "wcag", "screen reader", "aria"],
    "coding": ["code", "python", "javascript", "react", "typescript", "fix", "build", "function"],
}


def _persona_matches(keyword, clean):
    if " " in keyword or len(keyword) >= 4:
        return keyword in clean

    return re.search(rf"\b{re.escape(keyword)}\b", clean) is not None


def pick_persona(prompt):
    clean = prompt.strip().lower()

    best_name = None
    best_score = 0

    for name, keywords in PERSONA_KEYWORDS.items():
        score = sum(
            1
            for keyword in keywords
            if _persona_matches(keyword, clean)
        )

        if score > best_score:
            best_score = score
            best_name = name

    if best_name:
        return best_name

    task = detect_task(prompt).get("task", "general")

    if task == "general_chat":
        return "general"

    return task


TOOL_COUNT = len(all_tools())
SKILL_COUNT = len(sorted(PERSONA_DIR.glob("*.md")))


def init_console():
    if os.name == "nt":
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()

            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            mode.value |= 0x0004
            kernel32.SetConsoleMode(handle, mode)

        except Exception:
            pass

    os.system("cls" if os.name == "nt" else "clear")


# ---- text helpers ----
def vlen(text):
    return len(ANSI_RE.sub("", text))


def render(segs):
    return "".join(fg + t + RESET for fg, t in segs)


def trunc_segs(segs, width):
    out = []
    used = 0

    for fg, text in segs:
        if used >= width:
            break

        take = min(len(text), width - used)

        out.append((fg, text[:take]))
        used += take

    return out


def line_visible(segs):
    return sum(len(t) for _, t in segs)


# ---- painters ----
def paint_plain(text="", fg=TEXT):
    print(f"{fg}{text}{RESET}")


def paint_plain_segs(segs):
    print(render(segs))


def paint_row(content):
    pad = max(0, WIDTH - 4 - vlen(content))
    print(f"{GOLD}│{RESET} {content}{' ' * pad} {GOLD}│{RESET}")


def edge():
    print(f"{GOLD}┌{'─' * (WIDTH - 2)}┐{RESET}")


def edge_bottom():
    print(f"{GOLD}└{'─' * (WIDTH - 2)}┘{RESET}")


def row(text="", fg=TEXT, bold=False):
    inner = text[: WIDTH - 4]
    style = fg + (BOLD if bold else "")
    paint_row(f"{style}{inner}{RESET}")


def full_row(segs):
    segs = trunc_segs(segs, WIDTH - 4)
    paint_row(render(segs))


def two_row(left, right):
    lw = line_visible(left)
    lpad = " " * max(0, LEFT_W - lw)

    right = trunc_segs(right, RIGHT_W)
    rw = line_visible(right)
    rpad = " " * max(0, RIGHT_W - rw)

    content = f"{render(left)}{lpad}{DIM}┊{RESET}{render(right)}{rpad}"
    paint_row(content)


def three_row(a, b, c):
    aw = line_visible(a)
    apad = " " * max(0, LEFT_W - aw)

    b = trunc_segs(b, COL_B)
    bw = line_visible(b)
    bpad = " " * max(0, COL_B - bw)

    c = trunc_segs(c, COL_C)
    cw = line_visible(c)
    cpad = " " * max(0, COL_C - cw)

    content = (
        f"{render(a)}{apad}"
        f"{DIM}┊{RESET}"
        f"{render(b)}{bpad}"
        f"{DIM}┊{RESET}"
        f"{render(c)}{cpad}"
    )
    paint_row(content)


# ---- content builders ----
def build_left(config):
    lines = []

    emblem = [
        line for line in EMBLEM.splitlines()
        if line.strip()
    ]
    emax = max(len(line) for line in emblem) if emblem else 0
    off = max(0, (LEFT_W - emax) // 2)

    for line in emblem:
        lines.append([(GOLD, " " * off + line)])

    lines.append([])

    lines.append([(GOLD, config["model_id"][:LEFT_W])])
    lines.append([(DIM, "NOVA · NVIDIA NIM"[:LEFT_W])])

    path = os.getcwd()[:LEFT_W]
    lines.append([(FAINT, path)])

    session = time.strftime("Session: %Y%m%d_%H%M%S")[:LEFT_W]
    lines.append([(FAINT, session)])

    return lines


def pack_segs(items, width):
    rows = []
    current = []
    used = 0

    for fg, text in items:
        if current and used + 2 + len(text) > width:
            rows.append(current)
            current = []
            used = 0

        if current:
            current.append((DIM, "  "))
            used += 2

        current.append((fg, text))
        used += len(text)

    if current:
        rows.append(current)

    return rows


def build_tools():
    rows = [[(GOLD + BOLD, " Available Tools")]]

    names = [(TEXT, tool.name) for tool in all_tools()]

    for packed in pack_segs(names, COL_B):
        rows.append(packed)

    return rows


def build_skills():
    personas = collect_personas()

    rows = [[(GOLD + BOLD, " Available Skills")]]

    names = [(TEXT, name) for name, _ in personas]

    for packed in pack_segs(names, COL_C):
        rows.append(packed)

    return rows


def print_header(config):
    paint_plain()

    edge()

    mid = f" Nova Agent {VERSION} "
    dashes = "─" * max(4, (WIDTH - 4 - len(mid)) // 2)
    row(f"{dashes}{mid}{dashes}", fg=GOLD, bold=True)

    paint_row("")

    left = build_left(config)
    tools = build_tools()
    skills = build_skills()

    for i in range(max(len(left), len(tools), len(skills))):
        three_row(
            left[i] if i < len(left) else [],
            tools[i] if i < len(tools) else [],
            skills[i] if i < len(skills) else [],
        )

    full_row([(GOLD, f"{TOOL_COUNT} tools · {SKILL_COUNT} skills · /help")])
    edge_bottom()

    paint_plain()
    paint_plain_segs(trunc_segs([
        (TEXT, "Welcome to Nova Agent! "),
        (DIM, "Type your message or /help for commands."),
    ], WIDTH - 1))
    paint_plain_segs(trunc_segs([
        (FAINT, "△ nova-bridge routing active · "),
        (FAINT, f"endpoint {BRIDGE_URL} · "),
        (FAINT, f"model {config['model_id']} · "),
        (FAINT, f"width {WIDTH}"),
    ], WIDTH - 1))
    paint_plain()


def print_statusbar(config, elapsed, context_tokens=0):
    ctx = f"ctx {context_tokens}k/200k" if context_tokens else "ctx —"

    paint_plain_segs([
        (DIM, "✦"),
        (GOLD, f" {config['model_id']} "),
        (DIM, "|"),
        (TEXT, f" {ctx} "),
        (DIM, "|"),
        (GOLD, " [████████████] "),
        (DIM, "|"),
        (TEXT, f" {elapsed}s"),
    ])
    paint_plain()


def print_help():
    paint_plain()
    paint_plain_segs([(GOLD, "/help"), (TEXT, "    show this message")])
    paint_plain_segs([(GOLD, "/claude"), (TEXT, "  open the full Claude Code interface")])
    paint_plain_segs([(GOLD, "exit"), (TEXT, "     leave Nova")])
    paint_plain()


def launch_claude_tui(config):
    env = os.environ.copy()

    env["ANTHROPIC_BASE_URL"] = BRIDGE_URL
    env["ANTHROPIC_API_KEY"] = "not-used"

    env["ANTHROPIC_CUSTOM_MODEL_OPTION"] = config["model_id"]
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = config["model_id"]
    env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = config["model_id"]
    env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = config["model_id"]
    env["CLAUDE_CODE_SUBAGENT_MODEL"] = config["model_id"]
    env["CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"] = "1"

    paint_plain()
    paint_plain_segs([(GOLD, ">>> Opening Claude Code...")])
    paint_plain()

    subprocess.run(
        [r"C:\Users\DELL\AppData\Roaming\npm\claude.cmd"],
        env=env,
    )


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Exact commands/paths the user approved this session are remembered,
# so repeat requests don't re-prompt.
APPROVED_SESSION = set()

STREAMING = False
PROMPT_ACTIVE = False
UI_LOCK = threading.Lock()

TOOL_SCHEMAS = {
    "filesystem": {
        "action": ("string", ["read", "write", "exists", "list", "tree", "search"]),
        "path": "string",
        "content": "string",
        "query": "string",
    },
    "web": {
        "action": ("string", ["fetch"]),
        "url": "string",
        "max_bytes": "integer",
    },
    "shell": {
        "action": ("string", ["run"]),
        "command": "string",
        "timeout": "integer",
    },
    "tasks": {
        "action": ("string", ["create", "list", "complete", "delete"]),
        "text": "string",
        "id": "integer",
    },
    "repo": {
        "action": ("string", ["status", "log", "diff", "branch"]),
        "n": "integer",
    },
    "config-manager": {
        "action": ("string", ["list", "get", "set", "prefer"]),
        "section": ("string", ["settings", "models", "providers"]),
        "key": "string",
        "value": "string",
        "mode": ("string", ["speed", "balanced", "deep"]),
    },
    "memory": {
        "action": ("string", ["remember", "recall", "forget", "all"]),
        "key": "string",
        "value": "string",
    },
    "health": {
        "action": ("string", ["overview", "model"]),
        "alias": "string",
    },
    "router": {
        "action": ("string", ["recommend", "top", "explain"]),
        "prompt": "string",
        "n": "integer",
        "alias": "string",
    },
    "github": {
        "action": ("string", ["pr_list", "pr_view", "pr_create", "issue_list", "issue_view", "issue_create", "repo"]),
        "number": "integer",
        "title": "string",
        "body": "string",
        "base": "string",
        "head": "string",
        "limit": "integer",
    },
    "sqlite": {
        "action": ("string", ["tables", "schema", "query"]),
        "path": "string",
        "sql": "string",
        "limit": "integer",
    },
    "http": {
        "action": ("string", ["request"]),
        "method": "string",
        "url": "string",
        "headers": "string",
        "body": "string",
        "timeout": "integer",
    },
    "system": {
        "action": ("string", ["overview", "cpu", "memory", "disk", "uptime"]),
    },
    "notify": {
        "action": ("string", ["send"]),
        "title": "string",
        "message": "string",
    },
    "image": {
        "action": ("string", ["info", "describe"]),
        "path": "string",
        "prompt": "string",
    },
    "json": {
        "action": ("string", ["validate", "pretty", "minify", "query"]),
        "text": "string",
        "path": "string",
        "query": "string",
    },
    "time": {
        "action": ("string", ["now", "unix", "date"]),
        "days": "number",
        "hours": "number",
        "minutes": "number",
    },
}


def anthropic_tools():
    out = []

    for tool in all_tools():
        properties = {}

        for key, spec in TOOL_SCHEMAS.get(tool.name, {}).items():
            if isinstance(spec, tuple):
                props = {"type": spec[0]}

                if len(spec) > 1:
                    props["enum"] = spec[1]

            else:
                props = {"type": spec}

            properties[key] = props

        out.append({
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                },
            },
        })

    return out


def needs_consent(name, tool_input):
    if name == "shell":
        return True

    if name == "filesystem":
        if tool_input.get("action") == "write":
            try:
                target = Path(tool_input.get("path", ".")).resolve()

            except Exception:
                return True

            return not target.is_relative_to(PROJECT_ROOT)

        return False

    return False


def approved_key(name, tool_input):
    if name == "shell":
        return ("shell", (tool_input.get("command") or "").strip())

    if name == "filesystem" and tool_input.get("action") == "write":
        try:
            return ("fs", str(Path(tool_input.get("path", ".")).resolve()))

        except Exception:
            return None

    return None


def ask_consent(name, tool_input):
    if not needs_consent(name, tool_input):
        return True

    key = approved_key(name, tool_input)

    if key in APPROVED_SESSION:
        print(f"  {DIM}[approved earlier this session]{RESET}")
        return True

    print()
    print(f"  {GOLD}⚠ Nova wants to run: {TEXT}{name}{RESET}")

    if name == "shell":
        print(f"  {FAINT}{tool_input.get('command', '')}{RESET}")

    print(f"  {DIM}Allow? [y/N] {RESET}", end="", flush=True)

    try:
        answer = input().strip().lower()

    except (KeyboardInterrupt, EOFError):
        answer = ""

    if answer in {"y", "yes"}:
        if key is not None:
            APPROVED_SESSION.add(key)
        return True

    return False


def execute_tool(name, tool_input):
    tool = get_tool(name)

    if tool is None:
        return f"Unknown tool: {name}"

    try:
        return str(tool.run(**tool_input))

    except Exception as exc:
        return f"Tool error: {exc}"


def send(payload):
    response = requests.post(
        BRIDGE_URL + "/v1/messages",
        json=payload,
        timeout=300,
        stream=True,
    )

    response.encoding = "utf-8"

    if response.status_code != 200:
        try:
            detail = response.json()
            msg = detail.get("error", {}).get("message", str(detail))
        except ValueError:
            msg = response.text

        paint_plain_segs([(TEXT, f"❌ {msg}")])
        return "", []

    reply = []
    tool_open = {}

    for raw in response.iter_lines(decode_unicode=True):
        if not raw or not raw.startswith("data:"):
            continue

        line = raw[5:].strip()

        if not line:
            continue

        try:
            event = json.loads(line)
        except ValueError:
            continue

        etype = event.get("type")

        if etype == "content_block_start":
            block = event.get("content_block", {})

            if block.get("type") == "tool_use":
                idx = event.get("index")

                tool_open[idx] = {
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "args": "",
                }

        elif etype == "content_block_delta":
            delta = event.get("delta", {})

            if delta.get("type") == "text_delta":
                text = delta.get("text", "")
                reply.append(text)
                print(text, end="", flush=True)

            elif delta.get("type") == "input_json_delta":
                idx = event.get("index")

                if idx in tool_open:
                    tool_open[idx]["args"] += delta.get("partial_json", "")

        elif etype == "message_stop":
            break

    tool_blocks = []

    for idx in tool_open:
        entry = tool_open[idx]

        try:
            tool_input = (
                json.loads(entry["args"]) if entry["args"].strip() else {}
            )

        except ValueError:
            tool_input = {}

        tool_blocks.append({
            "id": entry["id"],
            "name": entry["name"],
            "input": tool_input,
        })

    print()
    return "".join(reply), tool_blocks


def run_turn(config, conversation):
    global STREAMING

    rounds = 0

    with UI_LOCK:
        STREAMING = True

    try:
        prompt_text = ""

        for msg in reversed(conversation):
            if (
                msg.get("role") == "user"
                and isinstance(msg.get("content"), str)
            ):
                prompt_text = msg["content"]
                break

        persona_name = pick_persona(prompt_text) if prompt_text else "general"
        persona = load_persona(persona_name)

        if persona_name != "general":
            paint_plain_segs([(DIM, f"◈ persona: {persona_name}")])

        while True:
            rounds += 1

            if rounds > 15:
                print(f"  {DIM}[stopping after 15 tool rounds]{RESET}")
                break

            payload = {
                "model": config["model_id"],
                "system": persona,
                "messages": conversation,
                "tools": anthropic_tools(),
                "max_tokens": 8192,
                "stream": True,
            }

            reply, tool_blocks = send(payload)

            if not tool_blocks:
                if reply:
                    conversation.append(
                        {
                            "role": "assistant",
                            "content": reply,
                        }
                    )

                return reply

            assistant_blocks = []

            if reply:
                assistant_blocks.append(
                    {"type": "text", "text": reply}
                )

            for block in tool_blocks:
                assistant_blocks.append(
                    {
                        "type": "tool_use",
                        "id": block["id"],
                        "name": block["name"],
                        "input": block["input"],
                    }
                )

            conversation.append(
                {
                    "role": "assistant",
                    "content": assistant_blocks,
                }
            )

            tool_results = []

            for block in tool_blocks:
                allowed = ask_consent(block["name"], block["input"])

                if allowed:
                    result = execute_tool(block["name"], block["input"])

                else:
                    result = "User denied permission for this tool call."

                short = " ".join(result.split())

                if len(short) > 120:
                    short = short[:120] + "…"

                paint_plain_segs([
                    (GOLD, f"[{block['name']}] "),
                    (FAINT, short),
                ])

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": result,
                    }
                )

            conversation.append(
                {
                    "role": "user",
                    "content": tool_results,
                }
            )

    finally:
        with UI_LOCK:
            STREAMING = False


def estimate_tokens(conversation):
    raw = json.dumps(conversation)
    return max(1, len(raw) // 4 // 1000)


def _resize_watcher(config, transcript):
    last = WIDTH

    while True:
        time.sleep(0.4)

        with UI_LOCK:
            measure()
            changed = WIDTH != last
            last = WIDTH

            if changed and not STREAMING:
                redraw(config, transcript)

                if PROMPT_ACTIVE:
                    print(f"{GOLD}> {RESET}", end="", flush=True)


def redraw(config, transcript):
    init_console()
    measure()
    print_header(config)

    for role, text in transcript:
        if role == "user":
            paint_plain_segs([(GOLD, f"> {text}")])

        elif role == "tool":
            paint_plain_segs([(FAINT, text)])

        else:
            paint_plain_segs([(TEXT, text)])

    paint_plain()


def run_chat(config):
    global PROMPT_ACTIVE

    init_console()

    measure()
    print_header(config)

    last_width = WIDTH

    transcript = []

    threading.Thread(
        target=_resize_watcher,
        args=(config, transcript),
        daemon=True,
    ).start()

    conversation = [
        {
            "role": "system",
            "content": build_system_prompt(),
        }
    ]

    while True:
        measure()

        if WIDTH != last_width:
            last_width = WIDTH
            redraw(config, transcript)

        try:
            with UI_LOCK:
                PROMPT_ACTIVE = True

            prompt = input(f"{GOLD}> {RESET}")

        except (KeyboardInterrupt, EOFError):
            print()
            print("Goodbye.")
            break

        finally:
            with UI_LOCK:
                PROMPT_ACTIVE = False

        prompt = prompt.strip()

        if not prompt:
            continue

        command = prompt.lower()

        if command in {"exit", "quit", "/exit"}:
            print()
            print("Goodbye.")
            break

        if command == "/help":
            print_help()
            continue

        if command == "/claude":
            launch_claude_tui(config)
            continue

        transcript.append(("user", prompt))

        conversation.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        history.add("user", prompt)

        start = time.perf_counter()

        reply = run_turn(config, conversation)

        elapsed = round(time.perf_counter() - start)

        if reply:
            transcript.append(("assistant", reply))
            history.add("assistant", reply)

        print_statusbar(
            config,
            elapsed,
            estimate_tokens(conversation),
        )