# Replicated Inventory Lab

A small Python simulation of an inventory system with one primary replica and one secondary replica. Writes go to the primary and are then propagated to the secondary. A client can read stock from either replica.

No third-party packages are required. Python 3.9 or newer is enough.

## Run

From this directory:

```bash
python3 inventory.py
```

The program prints three sections: replication, a stale read while replication is paused, and convergence after replication resumes.

## Architecture

```text
                 read
        +----------------------+
        |                      v
   +---------+   replicate   +-----------+
   | Primary | ------------> | Secondary |
   +---------+               +-----------+
        ^                      ^
        |        read          |
        +----------------------+
                   Client
```

- The client sends inventory updates to the primary.
- The primary applies the new stock value, then propagates it to the secondary.
- The client may read from the primary or the secondary.
- While propagation is paused, the secondary keeps the last value it received.

## Evidence

Output of `python3 inventory.py`:

```text
============================================================
1. Replication
============================================================
  initial primary stock = 10
  initial secondary stock = 10
  primary received update: stock 10 -> 15
  primary stock = 15
  propagating stock = 15 to secondary
  secondary stock = 15
  client read primary: stock = 15
  client read secondary: stock = 15
  replicas match: True

============================================================
2. Stale read
============================================================
  replication paused
  primary received update: stock 10 -> 9
  primary stock = 9
  replication delayed; secondary still has the older value
  client read primary: stock = 9
  client read secondary: stock = 10
  primary returns 9
  secondary returns 10 (stale)
  stale read observed: True

============================================================
3. Recovery and convergence
============================================================
  replication resumed
  propagating stock = 9 to secondary
  secondary stock = 9
  client read primary: stock = 9
  client read secondary: stock = 9
  primary returns 9
  secondary returns 9
  replicas match: True
```

Replication: the primary accepts `stock = 15` and the secondary receives the same value. Both reads return 15.

Stale read: replication is paused and the primary is updated from 10 to 9. The primary returns 9. The secondary still returns 10.

Convergence: replication resumes, the secondary applies 9, and both replicas return 9.

## Reflection

Reading from the secondary can return as soon as that replica answers, so the client does not have to wait on the primary or on replication. That speed is possible because the secondary is allowed to lag. In the stale-read test, the secondary still reported 10 after the primary had already stored 9. A reader that needs the latest stock has to read the primary or wait until replication finishes, which adds latency. The tradeoff is between a fast reply that may be slightly old and a slower reply that is guaranteed to be current.
