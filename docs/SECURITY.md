# M.A.N.T.I.S. — Security Model & Key Management

> How M.A.N.T.I.S. handles private keys and what threat model we've designed against.

---

## Core Security Principle: Encrypted Server-Side Key Custody

**Your Hedera private key is stored in an encrypted, access-controlled cloud secret store — never in plaintext, never exposed to the dashboard or any external interface.**

M.A.N.T.I.S. is a hosted service. Private keys are managed server-side using industry-standard secret management infrastructure (AWS Secrets Manager / HashiCorp Vault). The Hedera Agent Kit signs transactions on the server using the stored key. Only the already-signed transaction bytes are transmitted to the Hedera network.

```
Hosted Server:
  [Encrypted Secret Store] → [Hedera Agent Kit] → [Signed Tx Bytes]
                                                          │
                                                          ▼
                                                Hedera Network RPC
                                               (signed bytes only)
```

Your private key is **never serialized in logs, responses, or dashboard output.**

---

## Threat Model

| Threat | Mitigation |
|---|---|
| Key exfiltration via logs | Keys never written to logs or API responses |
| Key in plaintext storage | Encrypted at rest in secret store (AES-256) |
| Malicious Skill plugin | Review all Skill code before enabling. Sandboxing roadmapped. |
| Rogue LLM output (prompt injection) | Guard layer validates all LLM action plans before execution |
| Unauthorised dashboard access | Authentication layer required to access dashboard controls |
| Transaction replay attacks | Hedera transaction IDs are time-bound; replays are rejected by network |
| Supply chain attack on dependencies | Pinned dependency versions; regular audit schedule |

---

## Secret Management

Private keys and sensitive credentials are stored in the server-side secret store — not in environment files or application config:

| Secret | Storage |
|---|---|
| `HEDERA_PRIVATE_KEY` | Encrypted secret store (AWS Secrets Manager / HashiCorp Vault) |
| LLM API keys | Encrypted secret store |
| Oracle API keys | Encrypted secret store |

### Key Rotation

Keys can be rotated via the secret store's native rotation mechanism without redeploying the agent. The agent fetches the current key value at startup and on each signing operation.

---

## Permission Scoping

M.A.N.T.I.S. requires the minimum necessary permissions to operate:

| Service | Permission Required | Why |
|---|---|---|
| Twitter API | Read-only | Sentiment scanning only |
| CryptoPanic API | Read-only | News feed ingestion |
| Hedera Account | Sign transactions | Vault operations |
| Bonzo Vault | Rebalance, Harvest, Withdraw | DeFi operations |

**The agent has no database admin access, no admin rights beyond its own account, and no access to other wallets.**

---

## Transaction Authorization Model

Every Hedera transaction submitted by M.A.N.T.I.S. is:

1. **Built** by the Hedera Skill using the Bonzo Vault ABI
2. **Validated** by the Guard layer (precondition checks)
3. **Signed** server-side using the key retrieved from the encrypted secret store
4. **Broadcast** to the Hedera network
5. **Confirmed** by awaiting receipt from a mirror node
6. **Logged** to the dashboard audit log with the Hedera Transaction ID

All transactions are publicly auditable on [HashScan](https://hashscan.io) using your account ID.

---

## Audit Logging

M.A.N.T.I.S. keeps a server-side audit log of all actions:

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

A summary view of these logs is surfaced in the web dashboard.

---

## Responsible Disclosure

If you discover a security vulnerability in M.A.N.T.I.S., please report it privately to the maintainers before public disclosure. Do not open a public GitHub issue for security vulnerabilities.

Contact: security@elykid.com
