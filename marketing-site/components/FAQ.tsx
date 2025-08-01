import { useState } from 'react'

export default function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0)
  
  const faqs = [
    {
      question: "How quickly can I get my AI agent live?",
      answer: "Most customers are live within 60 minutes. Simply sign up, let our AI learn from your website, customize the appearance, and copy the embed code. No technical skills or developers required."
    },
    {
      question: "How does the AI learn about my business?",
      answer: "Our RAG (Retrieval-Augmented Generation) technology automatically crawls your website and extracts information about your products, services, pricing, and policies. You can also upload documents or manually add specific knowledge. The AI continuously improves based on real conversations."
    },
    {
      question: "What makes NETVEXA different from chatbots?",
      answer: "Traditional chatbots follow scripted flows and often frustrate users. NETVEXA uses advanced AI to understand context, provide accurate answers from your knowledge base, and have natural conversations. It's like having your best salesperson available 24/7."
    },
    {
      question: "Is my data secure and GDPR compliant?",
      answer: "Absolutely. We process all data in secure European data centers, encrypt everything in transit and at rest, and never use your data to train models for other customers. We're fully GDPR compliant with clear data processing agreements."
    },
    {
      question: "Can I customize the AI agent's personality?",
      answer: "Yes! You can adjust the tone (professional, friendly, casual), set specific goals (lead qualification, support, sales), and even provide custom instructions. The agent adapts to match your brand voice perfectly."
    },
    {
      question: "What happens if the AI doesn't know an answer?",
      answer: "The AI is trained to gracefully handle unknown questions by either asking clarifying questions, offering to connect the visitor with a human team member, or capturing their contact information for follow-up. It never makes up information."
    }
  ]
  
  return (
    <section className="py-20">
      <div className="container-narrow">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Frequently Asked Questions
          </h2>
          <p className="text-xl text-gray-600">
            Everything you need to know about deploying AI agents on your website
          </p>
        </div>
        
        <div className="max-w-3xl mx-auto">
          {faqs.map((faq, index) => (
            <div key={index} className="mb-4">
              <button
                className="w-full text-left p-6 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow"
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold pr-8">{faq.question}</h3>
                  <svg
                    className={`w-5 h-5 text-gray-500 transform transition-transform ${
                      openIndex === index ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
                {openIndex === index && (
                  <p className="mt-4 text-gray-600">{faq.answer}</p>
                )}
              </button>
            </div>
          ))}
        </div>
        
        <div className="text-center mt-12">
          <p className="text-gray-600 mb-4">
            Still have questions? We're here to help.
          </p>
          <a href="mailto:support@netvexa.com" className="text-primary font-semibold hover:underline">
            Contact Support →
          </a>
        </div>
      </div>
    </section>
  )
}