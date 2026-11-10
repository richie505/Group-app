"""Talks to the PYQ key-checking Managed Agent: starts a session, sends one message, prints the agent's reply as it
streams, and stops when the agent goes idle.

    pip install anthropic
    export ANTHROPIC_API_KEY=...            (or run `ant auth login` once)
    python3 tools/key_agent.py "Check the key of this PYQ: ..."
    python3 tools/key_agent.py < message.txt

Exit status: 0 when the agent finished, 1 on an error (API error, session error, or the session ended badly).
"""
import os
import sys

import anthropic

AGENT_ID = "agent_015TZopYZonR8mFCtQS1RCQc"
ENVIRONMENT_ID = "env_01W7iqhpLRpBVnT6VZF4TbfQ"


def run(text: str) -> int:
    # ANTHROPIC_API_KEY, or a variable named "key" as set in the cloud environment's settings
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("key"))
    session = client.beta.sessions.create(agent=AGENT_ID, environment_id=ENVIRONMENT_ID)
    print(f"[session {session.id}]", file=sys.stderr)

    failed = False
    # stream first, then send: the stream only carries events that happen after it opens
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message", "content": [{"type": "text", "text": text}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                for block in event.content:
                    if block.type == "text":
                        print(block.text, end="", flush=True)
            elif event.type == "session.error":
                failed = True
                print(f"\n[error: {event.error.type}: {getattr(event.error, 'message', '')}]", file=sys.stderr)
            elif event.type == "session.status_idle":
                if event.stop_reason.type == "requires_action":
                    # the agent wants a tool approval or a custom tool result this script does not give
                    print(f"\n[agent is waiting for action: {event.stop_reason}]", file=sys.stderr)
                    failed = True
                break
            elif event.type == "session.status_terminated":
                print("\n[session terminated]", file=sys.stderr)
                break
    print()
    return 1 if failed else 0


def main() -> int:
    text = " ".join(sys.argv[1:]).strip() or sys.stdin.read().strip()
    if not text:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        return run(text)
    except anthropic.AuthenticationError:
        print("No valid API key: set ANTHROPIC_API_KEY or run `ant auth login`.", file=sys.stderr)
    except anthropic.NotFoundError as e:
        print(f"Agent or environment not found: {e.message}", file=sys.stderr)
    except anthropic.RateLimitError:
        print("Rate limited: try again in a minute.", file=sys.stderr)
    except anthropic.APIStatusError as e:
        print(f"API error {e.status_code}: {e.message}", file=sys.stderr)
    except anthropic.APIConnectionError as e:
        print(f"Could not reach the API: {e}", file=sys.stderr)
    except KeyboardInterrupt:
        print("\n[stopped]", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
