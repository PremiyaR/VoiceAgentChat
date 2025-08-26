# Setting Up Multiple GitHub Accounts

This guide will help you manage both your personal and work GitHub accounts on the same machine.

## Current Situation
- **Work Account**: `rajani@genius-germany.de` (PremiyaRajani)
- **Personal Account**: `rajanipremiya@gmail.com` (PremiyaRajani)

## Method 1: Quick Account Switching (Recommended for beginners)

### Use the provided batch script:
1. Double-click `git-switch-accounts.bat`
2. Choose account 1 (Personal) or 2 (Work)
3. The script will configure Git for the selected account

### Manual switching:
```bash
# Switch to Personal Account
git config user.name "PremiyaRajani"
git config user.email "rajanipremiya@gmail.com"

# Switch to Work Account
git config user.name "PremiyaRajani"
git config user.email "rajani@genius-germany.de"
```

## Method 2: SSH Keys with Different Hosts (Advanced)

### Step 1: Generate SSH keys
```bash
# Personal account key
ssh-keygen -t ed25519 -C "rajanipremiya@gmail.com" -f ~/.ssh/id_ed25519_personal

# Work account key (if you don't have one)
ssh-keygen -t ed25519 -C "rajani@genius-germany.de" -f ~/.ssh/id_ed25519_work
```

### Step 2: Add keys to SSH agent
```bash
ssh-add ~/.ssh/id_ed25519_personal
ssh-add ~/.ssh/id_ed25519_work
```

### Step 3: Create SSH config file (~/.ssh/config)
```
# Personal GitHub account
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_personal

# Work GitHub account
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_work
```

### Step 4: Clone repositories with different hosts
```bash
# Personal repository
git clone git@github-personal:PremiyaRajani/repository-name.git

# Work repository
git clone git@github-work:PremiyaRajani/repository-name.git
```

## Method 3: Git Credential Manager (Windows)

### Install Git Credential Manager:
```bash
winget install Microsoft.GitCredentialManagerCore
```

### Configure multiple accounts:
1. Run: `git config --global credential.helper manager-core`
2. When pushing, Git will prompt for credentials
3. Enter the appropriate username/password for each account

## Best Practices

1. **Always check current account before committing:**
   ```bash
   git config user.name
   git config user.email
   ```

2. **Use the batch script for quick switching**

3. **Set up SSH keys for secure authentication**

4. **Use different local directories for personal vs work projects**

## Troubleshooting

### Permission denied errors:
- Check if you're using the correct account
- Verify SSH keys are added to the correct GitHub account
- Ensure repository permissions match your account

### Wrong account commits:
- Use `git log --oneline` to check recent commits
- If needed, amend the last commit: `git commit --amend --author="Name <email>"`

## Quick Commands Reference

```bash
# Check current account
git config user.name && git config user.email

# Switch to personal
git config user.email "rajanipremiya@gmail.com"

# Switch to work
git config user.email "rajani@genius-germany.de"

# Run account switcher
./git-switch-accounts.bat
```
