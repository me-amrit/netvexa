import { NextSeo } from 'next-seo'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'

export default function WordPressIntegration() {
  return (
    <>
      <NextSeo
        title="WordPress AI Chat Plugin - Deploy in Minutes"
        description="Add an AI-powered business agent to your WordPress site in under 60 minutes. No coding required. Qualify leads, answer questions, and grow revenue 24/7."
        canonical="https://netvexa.com/integrations/wordpress"
      />
      
      <div className="min-h-screen bg-white">
        <Navbar />
        
        <section className="pt-32 pb-20 bg-gradient-to-b from-blue-50 to-white">
          <div className="container-narrow">
            <div className="max-w-4xl mx-auto text-center">
              <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold mb-6">
                <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zM3.5 12c0-1.232.264-2.402.736-3.459L8.29 19.65A8.5 8.5 0 013.5 12zm5.586 8.162L4.838 9.454A8.433 8.433 0 0112 3.5c2.318 0 4.415.93 5.95 2.437l-.456.385a6.682 6.682 0 00-5.494-2.875 6.998 6.998 0 00-6.357 4.063l.561.48 4.792 13.001a8.503 8.503 0 01-1.91-.829zm1.672-.66l2.816-8.169c.53-1.318.703-2.37.703-3.306 0-.34-.023-.656-.058-.952a8.453 8.453 0 012.834 10.645l-2.839 7.723-3.456-5.941zm8.592-1.34A8.5 8.5 0 0020.5 12c0-.79-.108-1.555-.308-2.283-.015.102-.032.196-.054.279l-2.788 7.166z"/>
                </svg>
                WordPress Plugin
              </div>
              
              <h1 className="text-5xl md:text-6xl font-extrabold mb-6">
                AI Chat for WordPress in{' '}
                <span className="gradient-text">60 Minutes</span>
              </h1>
              
              <p className="text-xl text-gray-600 mb-8">
                Transform your WordPress site into a lead-generating machine. Our plugin brings 
                enterprise AI capabilities to WordPress without the complexity or cost.
              </p>
              
              <div className="flex gap-4 justify-center mb-12">
                <Link href="https://wordpress.org/plugins/netvexa-chat" className="btn-primary">
                  Install from WordPress.org
                </Link>
                <Link href="https://app.netvexa.com/signup" className="btn-secondary">
                  Get API Key
                </Link>
              </div>
              
              <div className="grid grid-cols-3 gap-8 text-center">
                <div>
                  <div className="text-3xl font-bold text-primary mb-1">50K+</div>
                  <div className="text-gray-600">Active Installs</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-primary mb-1">4.8/5</div>
                  <div className="text-gray-600">Average Rating</div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-primary mb-1">24/7</div>
                  <div className="text-gray-600">Lead Capture</div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-20">
          <div className="container-narrow">
            <h2 className="text-3xl font-bold text-center mb-12">
              Why 50,000+ WordPress Sites Choose NETVEXA
            </h2>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">Lightning Fast Setup</h3>
                <p className="text-gray-600">
                  Install, configure, and go live in under 60 minutes. No developers needed.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">Full Customization</h3>
                <p className="text-gray-600">
                  Match your brand with custom colors, position, and personality settings.
                </p>
              </div>
              
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold mb-2">Enterprise Security</h3>
                <p className="text-gray-600">
                  GDPR compliant with data processing in secure European data centers.
                </p>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-20 bg-gray-50">
          <div className="container-narrow">
            <h2 className="text-3xl font-bold text-center mb-12">
              How It Works
            </h2>
            
            <div className="max-w-3xl mx-auto">
              <div className="space-y-8">
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                    1
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Install the Plugin</h3>
                    <p className="text-gray-600">
                      Search for "NETVEXA Chat" in your WordPress admin or download from WordPress.org. 
                      Activate with one click.
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                    2
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Connect Your Agent</h3>
                    <p className="text-gray-600">
                      Sign up for a free NETVEXA account, create your AI agent, and connect it to 
                      WordPress with your API key.
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center font-bold">
                    3
                  </div>
                  <div>
                    <h3 className="text-xl font-bold mb-2">Start Converting</h3>
                    <p className="text-gray-600">
                      Your AI agent appears on your site, ready to engage visitors, qualify leads, 
                      and answer questions 24/7.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-20">
          <div className="container-narrow">
            <div className="bg-primary rounded-2xl p-12 text-center text-white">
              <h2 className="text-3xl font-bold mb-4">
                Ready to Transform Your WordPress Site?
              </h2>
              <p className="text-xl mb-8 opacity-90">
                Join 50,000+ WordPress sites using AI to capture more leads and grow revenue.
              </p>
              <div className="flex gap-4 justify-center">
                <Link href="https://wordpress.org/plugins/netvexa-chat" className="bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                  Download Plugin
                </Link>
                <Link href="/demo" className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary transition-colors">
                  See Demo
                </Link>
              </div>
            </div>
          </div>
        </section>
        
        <Footer />
      </div>
    </>
  )
}