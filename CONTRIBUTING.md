# Contributing to TeamOrre – Pokémon XD Decompilation

Welcome to the TeamOrre Pokémon XD decomp effort. This document explains how to contribute safely and effectively, and is subject to change as the decomp progresses and we establish our workflow.

## Team Roles

These correspond to GitHub Teams inside the organization:

### xd-decomp-core
Core XD developers.
Can push feature branches, review and merge PRs, contribute to the Ghidra project, and maintain repo stability.

### colo-decomp-core
Colosseum-focused developers who may open PRs here.

### research-contributors
Work in the `orre-research` repo (symbol maps, Ghidra notes, documentation).
Read-only access here.

### tool-contributors
Primarily develop utilities.
Open PRs here but do not push directly.

## General Contribution Rules

### 1. No direct commits to `main`
All work must be done through pull requests.

### 2. One purpose per PR
Small, focused PRs are easier to review and maintain.

Examples of good PRs:
- “Add 12 new retail XD symbols”
- “Document Pokemon evolution functions in docs/”
- “Initial split regions for .text segment”
- “Add tool to dump REL files from assets”

### 3. Naming Conventions
- Use names from symbol maps when available.
- Otherwise, use clear, descriptive technical names.
- Avoid lore names unless confirmed by evidence.

## Working on Symbols

Symbols are located in `config/GAMEID/symbols.txt`. The format and attributes are documented [here](https://github.com/encounter/dtk-template/blob/main/docs/symbols.md)

Guidelines:
- For symbols shared between versions, use the demo map symbol names (in `NXXJ01/symbols.txt`)
- Avoid adding speculative names without evidence

## Working on Splits

Splits go into `config/GAMEID/splits.txt`, defining DOL/REL segment boundaries. The format and attributes are documented [here](https://github.com/encounter/dtk-template/blob/main/docs/splits.md)

Guidelines:
- Keep placeholder splits until confirmed
- If making changes to splits, verify that they work first by building before submitting changes

## Tools

Scripts should go into `tools/` or the `orre-tools` repository depending on size.

Tool guidelines:
- Prefer small, single-purpose tools
- Document how to use them
- Avoid tools requiring proprietary software
- Leave clear instructions for setup if needed

## Getting Started

If you want to begin contributing:

1. Check the Projects tab for files to work on (coming soon), or help others stuck on an issue in the discussion channel.
2. Request access to the shared Ghidra project (instructions below).
3. Ask before adding new C source files or changing the project structure.
4. For symbols/splits work, open a PR with your proposed changes.

Thank you for contributing to TeamOrre and helping preserve and understand these games.

## Setting up Ghidra

We have a shared Ghidra project for Pokemon XD, with read/write access granted to xd-decomp-core contributors, and read access granted to everyone else.

The steps to access this project are as follows:

1. Go to https://ghidra.decomp.dev and link your Discord account.
2. Create a Ghidra account by entering a new username and password into the form on the right.
3. Request access to the Pokemon XD server. Request write access if part of the xd-decomp-core team, request read access otherwise.

Once an admin has approved your request, you can set up the Ghidra project through the following steps:

1. Download and install [OpenJDK 21](https://adoptium.net/temurin/releases).
2. Download the Rootcubed Ghidra 11.2 DEV build from [here](https://github.com/RootCubed/ghidra-ci/releases/tag/2024-08-14).
3. Launch Ghidra with `ghidraRun`, or run `ghidraRun.bat` if on Windows.
4. Go to `File -> New Project...`. Select `Shared Project` and input the following information:
    * Server Name: ghidra.decomp.dev
    * Port Number: 13100
    * User ID: (the username that you chose earlier)
    * Password: (the password that you chose earlier)

The files in the project should now be viewable.

## AI Assistance Policy

Due to the early nature of this project, **AI assisted contributions are banned until further notice.** This policy will be revisited once coding standards are finalized and further decomp progress is made. Any attempt to circumvent this ban by passing off AI work as human work will result in an immediate ban.
