export default function Pricing() {
  const plans = [
    {
      name: "Starter",
      price: "€79",
      period: "per month",
      description: "Perfect for small businesses getting started",
      features: [
        "1 AI Agent",
        "2,000 messages/month",
        "Basic analytics",
        "Email support",
        "WordPress plugin"
      ],
      cta: "Start Free Trial",
      popular: false
    },
    {
      name: "Growth",
      price: "€199",
      period: "per month",
      description: "For businesses ready to scale",
      features: [
        "2 AI Agents",
        "8,000 messages/month",
        "Advanced analytics",
        "Priority email support",
        "Custom branding",
        "API access"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Professional",
      price: "€499",
      period: "per month",
      description: "For teams with advanced needs",
      features: [
        "5 AI Agents",
        "25,000 messages/month",
        "Advanced analytics",
        "Priority support",
        "A/B testing",
        "Team collaboration (3 seats)"
      ],
      cta: "Start Free Trial",
      popular: false
    },
    {
      name: "Business",
      price: "€999",
      period: "per month",
      description: "For larger organizations",
      features: [
        "15 AI Agents",
        "60,000 messages/month",
        "Advanced analytics & reporting",
        "24/7 priority support",
        "Custom integrations",
        "Team collaboration (10 seats)",
        "SLA guarantee"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ]

  return (
    <section className="py-20 bg-gray-50">
      <div className="container-narrow">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-xl text-gray-600">
            No hidden fees. No per-seat charges. Just pay for conversations.
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`relative bg-white rounded-2xl shadow-lg p-6 ${
                plan.popular ? 'ring-2 ring-primary transform scale-105' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-primary text-white px-4 py-1 rounded-full text-sm font-semibold">
                    Most Popular
                  </span>
                </div>
              )}
              
              <div className="text-center mb-6">
                <h3 className="text-xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-2">
                  <span className="text-3xl font-bold">{plan.price}</span>
                  <span className="text-gray-600 text-sm ml-1">{plan.period}</span>
                </div>
                <p className="text-sm text-gray-600">{plan.description}</p>
              </div>
              
              <ul className="space-y-3 mb-8">
                {plan.features.map((feature, featureIndex) => (
                  <li key={featureIndex} className="flex items-start gap-2">
                    <svg className="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
              
              <button className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-colors ${
                plan.popular
                  ? 'bg-primary text-white hover:bg-secondary'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}>
                {plan.cta}
              </button>
            </div>
          ))}
        </div>
        
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            All plans include: SSL encryption, GDPR compliance, 99.9% uptime SLA
          </p>
          <p className="text-sm text-gray-500">
            Prices in EUR. VAT may apply. Cancel anytime.
          </p>
        </div>
      </div>
    </section>
  )
}