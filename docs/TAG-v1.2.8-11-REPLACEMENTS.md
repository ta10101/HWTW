# Replacements for `v1.2.8`–`v1.2.11`

Those four tag names were removed during a history rewrite (author email scrub on commit metadata). This repository had **immutable releases** enabled for earlier releases using those tags. Per [GitHub’s immutable releases policy](https://docs.github.com/en/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases), **those exact tag names cannot be created again** on this repo—even after the refs were deleted.

**Use these tags instead** (same trees as the rewritten `v1.2.8`–`v1.2.11` pointers):

| Original (reserved) | Replacement     |
| ------------------- | --------------- |
| `v1.2.8`            | `v1.2.8-privacy`  |
| `v1.2.9`            | `v1.2.9-privacy`  |
| `v1.2.10`           | `v1.2.10-privacy` |
| `v1.2.11`           | `v1.2.11-privacy` |

Default branch history uses `ta10101@users.noreply.github.com` for new commits; pin dependencies to the replacement tags above if you relied on the old names.
