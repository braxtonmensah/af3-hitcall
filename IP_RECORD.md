# Contemporaneous record: compute provenance for the virtual screen

Written 2026-09-25, before the screen was run, so it is a record and not a reconstruction.

## What was used

The Boltz-2 virtual screen of the RNase J (MPN280 / P75497) : MPN621 interface was run on **IU
Quartz**, the university's general-access research computing cluster.

- Quartz is open to **all IU students, including undergraduates**, at no cost.
- Access is **self-service**: an account is created at `access.iu.edu/Accounts/Create` with no
  proposal, no faculty sponsor, and no granted allocation.
- **No faculty sponsor, no IU funding, no sponsored project, no IU lab space, and no employment
  relationship** were involved.
- Big Red 200 was deliberately **not** used, because it requires a faculty or staff sponsor and an
  allocation granted through `projects.rt.iu.edu`.

## The policy basis relied on

IU policy **UA-24 (Intellectual Property: Inventions and Patents)**, as published at
`policies.iu.edu/policies/ua-24-intellectual-property-inventions-and-patents/` and read on
2026-09-25, defines "University Resources" so as to **exclude**:

> "incidental or insignificant use of office space and communication technologies, and resources
> routinely made available for general educational, research, and administrative purposes."

Quartz is resources routinely made available for general educational and research purposes: free,
open to every student by default, self-service, and requiring no grant of any kind. The exclusion is
relied on for that reason.

## Software licensing, kept separate from the above

- **Boltz-2 is MIT-licensed** and permits commercial use. The screen uses Boltz-2, not AlphaFold.
- **No AlphaFold Server output was used in the screen.** AF Server output is non-commercial only and
  its terms explicitly bar use in connection with any automated system predicting protein-ligand
  binding. That prohibition is the reason the clean room exists.
- Inputs: UniProt sequences (CC BY 4.0), ChEMBL approved-drug structures (CC BY-SA 3.0), and an MSA
  built from public sequence databases.

## Open item

IU's Innovation and Commercialization Office answers ownership questions at no cost. The exclusion
above is read as covering Quartz, but the language has no bright-line test, so a written confirmation
from the ICO would settle it. Nothing here is patentable as it stands (a natural complex and its
coordinates are not patentable subject matter, Myriad 2013); the question would only become live if
the screen produced a method-of-use candidate.
