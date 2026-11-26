# GitHub workflow for the shared repository

Repository: https://github.com/xahiru/PT22026
Your folder: `<first 3 letters of first name><last 3 digits of student ID>` (it should already exist; ask a TA if not).
Never edit another student's folder. Never push to `main`.

## One-time setup

```bash
git config --global user.name  "Your Name"
git config --global user.email "your-github-email@example.com"
```

## 1. Get the repository

If you have write access:
```bash
git clone https://github.com/xahiru/PT22026.git
cd PT22026
```
If GitHub says you have no write access, click **Fork** on the repo page, then clone **your fork** instead and open the PR from the fork later.

## 2. Work on a branch (not main)

```bash
git checkout -b feature/waste-classifier
```

## 3. Add the project

Copy the contents of the project (app.py, src/, data/, ...) into **your folder** inside `PT22026`. Then:

```bash
git status                 # check that only your folder changed
```

## 4. Commit in small, meaningful steps

Make several commits as you go, not one at the end. Suggested sequence:

```bash
git add <folder>/.gitignore <folder>/requirements.txt <folder>/README.md
git commit -m "Add project skeleton, requirements and README"

git add <folder>/src/config.py <folder>/src/validation.py <folder>/src/classifier.py
git commit -m "Add image validation and ViT classifier wrapper"

git add <folder>/data <folder>/src/recommender.py <folder>/tests
git commit -m "Add recycling knowledge base, recommender and unit tests"

git add <folder>/app.py
git commit -m "Add Gradio interface"

git add <folder>/evaluation
git commit -m "Add evaluation script and instructions"
```

## 5. Push the branch

```bash
git push -u origin feature/waste-classifier
```

## 6. Open the Pull Request

On GitHub, open the repository. Click **Compare & pull request**. Base branch is `main`, compare branch is your branch. Write a short description (what the project is, how to run it) and click **Create pull request**. The PR is the official submission, so confirm it appears under the repository's **Pull requests** tab.

## If something goes wrong

- `git status` shows what is changed. `git log --oneline` shows your commits.
- `Permission denied` on push: use the fork route above.
- Never commit `.venv/`, model weights, or test images (the `.gitignore` already blocks them).
