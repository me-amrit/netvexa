import Link from 'next/link'
import { useState } from 'react'

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm z-50 border-b border-gray-100">
      <div className="container-narrow">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex items-center">
            <span className="text-2xl font-bold gradient-text">NETVEXA</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <Link href="/features" className="text-gray-600 hover:text-primary transition-colors">
              Features
            </Link>
            <Link href="/pricing" className="text-gray-600 hover:text-primary transition-colors">
              Pricing
            </Link>
            <Link href="/integrations" className="text-gray-600 hover:text-primary transition-colors">
              Integrations
            </Link>
            <Link href="/blog" className="text-gray-600 hover:text-primary transition-colors">
              Blog
            </Link>
            <Link href="https://app.netvexa.com" className="btn-primary text-sm">
              Get Started
            </Link>
          </div>
          
          <button 
            className="md:hidden p-2"
            onClick={() => setIsOpen(!isOpen)}
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
            </svg>
          </button>
        </div>
      </div>
      
      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden bg-white border-t border-gray-100">
          <div className="container-narrow py-4 space-y-3">
            <Link href="/features" className="block text-gray-600 hover:text-primary">Features</Link>
            <Link href="/pricing" className="block text-gray-600 hover:text-primary">Pricing</Link>
            <Link href="/integrations" className="block text-gray-600 hover:text-primary">Integrations</Link>
            <Link href="/blog" className="block text-gray-600 hover:text-primary">Blog</Link>
            <Link href="https://app.netvexa.com" className="btn-primary inline-block text-sm">Get Started</Link>
          </div>
        </div>
      )}
    </nav>
  )
}