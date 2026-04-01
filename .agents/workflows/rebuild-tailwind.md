---
description: Rebuild Tailwind CSS from templates
---

Run this workflow whenever you add or modify Tailwind CSS classes in any HTML template.

// turbo-all

1. Rebuild the Tailwind CSS file:
```bash
cd /Users/xhlm/Desktop/陪玩店 && npx -y tailwindcss@3.4.17 -i /dev/stdin -o app/static/css/tailwind.css --minify <<'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;
EOF
```

2. Verify the output file:
```bash
ls -lh /Users/xhlm/Desktop/陪玩店/app/static/css/tailwind.css
```
