# NETVEXA Homepage Setup

The public-facing website has been renamed from `marketing-site` to `homepage` for clarity and consistency.

## 🚀 Quick Start

```bash
# From root directory
./start-homepage.sh

# The homepage will run on http://localhost:3001
```

## 📁 Directory Structure

```
homepage/
├── components/         # React components (Hero, Features, Pricing, etc.)
├── pages/             # Next.js pages
│   ├── index.tsx      # Main homepage
│   ├── blog/          # Blog section
│   └── integrations/  # Integration pages
├── content/           # Blog markdown files
├── styles/            # CSS styles
├── public/            # Static assets
└── README.md          # Homepage documentation
```

## 🌐 Available Pages

- **Homepage**: http://localhost:3001
- **Blog**: http://localhost:3001/blog
- **WordPress Integration**: http://localhost:3001/integrations/wordpress
- **Intercom Alternative**: http://localhost:3001/compare/intercom-alternative

## 🎨 Making UI Changes

1. **Start the development server**: `./start-homepage.sh`
2. **Edit components** in `homepage/components/`
3. **Save files** - the browser auto-refreshes!

### Common Components to Edit:
- `Hero.tsx` - Main landing section
- `Features.tsx` - Feature showcase
- `Pricing.tsx` - Pricing tables
- `Navbar.tsx` - Navigation menu
- `Footer.tsx` - Footer section

## 🛠️ Port Configuration

- **Homepage**: Port 3001 (default)
- **Dashboard (App)**: Port 3000
- **Backend API**: Port 8000

This separation ensures:
- Dashboard runs on port 3000 → app.netvexa.com (production)
- Homepage runs on port 3001 → netvexa.com (production)

## 📝 What Changed

1. **Renamed folder**: `marketing-site` → `homepage`
2. **Updated scripts**: All references updated
3. **Package name**: Changed to `netvexa-homepage`
4. **Documentation**: Updated all references

## 💡 Development Tips

- Uses **Next.js 14** with App Router
- Styled with **Tailwind CSS**
- **TypeScript** for type safety
- **Hot reload** enabled
- SEO optimized with `next-seo`

## 🔧 Troubleshooting

### If the server won't start:
```bash
cd homepage
rm -rf node_modules package-lock.json
npm install
```

### To run on a different port:
```bash
cd homepage
PORT=3002 npm run dev
```

## 📦 Production Build

```bash
cd homepage
npm run build
npm start
```

This creates an optimized production build ready for deployment.