# M.A.N.T.I.S. — Security Model & Key Management

> How M.A.N.T.I.S. handles your private keys and what threat model we've designed against.

---

## Core Security Principle: Local-Only Key Custody

**Your Hedera private key never leaves your machine.**

Unlike cloud-based DeFi bots that require uploading private keys to a web server or database, M.A.N.T.I.S. is designed to run **locally on hardware you control**. The Hedera Agent Kit signs transactions using your local private key. Only the already-signed transaction bytes are transmitted to the Hedera network.

```
Your Machine:
  [Private Key] + [Unsigned Tx] → [Hedera Agent Kit] → [Signed Tx Bytes]
                                                               │
                                                               ▼
                                                     Hedera Network RPC
                                                    (signed bytes only)
```

Your private key is **never serialized, transmitted, or logged.**

---

## Threat Model

| Threat | Mitigation |
|---|---|
| Key exfiltration via cloud | Agent runs entirely locally. No key upload. |
| Key in plaintext `.env` | Use OS keychain or env file with restricted permissions (`chmod 600 .env`) |
| Malicious Skill plugin | Review all Skill code before enabling. Sandboxing roadmapped. |
| Rogue LLM output (prompt injection) | Guard layer validates all LLM action plans before execution |
| Telegram message interception | Use Telegram's E2E encrypted Secret Chats or Signal channel |
| Unauthorized agent access (local) | Run agent under a dedicated OS user with minimal permissions |
| Transaction replay attacks | Hedera transaction IDs are time-bound; replays are rejected by network |

---

## `.env` File Security

### Recommended Permissions

After creating your `.env`:

```bash
chmod 600 .env
chown $USER .env
```

This ensures only your user account can read the file.

### Never Do This

```bash
# ❌ Never commit .env to git
git add .env

# ❌ Never share .env in Telegram, Discord, or email
# ❌ Never paste private keys into LLM chat interfaces
# ❌ Never store .env in a cloud drive (iCloud, Dropbox, Google Drive)
```

The `.gitignore` in this repo already excludes `.env`.

---

## Advanced: OS Keychain Integration (Recommended for Production)

Instead of storing `HEDERA_PRIVATE_KEY` in a plaintext `.env`, use your operating system's keychain:

### macOS (Keychain Access)

```bash
# Store key
security add-generic-password -a "mantis" -s "hedera-private-key" -w "302e..."

# Retrieve key at runtime (in your shell profile or startup script)
export HEDERA_PRIVATE_KEY=$(security find-generic-password -a "mantis" -s "hedera-private-key" -w)
```

### Linux (Secret Service / `pass`)

```bash
# Using `pass` (GPG-encrypted password store)
pass insert mantis/hedera-private-key

# Retrieve
export HEDERA_PRIVATE_KEY=$(pass mantis/hedera-private-key)
```

---

## Permission Scoping

M.A.N.T.I.S. requires the minimum necessary permissions to operate:

| Service | Permission Required | Why |
|---|---|---|
| Twitter API | Read-only | Sentiment scanning only |
| CryptoPanic API | Read-only | News feed ingestion |
| Telegram Bot | Send + Receive messages | Alerts + commands |
| Hedera Account | Sign transactions | Vault operations |
| Bonzo Vault | Rebalance, Harvest, Withdraw | DeFi operations |

**The agent has no database access, no admin rights, and no access to other wallets.**

---

## Transaction Authorization Model

Every Hedera transaction submitted by M.A.N.T.I.S. is:

1. **Built** by the Hedera Skill using the Bonzo Vault ABI
2. **Validated** by the Guard layer (precondition checks)
3. **Signed** locally using `HEDERA_PRIVATE_KEY`
4. **Broadcast** to the Hedera network
5. **Confirmed** by awaiting receipt from a mirror node
6. **Logged** to local state with the Hedera Transaction ID

All transactions are publicly auditable on [HashScan](https://hashscan.io) using your account ID.

---

## Audit Logging

M.A.N.T.I.S. keeps a local audit log of all actions:

```
logs/
├── agent.log          # All decision loop events
├── transactions.log   # All on-chain transactions (ID, action, timestamp)
└── errors.log         # Error events and stack traces
```

Example `transactions.log` entry:
```
2025-03-17T14:05:22Z | WIDEN_RANGE | vault:0.0.1234567 | tx:0.0.1234567@1710000000.000000000 | reason:"vol=0.82,sentiment=-0.62"
```

---

## Responsible Disclosure

If you discover a security vulnerability in M.A.N.T.I.S., please report it privately to the maintainers before public disclosure. Do not open a public GitHub issue for security vulnerabilities.

Contact: security@elykid.com
