import { NextSeo } from 'next-seo'
import Link from 'next/link'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'

export default function IntercomAlternative() {
  return (
    <>
      <NextSeo
        title="Intercom Alternative - 70% Lower Cost, Same Results"
        description="NETVEXA vs Intercom: Get enterprise AI chat capabilities at SME prices. No per-seat pricing, faster setup, and GDPR compliant. See why 5,000+ businesses switched."
        canonical="https://netvexa.com/compare/intercom-alternative"
      />
      
      <div className="min-h-screen bg-white">
        <Navbar />
        
        <section className="pt-32 pb-20">
          <div className="container-narrow">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-extrabold mb-6">
                The Intercom Alternative Built for{' '}
                <span className="gradient-text">Growing SMEs</span>
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Get the same powerful customer engagement capabilities at 70% lower cost. 
                No complex setup, no per-seat pricing, just results.
              </p>
            </div>
            
            <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
              <div className="grid md:grid-cols-3">
                <div className="p-8 md:col-span-1 bg-gray-50">
                  <h3 className="text-xl font-bold mb-6">Feature Comparison</h3>
                </div>
                <div className="p-8 text-center border-l border-gray-200">
                  <div className="text-2xl font-bold gradient-text mb-2">NETVEXA</div>
                  <div className="text-gray-600">SME-Focused Solution</div>
                </div>
                <div className="p-8 text-center border-l border-gray-200">
                  <div className="text-2xl font-bold text-gray-700 mb-2">Intercom</div>
                  <div className="text-gray-600">Enterprise Platform</div>
                </div>
              </div>
              
              <div className="divide-y divide-gray-200">
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">Starting Price</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-2xl font-bold text-green-600">€99</span>/month
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-2xl font-bold text-gray-700">$500+</span>/month
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">Setup Time</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-green-600 font-semibold">60 minutes</span>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-gray-700">2-4 weeks</span>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">AI-Powered Responses</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-gray-500">Add-on pricing</span>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">Lead Qualification</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">GDPR Compliant</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">WordPress Plugin</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-green-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <svg className="w-6 h-6 text-red-500 mx-auto" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3">
                  <div className="p-6 bg-gray-50 font-semibold">Contract Required</div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-green-600 font-semibold">No, cancel anytime</span>
                  </div>
                  <div className="p-6 text-center border-l border-gray-200">
                    <span className="text-gray-700">12-month minimum</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-20 bg-gray-50">
          <div className="container-narrow">
            <h2 className="text-3xl font-bold text-center mb-12">
              Why SMEs Choose NETVEXA Over Intercom
            </h2>
            
            <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
              <div>
                <h3 className="text-2xl font-bold mb-4">Built for Your Budget</h3>
                <p className="text-gray-600 mb-6">
                  Intercom's pricing model punishes growth. As you add team members and conversations 
                  increase, costs skyrocket. NETVEXA offers predictable, usage-based pricing that 
                  scales with your success, not your headcount.
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>No per-seat pricing - add unlimited team members</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Pay only for conversations, not features</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Free trial with no credit card required</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold mb-4">Faster Time to Value</h3>
                <p className="text-gray-600 mb-6">
                  While Intercom requires weeks of onboarding, custom development, and training, 
                  NETVEXA gets you live in 60 minutes. Our AI learns from your existing content 
                  automatically - no manual setup required.
                </p>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Self-service setup - no implementation team needed</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>AI learns from your website automatically</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-green-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span>Start capturing leads on day one</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-20">
          <div className="container-narrow">
            <h2 className="text-3xl font-bold text-center mb-12">
              Real Stories from Businesses Who Switched
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
              <div className="bg-white rounded-lg p-8 shadow-lg">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-700 mb-4">
                  "We were paying Intercom €1,200/month for features we didn't use. NETVEXA gives 
                  us better AI responses at €299/month. The switch was a no-brainer."
                </p>
                <div>
                  <div className="font-semibold">Michael Schmidt</div>
                  <div className="text-gray-600 text-sm">CEO, TechConsult GmbH</div>
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-8 shadow-lg">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <svg key={i} className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-700 mb-4">
                  "Intercom's onboarding took 3 weeks and required developer resources. With NETVEXA, 
                  we were live in an hour and capturing leads immediately."
                </p>
                <div>
                  <div className="font-semibold">Emma Thompson</div>
                  <div className="text-gray-600 text-sm">Marketing Director, CloudFirst</div>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        <section className="py-20 bg-primary text-white">
          <div className="container-narrow text-center">
            <h2 className="text-3xl font-bold mb-4">
              Ready to Cut Your Chat Costs by 70%?
            </h2>
            <p className="text-xl mb-8 opacity-90">
              Join 5,000+ businesses that switched from Intercom to NETVEXA
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="https://app.netvexa.com/signup" className="bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Start Free Trial
              </Link>
              <Link href="/migration/intercom" className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary transition-colors">
                Migration Guide
              </Link>
            </div>
          </div>
        </section>
        
        <Footer />
      </div>
    </>
  )
}