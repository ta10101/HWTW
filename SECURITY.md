# Security policy

## Supported versions

| Track | Supported |
| ----- | --------- |
| Latest commit on `main` | Yes |
| Recent version tags (`v*`) | Yes |
| Older tags | Best effort only |

## Reporting a vulnerability

Do **not** open a public issue for exploit details.

1. Prefer **[private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)** on GitHub: repository **Security** tab → **Report a vulnerability** (enable it under **Settings → Code security** if it is off).
2. If that is unavailable, contact the repository owner through a **private** channel (e.g. GitHub profile contact options).

We will try to acknowledge reports within a few business days.

## Supply chain — releases

`HWTW.exe` and `requirements.txt` attached to GitHub **Releases** are produced by the **Release** workflow on this repository. Compare the release tag to the workflow run and commit SHA when verifying binaries.

## Maintainer checklist (GitHub settings)

Apply these on **github.com/ta10101/HWTW** (or your fork) to reduce tampering and accidents:

1. **Settings → General**
   - Turn off unused features (**Wiki**, **Discussions**, **Projects**) if you do not use them.
   - Under **Features**, consider **Restrict editing to collaborators only** if you want stricter control (optional).

2. **Settings → Rules → Rulesets** (or **Branches → Branch protection**) for `main`
   - Require **status checks** to pass before merge (select the **CI** workflow).
   - **Block force pushes** to `main`.
   - Optionally **require a pull request** before merging and **require approvals** (even solo maintainers can self-approve, but it blocks silent direct pushes).
   - Enable **Do not allow bypassing the above settings** if your role allows it.

3. **Settings → Actions → General**
   - **Fork pull request workflows**: prefer **Require approval for all outside collaborators** (or stricter) so unknown forks cannot run Actions against your repo without review.
   - Do **not** attach **self-hosted runners** to this **public** repository.

4. **Settings → Code security and analysis**
   - Enable **Dependabot alerts** and **Dependabot security updates**.
   - Enable **Secret scanning** (and push protection if available on your plan).

5. **Secrets**
   - This project’s workflows do **not** require repository secrets for build/release. Do not add tokens unless you have a clear need; never commit secrets into the tree.

6. **Collaborators**
   - Only add people who need write access; use **Read** or **Triage** for contributors who do not need to push to `main`.

## Personal / machine data

Do not commit:

- `hwtw_config.json`, `.wind_tunnel_gui_setup_done` (already in `.gitignore` — hostnames and local prefs).
- `.env`, API keys, Nomad tokens, or SSH private keys (see `.gitignore`).

If something sensitive was ever pushed, **rotate the secret** and consider `git filter-repo` or GitHub support — revoking the secret matters more than history scrubbing alone.
