# Setup Instructions for AI Career Discovery Application

## Prerequisites

Before you can run this application, you need to have Node.js and npm installed on your system.

### Step 1: Install Node.js

#### Windows (Using Chocolatey - Recommended)

If you have Chocolatey installed:
```powershell
choco install nodejs
```

#### Windows (Direct Download)

1. Go to [https://nodejs.org/](https://nodejs.org/)
2. Download the LTS (Long Term Support) version
3. Run the installer and follow the installation wizard
4. Verify installation by opening PowerShell and running:
   ```powershell
   node --version
   npm --version
   ```

#### macOS

Using Homebrew:
```bash
brew install node
```

Or visit https://nodejs.org/

#### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nodejs npm

# Or using nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install node
```

## Step 2: Install Dependencies

After Node.js is installed, navigate to the project directory and install dependencies:

```powershell
cd "c:\Users\rahul.mishra\Desktop\hackthon"
npm install
```

## Step 3: Run the Application

Start the development server:

```powershell
npm run dev
```

The application will open automatically at `http://localhost:5173`

## Step 4: Build for Production (Optional)

To create a production build:

```powershell
npm run build
```

To preview the production build locally:

```powershell
npm run preview
```

## Troubleshooting

### PowerShell Execution Policy Error
If you get an execution policy error, try running PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port Already in Use
If port 5173 is already in use, Vite will automatically use the next available port.

### Module Not Found Errors
If you get "module not found" errors after installation, try:
```powershell
npm install --legacy-peer-deps
```

### Clear npm Cache
If installation fails, clear the npm cache:
```powershell
npm cache clean --force
npm install
```

## System Requirements

- Node.js 16 or higher
- npm 7 or higher
- 500MB free disk space
- Modern web browser (Chrome, Firefox, Safari, or Edge)

## Recommended Setup

1. Install Node.js LTS from https://nodejs.org/
2. Use VS Code as your editor (already installed)
3. Install VS Code extensions:
   - ES7+ React/Redux/React-Native snippets
   - Tailwind CSS IntelliSense
   - TypeScript Vue Plugin

## Once Everything is Set Up

After Node.js is installed and you've run `npm install`, you can:

1. **Start developing**: `npm run dev`
2. **Build**: `npm run build`
3. **Preview**: `npm run preview`
4. **Lint**: `npm run lint`

The development server will provide hot module replacement (HMR), so changes you make will be reflected immediately in the browser.

---

**Next Steps:**
1. Install Node.js from https://nodejs.org/ (LTS version recommended)
2. Come back and run `npm install` in this directory
3. Then run `npm run dev` to start the application

If you need further assistance, please refer to the official Node.js documentation at https://nodejs.org/docs/
