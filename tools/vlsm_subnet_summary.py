"""Generate a simple VLSM subnet summary for the SkyNetix KL branch.

The values here are an editable example for documenting subnet allocation
logic alongside the Packet Tracer files and addressing screenshots.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import IPv4Network


@dataclass(frozen=True)
class NetworkRequirement:
    name: str
    hosts_required: int


REQUIREMENTS = [
    NetworkRequirement("Admin office", 50),
    NetworkRequirement("Staff workspace", 40),
    NetworkRequirement("Guest Wi-Fi", 30),
    NetworkRequirement("Server room", 12),
    NetworkRequirement("WAN link", 2),
]


def prefix_for_hosts(hosts_required: int) -> int:
    host_bits = 0

    while (2 ** host_bits) - 2 < hosts_required:
        host_bits += 1

    return 32 - host_bits


def allocate_subnets(base_network: str, requirements: list[NetworkRequirement]) -> list[tuple[str, IPv4Network]]:
    network = IPv4Network(base_network)
    sorted_requirements = sorted(requirements, key=lambda item: item.hosts_required, reverse=True)
    available = [network]
    allocations: list[tuple[str, IPv4Network]] = []

    for requirement in sorted_requirements:
      prefix = prefix_for_hosts(requirement.hosts_required)

      for index, candidate in enumerate(available):
          if candidate.prefixlen <= prefix:
              split = list(candidate.subnets(new_prefix=prefix))
              allocations.append((requirement.name, split[0]))
              available.pop(index)
              available.extend(split[1:])
              available.sort(key=lambda item: int(item.network_address))
              break
      else:
          raise ValueError(f"No subnet available for {requirement.name}")

    return allocations


def main() -> None:
    for name, subnet in allocate_subnets("192.168.10.0/24", REQUIREMENTS):
        usable_hosts = max(subnet.num_addresses - 2, 0)
        print(f"{name:18} {subnet} usable_hosts={usable_hosts}")


if __name__ == "__main__":
    main()
