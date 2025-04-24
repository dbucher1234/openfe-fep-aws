#!/bin/bash

# Add everything
git add .

# Commit with generic or default message
git commit -m "Quick sync" 2>/dev/null

# Pull remote changes first (with rebase to avoid merge commits)
git pull origin main --rebase

# Now push
git push origin main

