# Replicated Inventory

## Run

```bash
python3 inventory.py
```

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

The client writes to the primary. The primary propagates the new stock value to the secondary. The client can read from either replica.

## Replication

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
```

The primary receives 15, the secondary receives 15, and both reads return 15.

## Stale read

```text
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
```

Replication is paused. The primary returns 9. The secondary still returns 10.

## Recovery and convergence

```text
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

After replication resumes, the secondary updates to 9 and both replicas return 9.

## Reflection

Reading from the secondary can return as soon as that replica answers, so the client does not have to wait on the primary or on replication. That speed is possible because the secondary is allowed to lag. In the stale-read test, the secondary still reported 10 after the primary had already stored 9. A reader that needs the latest stock has to read the primary or wait until replication finishes, which adds latency. The tradeoff is between a fast reply that may be slightly old and a slower reply that is guaranteed to be current.
