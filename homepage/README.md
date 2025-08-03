# NETVEXA Home Page

This is the public-facing home page for NETVEXA, built with Next.js and Tailwind CSS.

## 🚀 Quick Start

From the root directory:
```bash
./start-homepage.sh
```

Or from this directory:
```bash
./start-homepage.sh
```

The home page will be available at: **http://localhost:3001**

> Note: Port 3001 is used to avoid conflict with the dashboard app on port 3000

## 📁 Structure

```
homepage/
├── components/         # Reusable React components
│   ├── Hero.tsx       # Main hero section
│   ├── Features.tsx   # Features showcase
│   ├── Pricing.tsx    # Pricing tables
│   ├── FAQ.tsx        # Frequently asked questions
│   └── ...
├── pages/             # Next.js pages (routes)
│   ├── index.tsx      # Home page
│   ├── blog/          # Blog section
│   └── integrations/  # Integration pages
├── content/           # Markdown content for blog
├── styles/            # Global CSS styles
└── public/            # Static assets
```

## 🎨 Making UI Changes

### 1. **Editing Components**

To modify a section of the home page, edit the corresponding component:

- **Hero Section**: `components/Hero.tsx`
- **Features**: `components/Features.tsx`
- **Pricing**: `components/Pricing.tsx`
- **Navigation**: `components/Navbar.tsx`

### 2. **Styling with Tailwind**

This project uses Tailwind CSS. Common classes:

```tsx
// Spacing
className="p-4"     // padding
className="m-4"     // margin
className="mt-8"    // margin-top

// Colors
className="bg-blue-500"      // background
className="text-gray-800"    // text color
className="border-green-400" // border color

// Layout
className="flex items-center justify-between"
className="grid grid-cols-3 gap-4"
```

### 3. **Testing Changes**

1. Start the development server: `./start-homepage.sh`
2. Edit any file
3. Save the file
4. The browser will automatically refresh!

## 🌐 Available Pages

- **Home**: http://localhost:3001
- **Blog**: http://localhost:3001/blog
- **WordPress Integration**: http://localhost:3001/integrations/wordpress
- **Intercom Alternative**: http://localhost:3001/compare/intercom-alternative

## 📝 Common UI Tasks

### Change Hero Text
Edit `components/Hero.tsx`:
```tsx
<h1 className="text-5xl font-bold">
  Your New Headline Here
</h1>
```

### Update Pricing
Edit `components/Pricing.tsx` to modify plans and prices.

### Add a New Page
Create a new file in `pages/` directory:
```tsx
// pages/about.tsx
export default function About() {
  return <div>About Us</div>
}
```

### Modify Colors
The main colors are defined using Tailwind classes:
- Primary: `blue-600`
- Secondary: `green-500`
- Text: `gray-800`

## 🛠️ Development Tips

1. **Hot Reload**: All changes auto-refresh in the browser
2. **TypeScript**: The project uses TypeScript for type safety
3. **SEO**: Each page can have custom SEO tags using `next-seo`
4. **Responsive**: Use Tailwind's responsive prefixes (sm:, md:, lg:)

## 🚨 Troubleshooting

### Port 3001 in use
The startup script will ask if you want to:
1. Kill the existing process
2. Use a different port (3002)
3. Cancel

### Dependencies not installing
```bash
rm -rf node_modules package-lock.json
npm install
```

### Changes not reflecting
1. Check the browser console for errors
2. Try hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
3. Restart the development server

## 📦 Build for Production

```bash
npm run build
npm start
```

This creates an optimized production build.