import { NextSeo } from 'next-seo'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import Features from '@/components/Features'
import HowItWorks from '@/components/HowItWorks'
import Pricing from '@/components/Pricing'
import FAQ from '@/components/FAQ'
import CTA from '@/components/CTA'
import Footer from '@/components/Footer'

export default function Home() {
  return (
    <>
      <NextSeo
        title="AI Business Agent Platform - Deploy in 60 Minutes"
        description="Transform your website into a 24/7 sales machine. NETVEXA's AI agents qualify leads, answer questions, and convert visitors automatically. Start free today."
        canonical="https://netvexa.com"
      />
      
      <div className="min-h-screen bg-white">
        <Navbar />
        <Hero />
        <Features />
        <HowItWorks />
        <Pricing />
        <FAQ />
        <CTA />
        <Footer />
      </div>
    </>
  )
}