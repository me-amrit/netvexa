import Link from 'next/link'

export default function CTA() {
  return (
    <section className="py-20 bg-gradient-to-r from-primary to-secondary">
      <div className="container-narrow text-center text-white">
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Stop Losing Leads to "Office Hours"
        </h2>
        <p className="text-xl mb-8 opacity-90 max-w-2xl mx-auto">
          Join 5,000+ businesses using AI agents to capture more leads, 
          qualify prospects, and grow revenue 24/7.
        </p>
        <div className="flex gap-4 justify-center mb-6">
          <Link href="https://app.netvexa.com/signup" className="bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
            Start Free Trial
          </Link>
          <Link href="/demo" className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary transition-colors">
            See Live Demo
          </Link>
        </div>
        <p className="text-sm opacity-75">
          No credit card required · Deploy in 60 minutes · Cancel anytime
        </p>
      </div>
    </section>
  )
}