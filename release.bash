#!/bin/bash
set -e

# Simple tag-based release script
# This triggers GitHub Actions to handle the actual PyPI upload

VERSION_TYPE=${1:-patch}
echo "🚀 Preparing release with $VERSION_TYPE version bump..."

# Check if we're on main/master branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]; then
    echo "❌ Error: Must be on main/master branch. Current: $BRANCH"
    exit 1
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Error: Working directory not clean. Commit changes first."
    exit 1
fi

# Install bump2version if needed
if ! command -v bump2version &> /dev/null; then
    echo "📦 Installing bump2version..."
    pip install bump2version
fi

# Get current version from setup.py
CURRENT_VERSION=$(grep "version=" setup.py | cut -d'"' -f2)
echo "📍 Current version: $CURRENT_VERSION"

# Bump version
echo "📈 Bumping $VERSION_TYPE version..."
bump2version $VERSION_TYPE --current-version $CURRENT_VERSION setup.py

# Get new version
NEW_VERSION=$(grep "version=" setup.py | cut -d'"' -f2)
echo "🎯 New version: $NEW_VERSION"

# Commit version bump
git add setup.py .bumpversion.cfg
git commit -m "Bump version to $NEW_VERSION"

# Run tests locally before tagging
echo "🧪 Running tests..."
python -m pytest tests/ || {
    echo "❌ Tests failed! Rolling back..."
    git reset --hard HEAD~1
    exit 1
}

# Create and push tag (this triggers GitHub Actions)
echo "🏷️  Creating and pushing tag v$NEW_VERSION..."
git tag "v$NEW_VERSION"
git push origin $BRANCH
git push origin "v$NEW_VERSION"

echo "✅ Release initiated!"
echo "🔗 GitHub Actions will handle PyPI publishing"
echo "📊 Monitor progress: https://github.com/yushdotkapoor/service_config_foundry/actions"
echo "📦 Package will be available at: https://pypi.org/project/service-config-foundry/$NEW_VERSION/"
