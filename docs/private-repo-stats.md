# Private repository stats

The generator can count private repository activity without listing private
repositories in `config.yml` or exposing their names in the generated SVGs.

How it works:

- Without a token, GitHub only returns public data.
- With `GITHUB_TOKEN` or a PAT, stats use GitHub GraphQL.
- With a PAT that can read your private repositories, language totals and repo
  counts include every owned repository visible to that token.
- `projects` in `config.yml` should only contain repositories you want to show
  publicly as featured projects.

For GitHub Actions, create a repository secret named `GH_PROFILE_TOKEN` and map
it to `GITHUB_TOKEN` in the workflow step that runs the generator:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GH_PROFILE_TOKEN }}
```

Recommended token setup:

- Fine-grained personal access token.
- Set the resource owner to the account that owns the private repositories.
- Select the repositories you want counted, or all repositories.
- Grant read-only access to Contents, Issues, Pull requests, and Profile.
- Keep the shortest practical expiration date and rotate the secret before it
  expires.

If some repositories belong to an organization, the organization may need to
approve the token. A fine-grained PAT is limited to one resource owner, so
repositories spread across multiple owners require separate automation or a
GitHub App.

Do not commit the token to the repository. Use an environment variable locally:

```powershell
$env:GITHUB_TOKEN = "github_pat_..."
python -m generator.main
```
