#!/bin/bash

cat <<'EOF' > .git/hooks/pre-commit
#!/bin/bash

black .
python3 lint.py -p ../miner_preview/
EOF

chmod +x .git/hooks/pre-commit
