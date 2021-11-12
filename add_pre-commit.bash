#!/bin/bash

cat <<'EOF' > .git/hooks/pre-commit
#!/bin/bash

black -l 79 .
if python3 lint.py -p ../miner_preview/ ; then
  echo "flash8:"
  flake8 --ignore E203,W503 .
fi
EOF

chmod +x .git/hooks/pre-commit
