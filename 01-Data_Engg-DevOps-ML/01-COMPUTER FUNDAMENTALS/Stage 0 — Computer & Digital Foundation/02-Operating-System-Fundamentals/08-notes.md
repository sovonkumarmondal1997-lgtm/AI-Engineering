# Concept 08 — Permissions

**Permissions** are rules enforced by the operating system that decide who can read, modify, or execute a file or directory. They protect data from unauthorized access, accidental changes, and compromised programs.

---

## 1. Why permissions exist

Permissions help the operating system:

- Prevent unauthorized access to files.
- Protect private information, credentials, and configuration.
- Prevent accidental modification or deletion.
- Separate different users and services.
- Limit damage caused by buggy or compromised applications.

---

## 2. Users, groups, and ownership

Linux uses three permission categories:

| Category | Meaning |
|---|---|
| Owner | User who owns the file |
| Group | Users belonging to the file's owning group |
| Others | Everyone else |

- **UID:** Numeric identity of a user.
- **GID:** Numeric identity of a group.
- **Username:** Human-readable name associated with a UID.
- **Owning group:** Group associated with a file.

**Commands:** `id` shows UID, GID, and groups; `whoami` shows your username; `groups` lists your groups.

---

## 3. Three permission types

| Permission | Regular file | Directory |
|---|---|---|
| `r` — Read | Read file content | List filenames inside |
| `w` — Write | Modify file content | Create, rename, or delete entries |
| `x` — Execute | Run a program | Enter/traverse the directory |

**Important:** Directory `r` and `x` are different. With `x` but without `r`, you can access a known filename but cannot list the directory. With `r` but without `x`, you can list filenames but cannot access their contents.

---

## 4. Numeric and symbolic permissions

### Numeric values

- `r` = 4
- `w` = 2
- `x` = 1

Add them to calculate each category's permission.

| Permission | Meaning |
|---|---|
| `644` | Owner reads/writes; group and others read |
| `755` | Owner has full access; group and others read/execute |
| `700` | Only owner has access |
| `600` | Only owner can read/write |

### Symbolic notation

- `u` = owner
- `g` = group
- `o` = others
- `a` = all

Examples:

```bash
chmod u+x file
chmod g-w file
chmod o-r file
chmod 644 file
chmod 755 file
```

`+` adds, `-` removes, and `=` sets permissions exactly.

---

## 5. How permission checking works

1. Python requests file access through a system call.
2. Kernel identifies the process's UID/GID.
3. Kernel checks file ownership and permission metadata.
4. It determines whether owner, group, or others rules apply.
5. It allows or denies the operation.
6. Python receives the data or a permission-related error.

The file's owner is also subject to permission bits.

---

## 6. Practical Linux commands

| Command | Purpose |
|---|---|
| `ls -l` | View permissions, owner, and group |
| `ls -ld directory` | Inspect directory permissions |
| `stat file` | Detailed ownership and permission information |
| `id` | Show user and group IDs |
| `whoami` | Show current username |
| `groups` | Show group memberships |
| `chmod` | Change permissions |

The lesson demonstrates these commands using an isolated temporary directory in WSL2's native Linux filesystem. Windows-mounted paths such as `/mnt/c` may behave differently.

---

## 7. Debugging and production relevance

Common problems include `PermissionError`, inability to write a readable file, inaccessible files inside directories, and services failing under different user accounts.

Never use `chmod 777` as a default fix. It gives everyone full access and removes protection. Instead, identify the actual process identity, inspect ownership and permissions, check every parent directory's `x` permission, and grant only the minimum access required.

For AI engineering:

- Model directories should generally be read-only for inference services.
- Log and temporary directories need scoped write access.
- Secrets/configuration files need restricted access, often `600`.
- Dedicated service accounts help isolate application permissions.

---

## 8. Complete lesson coverage

The file also includes 12 common misconceptions, 6 debugging scenarios, 37 exercises, expected results, and review questions.

The central production principle is **least privilege**: give every process exactly the permissions it needs, and nothing more.
