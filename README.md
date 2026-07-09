# ArtemOnus Agent

> On-chain AI agent anchored to **artemonus.eth**

An autonomous on-chain agent deployed on Base mainnet. Monitors ETH/USD price via Chainlink, records observations, and creates tasks — all governed by a Safe multisig for accountable, non-upgradeable control.

---

## Identity

| Field | Value |
|-------|-------|
| ENS Name | `artemonus.eth` |
| Agent Type | AI Price Observer |
| Version | 1.0.0 |
| Network | Base mainnet |
| Veral Score | [artemonus.eth on Veral](https://veral.tech/b/artemonus.eth) |

---

## Deployed Contracts

### Base Mainnet

| Contract | Address |
|----------|---------|
| ArtemOnusAgent | [`0x7bDaD7145Be9B696459643dAd13c0dfBad5e5d49`](https://basescan.org/address/0x7bDaD7145Be9B696459643dAd13c0dfBad5e5d49) |
| Safe Multisig (owner) | [`0x2626AC38bf07e8b7b2986026a12A3c7E441FB643`](https://basescan.org/address/0x2626AC38bf07e8b7b2986026a12A3c7E441FB643) |

**Verification:** [Sourcify](https://sourcify.dev/#/lookup/0x7bDaD7145Be9B696459643dAd13c0dfBad5e5d49) · [Basescan](https://basescan.org/address/0x7bDaD7145Be9B696459643dAd13c0dfBad5e5d49#code)

---

## Architecture

```
artemonus.eth  ──ENS──▶  0x55e5fa8F62Dc38c3A4aCE67909A7849e5B1448bF
                                        │ owns
                                        ▼
                          Safe Multisig (1/1)
                          0x2626AC38bf07e8b7b2986026a12A3c7E441FB643
                                        │ owner
                                        ▼
                          ArtemOnusAgent.sol
                          0x7bDaD7145Be9B696459643dAd13c0dfBad5e5d49
                                        │ reads
                                        ▼
                          Chainlink ETH/USD Feed
                          0x71041dddad3595F9CEd3DcCFBe3D1F4b0a16Bb70
```

---

## What It Does

- **`recordObservation(string note)`** — logs an on-chain observation (only Safe owner)
- **`createTask(string description)`** — creates a trackable on-chain task (only Safe owner)
- **`getLatestPrice()`** — reads live ETH/USD from Chainlink (anyone can call)
- **`transferOwnership(address)`** — transfers control (only Safe owner)

---

## Security

- **Owner**: Safe multisig (`0x2626AC38...FB643`) — not a lone EOA
- **No proxy / no upgradeability** — code is immutable after deploy
- **Chainlink oracle** — no self-reported price data
- **Verified source**: Sourcify + Basescan Exact Match

---

## Operator

**Artem Starokozhko** · ENS: `artemonus.eth`
Prague · Economics & Management in Sport · PM & Web3

GitHub: [@Artemstar](https://github.com/Artemstar)
