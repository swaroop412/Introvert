import os
import json

print("=" * 80)
print("ORATORIQ - SETTING UP REACT + VITE + TYPESCRIPT CLIENT")
print("=" * 80)

# Create client directory structure
client_dir = "oratoriq/client"
os.makedirs(client_dir, exist_ok=True)

# Create subdirectories
subdirs = [
    "src",
    "src/components",
    "src/components/layout",
    "src/store",
    "src/types",
    "src/styles",
    "src/pages",
    "public"
]

for subdir in subdirs:
    path = os.path.join(client_dir, subdir)
    os.makedirs(path, exist_ok=True)
    print(f"✓ Created {path}")

# ============================================================================
# package.json
# ============================================================================
package_json = {
    "name": "oratoriq-client",
    "version": "1.0.0",
    "type": "module",
    "scripts": {
        "dev": "vite",
        "build": "tsc && vite build",
        "preview": "vite preview",
        "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
    },
    "dependencies": {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
        "react-router-dom": "^6.21.1",
        "zustand": "^4.4.7"
    },
    "devDependencies": {
        "@types/react": "^18.2.43",
        "@types/react-dom": "^18.2.17",
        "@vitejs/plugin-react": "^4.2.1",
        "autoprefixer": "^10.4.16",
        "postcss": "^8.4.32",
        "tailwindcss": "^3.4.0",
        "typescript": "^5.3.3",
        "vite": "^5.0.8"
    }
}

with open(os.path.join(client_dir, "package.json"), 'w') as f:
    json.dump(package_json, f, indent=2)
print("\n✓ Created package.json")

# ============================================================================
# vite.config.ts
# ============================================================================
vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
"""

with open(os.path.join(client_dir, "vite.config.ts"), 'w') as f:
    f.write(vite_config)
print("✓ Created vite.config.ts")

# ============================================================================
# tsconfig.json
# ============================================================================
tsconfig = {
    "compilerOptions": {
        "target": "ES2020",
        "useDefineForClassFields": True,
        "lib": ["ES2020", "DOM", "DOM.Iterable"],
        "module": "ESNext",
        "skipLibCheck": True,
        "moduleResolution": "bundler",
        "allowImportingTsExtensions": True,
        "resolveJsonModule": True,
        "isolatedModules": True,
        "noEmit": True,
        "jsx": "react-jsx",
        "strict": True,
        "noUnusedLocals": True,
        "noUnusedParameters": True,
        "noFallthroughCasesInSwitch": True
    },
    "include": ["src"],
    "references": [{"path": "./tsconfig.node.json"}]
}

with open(os.path.join(client_dir, "tsconfig.json"), 'w') as f:
    json.dump(tsconfig, f, indent=2)
print("✓ Created tsconfig.json")

# ============================================================================
# tsconfig.node.json
# ============================================================================
tsconfig_node = {
    "compilerOptions": {
        "composite": True,
        "skipLibCheck": True,
        "module": "ESNext",
        "moduleResolution": "bundler",
        "allowSyntheticDefaultImports": True
    },
    "include": ["vite.config.ts"]
}

with open(os.path.join(client_dir, "tsconfig.node.json"), 'w') as f:
    json.dump(tsconfig_node, f, indent=2)
print("✓ Created tsconfig.node.json")

# ============================================================================
# tailwind.config.js
# ============================================================================
tailwind_config = """/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
        },
      },
    },
  },
  plugins: [],
}
"""

with open(os.path.join(client_dir, "tailwind.config.js"), 'w') as f:
    f.write(tailwind_config)
print("✓ Created tailwind.config.js")

# ============================================================================
# postcss.config.js
# ============================================================================
postcss_config = """export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
"""

with open(os.path.join(client_dir, "postcss.config.js"), 'w') as f:
    f.write(postcss_config)
print("✓ Created postcss.config.js")

# ============================================================================
# index.html
# ============================================================================
index_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OratorIQ - Speech Analysis Platform</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
"""

with open(os.path.join(client_dir, "index.html"), 'w') as f:
    f.write(index_html)
print("✓ Created index.html")

# ============================================================================
# src/styles/index.css
# ============================================================================
index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
  color-scheme: light dark;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  width: 100%;
  min-height: 100vh;
}
"""

with open(os.path.join(client_dir, "src/styles/index.css"), 'w') as f:
    f.write(index_css)
print("✓ Created src/styles/index.css")

print("\n" + "=" * 80)
print("CLIENT SETUP COMPLETE")
print("=" * 80)
print("\n📦 Next steps:")
print("  1. cd oratoriq/client")
print("  2. npm install")
print("  3. npm run dev")

client_structure_ready = True
