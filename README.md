# 🚀 Nova

> A lightweight CLI for launching Claude Code with configurable AI providers and models.

Nova simplifies working with Claude Code by handling model selection, configuration, and startup through a single command.

---

## ✨ Features

- 🚀 Launch Claude Code with a single command
- 🤖 Configurable AI models
- 🔌 NVIDIA NIM integration
- ⚙️ JSON-based configuration
- 📦 Simple installation
- 🖥️ Cross-platform (Windows support today, more to come)

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/Ayomi789/Nova.git
cd Nova
```

Install Nova:

```bash
pip install -e .
```

---

## 🚀 Usage

Launch Claude Code using your configured default model:

```bash
nova
```

Current default model:

```text
z-ai/glm-5.2
```

---

## 📁 Project Structure

```
Nova/
├── config/
│   ├── models.json
│   ├── secrets.json
│   └── settings.json
│
├── scripts/
│   ├── launcher.py
│   ├── checks.py
│   ├── config.py
│   └── proxy.py
│
├── launcher.py
├── pyproject.toml
└── README.md
```

---

## 🛣️ Roadmap

### ✅ v0.1.0
- CLI launcher
- NVIDIA NIM support
- Configurable models
- GitHub release
- JSON configuration

### 🚧 v0.2.0
- `nova doctor`
- `nova models`
- `nova use`

### 🔮 Future
- OpenRouter support
- Ollama support
- Interactive terminal UI
- Plugin system
- Auto update

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

If you have an idea that improves Nova, feel free to open an issue or submit a pull request.

---

## 📄 License

MIT License

(License file coming soon.)