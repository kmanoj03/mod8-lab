"""Replicated inventory: one primary, one secondary, and a client.

Updates are applied on the primary and then propagated to the secondary.
Replication can be paused so a read against the secondary returns a stale value.
"""

from __future__ import annotations


class Replica:
    def __init__(self, name: str, stock: int) -> None:
        self.name = name
        self.stock = stock

    def apply(self, stock: int) -> None:
        self.stock = stock


class Client:
    """Reads inventory from whichever replica the caller names."""

    def read(self, replica: Replica) -> int:
        print(f"  client read {replica.name}: stock = {replica.stock}")
        return replica.stock


class InventorySystem:
    def __init__(self, stock: int = 10) -> None:
        self.primary = Replica("primary", stock)
        self.secondary = Replica("secondary", stock)
        self.client = Client()
        self.replication_paused = False
        self._pending: int | None = None

    def update(self, stock: int) -> None:
        previous = self.primary.stock
        self.primary.apply(stock)
        print(f"  primary received update: stock {previous} -> {stock}")
        print(f"  primary stock = {self.primary.stock}")
        if self.replication_paused:
            self._pending = stock
            print("  replication delayed; secondary still has the older value")
            return
        self._propagate(stock)

    def pause_replication(self) -> None:
        self.replication_paused = True
        print("  replication paused")

    def resume_replication(self) -> None:
        self.replication_paused = False
        print("  replication resumed")
        if self._pending is None:
            return
        stock = self._pending
        self._pending = None
        self._propagate(stock)

    def read(self, which: str) -> int:
        replica = self.primary if which == "primary" else self.secondary
        return self.client.read(replica)

    def _propagate(self, stock: int) -> None:
        print(f"  propagating stock = {stock} to secondary")
        self.secondary.apply(stock)
        print(f"  secondary stock = {self.secondary.stock}")


def _header(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def demonstrate_replication() -> None:
    _header("1. Replication")
    system = InventorySystem(stock=10)
    print("  initial primary stock = 10")
    print("  initial secondary stock = 10")
    system.update(15)
    primary = system.read("primary")
    secondary = system.read("secondary")
    print(f"  replicas match: {primary == secondary == 15}")


def demonstrate_stale_read_and_recovery() -> None:
    _header("2. Stale read")
    system = InventorySystem(stock=10)
    system.pause_replication()
    system.update(9)
    primary = system.read("primary")
    secondary = system.read("secondary")
    print(f"  primary returns {primary}")
    print(f"  secondary returns {secondary} (stale)")
    print(f"  stale read observed: {primary == 9 and secondary == 10}")

    _header("3. Recovery and convergence")
    system.resume_replication()
    primary = system.read("primary")
    secondary = system.read("secondary")
    print(f"  primary returns {primary}")
    print(f"  secondary returns {secondary}")
    print(f"  replicas match: {primary == secondary == 9}")


def main() -> None:
    demonstrate_replication()
    demonstrate_stale_read_and_recovery()
    print()


if __name__ == "__main__":
    main()
