#!/bin/bash
set -e

# Modern deployment script for service_config_foundry
# Usage: ./deploy_modern.bash [patch|minor|major]

VERSION_TYPE=${1:-patch}

echo "🚀 Starting deployment process..."
echo "📦 Version bump type: $VERSION_TYPE"

# Check if we're on main/master branch
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$BRANCH" != "main" && "$BRANCH" != "master" ]]; then
    echo "❌ Error: Must be on main/master branch to deploy. Current branch: $BRANCH"
    exit 1
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Error: Working directory is not clean. Please commit or stash changes."
    git status --short
    exit 1
fi

# Install/upgrade required tools
echo "🔧 Installing deployment tools..."
pip install --upgrade build twine bump2version

# Get current version
CURRENT_VERSION=$(python -c "import setuptools_scm; print(setuptools_scm.get_version())" 2>/dev/null || echo "0.5.2")
echo "📍 Current version: $CURRENT_VERSION"

# Bump version in setup.py (if using setup.py)
if [[ -f "setup.py" ]]; then
    echo "📈 Bumping version in setup.py..."
    bump2version $VERSION_TYPE --current-version $CURRENT_VERSION setup.py
fi

# Get new version
NEW_VERSION=$(grep "version=" setup.py | cut -d'"' -f2)
echo "🎯 New version: $NEW_VERSION"

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ || {
    echo "❌ Tests failed! Aborting deployment."
    exit 1
}

# Build package
echo "📦 Building package..."
rm -rf dist/ build/ *.egg-info/
python -m build

# Check package
echo "🔍 Checking package..."
twine check dist/*

# Ask for confirmation
echo "🤔 Ready to deploy version $NEW_VERSION to PyPI?"
echo "📋 Files to upload:"
ls -la dist/
echo ""
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

# Upload to PyPI
echo "🚀 Uploading to PyPI..."
twine upload dist/*

# Create and push git tag
echo "🏷️  Creating git tag..."
git tag "v$NEW_VERSION"
git push origin "v$NEW_VERSION"
git push origin $BRANCH

echo "✅ Deployment complete!"
echo "📦 Version $NEW_VERSION is now live on PyPI"
echo "🏷️  Git tag v$NEW_VERSION created and pushed"
echo "🔗 View on PyPI: https://pypi.org/project/service-config-foundry/$NEW_VERSION/"
