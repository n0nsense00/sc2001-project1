# Working together on GitHub

Repository: https://github.com/n0nsense00/sc2001-project1

This repository is private. Only authorized GitHub users can browse or clone it.
The project owner authorized its creation and upload on 2026-09-14. Uploading the
project does not invite teammates or grant Google Slides access.

## Owner: give teammates access

1. Ask teammates for their GitHub usernames.
2. Open the repository's Settings > Collaborators > Add people.
3. Select the intended teammate and send an invitation.
4. The teammate accepts the invitation while signed in to that GitHub account.

These invitations have not been sent automatically. A private-repository link
alone does not grant access; an unauthorized viewer may see a 404 page.

GitHub's instructions:
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository

## Teammates: read or run the project

For reading, open README.md, algorithms.py, analysis.ipynb, docs/ and plots/ on
GitHub. Download analysis.html and open it locally for the portable report.

For running and editing, install Git and Python, then run:

```bash
git clone https://github.com/n0nsense00/sc2001-project1.git
cd sc2001-project1
```

Follow the README's Windows or macOS/Linux virtual-environment setup. Each
teammate creates their own `.venv`; it is intentionally absent from GitHub.
Run the small demo and tests first. Full benchmark results are already included.
Do not rerun the expensive full experiment merely to read or demonstrate it.

## Make and review a change

Start with a clean working tree. Pull the latest main branch, then create a
branch for one change; choose a descriptive branch name:

```bash
git switch main
git pull --ff-only
git switch -c codex/explain-merge
```

Edit files in your editor. For algorithm changes, run the correctness tests
using your virtual environment's Python:

```bash
python -m unittest discover -s tests -v
python demo.py
git diff
```

Save and upload only the intended files. This example changes a document:

```bash
git add docs/walkthrough-and-qa.md
git commit -m "Clarify the merge comparison example"
git push -u origin codex/explain-merge
```

Open a pull request on GitHub from the new branch into main. A teammate reviews
the differences and relevant checks before merging. Others then update their
clean main branches with `git pull --ff-only`. Do not force-push shared branches.
If pull reports conflicting or uncommitted changes, stop and inspect `git status`
instead of deleting work. Branch review is the suggested workflow; branch
protection has not been configured or claimed.

Small documentation edits can also be made through GitHub's file editor. Use a
new branch and pull request so the rest of the group can see what changed.

## Files to keep and files to exclude

Keep code, tests, configurations, compact saved results, plots, notebook, slides,
and documentation in version control. Keep `.venv`, `.build`, caches and large
regenerable input arrays out of Git; `.gitignore` covers them.

Treat `results/full` as evidence for the original recorded implementation.
Changing algorithms.py or experiment.py invalidates the old run's source-hash
match. Keep the original data and run a new experiment into a new results folder;
never edit the old metadata to pretend the changed code produced those results.
Do not manually edit notebook outputs to alter reported findings.

Google Slides is separate from GitHub: the owner must grant presentation access
in Google Slides when ready. The PDF and PowerPoint copies are available here.

## Original computer layout

The original clone is at
`C:\Users\daboi\Documents\ChatGPT\SC2001\project1` and has its own `.git`
directory and GitHub remote. The parent SC2001 course-notes repository is separate.
Run Git commands inside `project1` when editing this project. Teammates' clones
are standalone and do not require the parent course-notes folder.
