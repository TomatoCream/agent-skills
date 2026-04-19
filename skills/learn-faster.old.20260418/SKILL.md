# learn-faster

Use when the user wants to learn a new topic using the FASTER framework (spaced repetition + active practice).

## Setup

```bash
# Clone the repo if not already present
git clone https://github.com/TomatoCream/learn-faster-kit.git /tmp/learn-faster-kit

# Checkout the feat/opencode-support branch (contains opencode agent support)
git checkout feat/opencode-support

# Install via uv
uv tool install -e .
```

## Usage

```bash
# Create a learning directory and launch learn-faster with opencode agent
mkdir -p "/tmp/learn-faster-kit/<topic name>"
cd "/tmp/learn-faster-kit/<topic name>"
learn-faster --agent opencode
```

Then interact with the OpenCode TUI to learn the topic.

## Tips

- Each topic should have its own subdirectory inside `/tmp/learn-faster-kit/`
- The tool will ask about experience level and create a personalized syllabus
- It's a TUI app — the user interacts with it directly via keyboard
- On Telegram/group chat, the TUI output won't be visible — just relay key info and let the user know it's running
